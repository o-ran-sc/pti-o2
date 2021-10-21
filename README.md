## Building containers


```sh
docker-compose build
```


## Creating a local virtualenv (optional)

```sh
python3.8 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e src/
```

## Running the tests

```sh
docker-compose up -d
docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Tear down containers

```sh
docker-compose down --remove-orphans
```
