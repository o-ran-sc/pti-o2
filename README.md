## Building containers


```sh
docker-compose build
```

## Running the tests


```sh
source ./admin_openrc.sh
export |grep OS_AUTH_URL
export |grep OS_USERNAME
export |grep OS_PASSWORD
docker-compose up -d
docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration
```

## Running the tests with a O-Cloud

Prerequisite: in case of testing against real ocloud, download openrc file from ocloud dashboard, e.g. 

```sh
admin_openrc.sh
docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration-ocloud

docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration-ocloud --log-level=DEBUG --log-file=/test
s/debug.log
```

## Tear down containers

```sh
docker-compose down --remove-orphans
```

## Test with local virtualenv

```sh
python3.8 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt
pip install -r requirements-test.txt
pip install -e o2ims
# pip install -e o2dms -e o2common
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```
