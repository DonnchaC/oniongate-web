import datetime

from flask import current_app
from sqlalchemy.orm import exc
from sqlalchemy.ext.hybrid import hybrid_property
from flask_restful import abort

from .. import utils
from . import db, mixins


class Domain(db.Model, mixins.CRUDMixin):
    """
    A mapping of a domain name to an onion service address
    """
    __tablename__ = 'domains'

    domain_name = db.Column(db.String(256), unique=True, index=True)
    zone = db.Column(db.String(256), nullable=False, index=True)
    onion_address = db.Column(db.String(80))

    # Should this domain be publically listed in the onion service index.
    public = db.Column(db.Boolean, default=True)

    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_since_synced = db.Column(db.Boolean, default=True)

    service_last_online = db.Column(db.DateTime)

    # We default to True so that the service is assumed up until we can
    # scan it and determine that it it down. We want users to be able
    # to access services ASAP, before we have time to scan them.
    service_online = db.Column(db.Boolean, default=True)

    # Indicate domain is flagged for deletion before it is removed from DNS
    deleted = db.Column(db.Boolean, default=False)

    records = db.relationship("Record", back_populates="domain", cascade="all, delete-orphan")

    def __repr__(self):
        return '<Domain %r>' % self.domain_name

    def __str__(self):
        return self.domain_name

    @hybrid_property
    def subdomain(self):
        """
        Return the subdomain label without the zone name
        """
        return self.domain_name.split(self.zone)[0].strip(".")

    @hybrid_property
    def txt_label(self):
        """
        Return the domain where the TXT record should be placed
        """
        if not current_app.config.get("USE_ALIAS_RECORDS"):
            return "_onion.{}".format(self.subdomain)
        return self.subdomain

    @hybrid_property
    def token(self):
        """
        Generate a JWT for authenticate future requests to edit this domain
        """
        return utils.create_jwt({'domain': self.domain_name}).decode('utf-8')

    def get_or_404(domain_name):
        """
        Helper method to retrieve a domain object or raise a 404 error
        """
        try:
            return Domain.query.filter_by(domain_name=domain_name.lower(),
                                          deleted=False).one()
        except exc.NoResultFound:
            abort(404, message='Domain {} does not exist'.format(domain_name))

