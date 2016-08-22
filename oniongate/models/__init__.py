from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .domain import Domain
from .proxy import Proxy
