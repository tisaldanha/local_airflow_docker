# local_airflow_docker

Repo to bootstrap local Airflow development using docker compose. This document is a simplification of https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

## Running                      

Now, to build the image for your local environment:

```bash
docker-compose build
```

And to run all containers:

```bash
docker-compose up
```

The airflow webserver will be available on localhost:8080 and username and password will be `airflow`
