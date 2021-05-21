import pytest

from mongoengine import connect
from photographer import MongoPhotographer


from starlette.testclient import TestClient

@pytest.fixture
def clearPhotographers():
    MongoPhotographer.objects.all().delete()

@pytest.fixture(scope="class")
def initDB():
    connect("photographers_test", host="mongo-service-test")
    yield
