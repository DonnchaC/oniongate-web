import pytest

from oniongate import create_app
from oniongate.models import db, User


@pytest.fixture
def client(request):
    app = create_app('appname.settings.TestConfig')
    client = app.test_client()

    db.app = app
    db.create_all()

    def teardown():
        db.session.remove()
        db.drop_all()

    request.addfinalizer(teardown)
    return client
