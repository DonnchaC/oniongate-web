import os

from flask import Flask, Blueprint
from flask_restful import Api
from flask_cors import CORS

from .models import db
from .resources import Domains, Proxies
from .main import main_bp


def create_app(object_name):
    """
    An flask application factory

    object_name: the python path of the config object,
                 e.g. oniongate.settings.ProdConfig
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(object_name)
    app.config.from_pyfile("config.py")

    # Create zone file directory if it doesn't exist
    zone_directory = app.config.get('zone_dir') or os.path.join(app.instance_path, 'zones')
    if not os.path.isdir(zone_directory):
        os.makedirs(zone_directory, 644)
    app.config["zone_dir"] = zone_directory

    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    # register our blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    api.add_resource(Domains, '/domains', '/domains/<domain_name>')
    api.add_resource(Proxies, '/proxies', '/proxies/<ip_address>')

    return app
