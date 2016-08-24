import datetime

from sqlalchemy.orm import exc
from flask_restful import abort

from . import db, mixins


class Record(db.Model, mixins.CRUDMixin):
    """
    A DNS record for a domain
    """
    __tablename__ = 'records'

    label = db.Column(db.String(255), nullable=False)
    ttl = db.Column(db.Integer)
    record_type = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Text(65000), nullable=False)

    is_onion_mapping = db.Column(db.String(80), default=False)

    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    domain = db.relationship("Domain", back_populates="records")

    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_since_synced = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return ('<Record label=%r type=%r value=%r>' %
                (self.label, self.type, self.value))

    def get_or_404(domain, record_id):
        """
        Helper method to retrieve a record object or raise a 404 error
        """
        try:
            return Record.query.filter_by(domain=domain, id=record_id).one()
        except exc.NoResultFound:
            abort(404, message="Record does not exist")

