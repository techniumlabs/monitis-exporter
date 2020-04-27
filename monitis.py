import httpx
import json
import time
from dynaconf import settings, LazySettings
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF='MONITIS')

class Monitis():
    def __init__(self, apikey, secretkey):
        self.apikey = apikey
        self.secretkey = secretkey

    def token(self):
        params = {
            'action': 'authToken',
            'apikey': self.apikey,
            'secretkey': self.secretkey,
            'output': 'json'
        }
        r = httpx.get('https://api.monitis.com/api', params=params)
        output = json.loads(r.content)
        return output['authToken']

    def tests(self, test_type='https'):
        params = {
            'apikey': self.apikey,
            'output': 'json',
            'version': 3,
            'action': 'tests',
            'validation': 'token',
            'authToken': self.token()
        }
        list_output = httpx.get('https://api.monitis.com/api', params=params)
        output = json.loads(list_output.content)
        return [elem['name'] for elem in output['testList'] if elem['type'] == test_type]

    def last_test_result(self):
        params = {
            'apikey': self.apikey,
            'output': 'json',
            'version': 3,
            'action': 'testsLastValues',
            'validation': 'token',
            'authToken': self.token(),
        }
        last_result_output = httpx.get('https://api.monitis.com/api', params=params)
        output = json.loads(last_result_output.content)
        return output


class MonitisCollector():
    def __init__(self, monitis):
        self.monitis = monitis

    def collect(self):
        result = self.monitis.last_test_result()
        labels = ['name', 'location', 'testType', 'status']
        gauge = GaugeMetricFamily("monitis_https", "HTTP/S Response Time", value=None, labels=labels)
        for location in result:
            for site in location['data']:
                if site['testType'] == 'https':
                    labelvalues = [site['name'], location['name'], 'https', site['status']]
                    gauge.add_metric(labelvalues, site['perf'])
        yield gauge

        labels = ['name', 'location', 'status']
        gauge = GaugeMetricFamily("monitis_certificate", "Certificate Expiry time", value=None, labels=labels)
        for location in result:
            for site in location['data']:
                if site['testType'] == 'certificate':
                    labelvalues = [site['name'], location['name'], site['status']]
                    gauge.add_metric(labelvalues, site['perf'])
        yield gauge
def setup():
    m = Monitis(settings.APIKEY, settings.SECRETKEY)
    REGISTRY.register(MonitisCollector(m))
    start_http_server(8000)

if __name__ == '__main__':
    setup()
    while True:
        time.sleep(1)
