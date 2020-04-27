# Monitis Exporter
This is a prometheus exporter for Monitis. Currently it exposes `https` and `certificate` test types. 

### Run
To run use the following

```
docker run -e MONITIS_APIKEY=xxxx -e MONITIS_SECRETKEY=yyyy -p 8000:8000 -it techniumlabs/monitis-exporter-0.0.1
```

### Reference
1. ![Monitis](https://www.monitis.com/)
2. ![Prometheus Python Client API](https://github.com/prometheus/client_python)
3. ![Dynaconf](https://dynaconf.readthedocs.io/en/latest/index.html)
