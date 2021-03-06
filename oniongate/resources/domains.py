"""
Domain resource presented on the API interface
"""
import datetime
from collections import OrderedDict

from flask_restful import fields, inputs, marshal_with, marshal, reqparse, Resource, abort
from sqlalchemy import exc

from .. import validators
from ..utils import auth_domain
from ..models import Domain
from .records import record_fields


new_domain_parser = reqparse.RequestParser()
new_domain_parser.add_argument(
    'domain_name', type=validators.domain_name, required=True, location='json',
)
new_domain_parser.add_argument(
    'public', type=inputs.boolean, default=True,
)

update_domain_parser = new_domain_parser.copy()
update_domain_parser.remove_argument('domain_name')

domain_fields = OrderedDict([
    ('domain_name', fields.String),
    ('zone', fields.String),
    ('onion_address', fields.String),
    ('date_created', fields.DateTime('iso8601')),
    ('date_updated', fields.DateTime('iso8601')),
    ('updated_since_synced', fields.Boolean),
    ('service_last_online', fields.DateTime('iso8601')),
    ('service_online', fields.Boolean)
])

# Include DNS records when requesting an individual domain
domain_fields_with_records = domain_fields.copy()
domain_fields_with_records['records'] = fields.Nested(record_fields)

# Return a serialisation with a JWT (JSON Web Token) for authenticating
# future updates to this domain
domain_fields_with_token = domain_fields.copy()
domain_fields_with_token['update_token'] = fields.String(attribute='token')


class Domains(Resource):
    def get(self, domain_name=None):
        """
        Return a listing of all public domains resolved by this resolver
        """
        if domain_name:
            # Include DNS records when an individual domain is requested
            return marshal(Domain.get_or_404(domain_name), domain_fields_with_records), 200

        all_domains = Domain.query.filter_by(public=True, deleted=False).all()
        return marshal(all_domains, domain_fields), 200

    @marshal_with(domain_fields_with_token)
    def post(self):
        """
        Register a new domain name on this resolver.

        Returns a serialization which includes a JSON Web Token which can be used to authorize
        updates to this domain mapping in future.
        """
        args = new_domain_parser.parse_args()
        domain_name = "{}.{}".format(args.domain_name["label"], args.domain_name["zone"])
        try:
            domain = Domain.create(domain_name=domain_name,
                                   zone=args.domain_name["zone"],
                                   public=args.public)
        except exc.IntegrityError:
            return abort(422,
                         message={'domain_name': "Domain {} already exists".format(domain_name)})

        return domain

    @auth_domain
    def delete(self, domain_name):
        """
        Allow the registered domain name to be deleted
        """
        domain = Domain.get_or_404(domain_name)
        domain.update(deleted=True,
                      date_updated=datetime.datetime.utcnow())
        return {"message": "Domain {} was deleted from our service".format(domain.domain_name)}
