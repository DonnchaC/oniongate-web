import datetime

from flask_restful import abort
from sqlalchemy.orm import exc

from . import db, mixins

class Proxy(db.Model, mixins.CRUDMixin):
    __tablename__ = 'proxies'

    ip_address = db.Column(db.String(100), unique=True, nullable=False)
    ip_type =  db.Column(db.Enum('4', '6'), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Track when this proxy was last checked and confirmed to be working
    last_succesful_check = db.Column(db.DateTime)
    last_checked = db.Column(db.DateTime)
    online = db.Column(db.Boolean, default=False)

    updated_since_synced = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Proxy %r>' % self.ip_address

    def get_or_404(ip_address):
        """
        Helper method to retrieve a proxy object or raise a 404 error
        """
        try:
            return Proxy.query.filter_by(ip_address=ip_address).one()
        except exc.NoResultFound:
            abort(404, message='Proxy {} does not exist'.format(ip_address))
