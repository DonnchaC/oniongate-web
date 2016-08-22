#!/usr/bin/env python
import os

from flask_script import Manager
from flask_script.commands import ShowUrls, Clean

from oniongate import create_app
from oniongate.models import *

# default to dev config
env = os.environ.get('ONIONGATE_ENV', 'dev')
app = create_app('oniongate.settings.%sConfig' % env.capitalize())

manager = Manager(app)
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """
    Creates a python REPL with several default imports
    in the context of the app
    """
    return dict(app=app, db=db,
                Domain=Domain, Proxy=Proxy)


@manager.command
def createdb():
    """
    Creates a database with all of the tables defined in
    your SQLAlchemy models.
    """
    db.create_all()


if __name__ == "__main__":
    manager.run()
