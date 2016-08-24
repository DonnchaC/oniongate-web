from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .domain import Domain
from .record import Record
from .proxy import Proxy
