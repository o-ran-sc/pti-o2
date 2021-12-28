# pylint: disable=redefined-outer-name
import shutil
import subprocess
import time
from pathlib import Path

import pytest
import redis
import requests
from flask import Flask
from flask_restx import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay
from unittest.mock import MagicMock

from o2common.config import config

from o2ims.adapter.orm import metadata, start_o2ims_mappers
# from o2ims.adapter.clients.orm_stx import start_o2ims_stx_mappers

from o2app.adapter import unit_of_work
from o2ims.views import configure_namespace

from o2app.bootstrap import bootstrap


@pytest.fixture
def mock_uow():
    session = MagicMock()
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session)
    return session, uow


@pytest.fixture
def mock_flask_uow(mock_uow):
    session, uow = mock_uow
    app = Flask(__name__)
    app.config["TESTING"] = True
    api = Api(app)
    bootstrap(False, uow)
    configure_namespace(api)
    return session, app


@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    # engine = create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(in_memory_sqlite_db):
    yield sessionmaker(bind=in_memory_sqlite_db)


@pytest.fixture
def sqlite_uow(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(
        session_factory=sqlite_session_factory)
    # with uow:
    #     start_o2ims_mappers(uow.session.get_bind())
    #     uow.commit()
    yield uow
    # clear_mappers()
    with uow:
        engine = uow.session.get_bind()
        metadata.drop_all(engine)


@pytest.fixture
def sqlite_flask_uow(sqlite_uow):
    app = Flask(__name__)
    app.config["TESTING"] = True
    api = Api(app)
    bootstrap(False, sqlite_uow)
    configure_namespace(api)
    yield sqlite_uow, app


@pytest.fixture
def mappers():
    start_o2ims_mappers()
    # start_o2ims_stx_mappers()
    yield
    clear_mappers()


@retry(stop=stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())
    return r.ping()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri(),
                           isolation_level="SERIALIZABLE")
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    yield sessionmaker(bind=postgres_db)


@pytest.fixture
def postgres_session(postgres_session_factory):
    return postgres_session_factory()


@pytest.fixture
def postgres_uow(postgres_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(
        session_factory=postgres_session_factory)
    yield uow


@pytest.fixture
def postgres_flask_uow(postgres_uow):
    app = Flask(__name__)
    app.config["TESTING"] = True
    api = Api(app)
    bootstrap(False, postgres_uow)
    configure_namespace(api)
    yield postgres_uow, app


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/o2ims/entrypoints/flask_application.py")\
        .touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which("docker-compose"):
        print("skipping restart, assumes running in container")
        return
    subprocess.run(
        ["docker-compose", "restart", "-t", "0", "redis_pubsub"],
        check=True,
    )
