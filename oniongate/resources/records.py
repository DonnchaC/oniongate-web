"""
Record resource presented on the API interface
"""
from collections import OrderedDict

from flask import g, current_app
from flask_restful import fields, marshal_with, reqparse, Resource, abort
from sqlalchemy import exc

from .. import validators
from ..utils import auth_domain, domain_exists
from ..models import Record


new_record_parser = reqparse.RequestParser()
new_record_parser.add_argument('label', type=validators.label, required=True)
new_record_parser.add_argument('ttl')
new_record_parser.add_argument('type', type=validators.allowed_dns_record_type, required=True)
new_record_parser.add_argument('value', required=True)

record_fields = OrderedDict([
    ('id', fields.Integer),
    ('label', fields.String),
    ('ttl', fields.Integer),
    ('type', fields.String(attribute="record_type")),
    ('value', fields.String),
    ('date_created', fields.DateTime('iso8601')),
    ('updated_since_synced', fields.Boolean),
])


def is_onion_record(record_value):
    """
    Check if this record looks like an onion address mapping
    """
    key, value = record_value.lower().split("=", 1)
    if key and value:
        return key == "onion" and validators.is_onion_address(value)
    return None


class Records(Resource):
    method_decorators = [domain_exists]

    @marshal_with(record_fields)
    def get(self, domain_name, record_id=None):
        """
        Return a listing of all records for this domain
        """
        if record_id:
            return Record.get_or_404(domain=g.domain, record_id=record_id)
        return Record.query.filter_by(domain=g.domain).all()

    @marshal_with(record_fields)
    @auth_domain
    def post(self, domain_name):
        """
        Create a new DNS record on this domain

        The request must be validated with the domain token.
        """
        probable_onion_mapping = None
        args = new_record_parser.parse_args()
        num_records = Record.query.filter_by(domain=g.domain).count()

        if num_records >= current_app.config["MAX_RECORDS"]:
            return abort(403, message="This domain has had reach the DNS record limit. You cannot "
                         "add more without removing some existing records")

        # Record address on domain if this looks like an onion mapping
        if is_onion_record(args.value) and args.type == "TXT":
            probable_onion_mapping = args.value.split("=")[1]

        try:
            record = Record.create(domain=g.domain,
                                   label=args.label,
                                   ttl=args.ttl or current_app.config["TXT_RECORD_TTL"],
                                   record_type=args.type,
                                   value=args.value,
                                   is_onion_mapping=probable_onion_mapping)
        except exc.IntegrityError:
            return abort(422, message="An unknown error occurred when trying to create "
                         "this record")

        # Guess that the user is updating their onion address if its a valid
        # onion=theonionaddress.onion type TXT record
        if probable_onion_mapping:
            # Update the convenience onion_address wrapper on the domain
            g.domain.update(onion_address=probable_onion_mapping)

        return record

    @auth_domain
    def delete(self, domain_name, record_id):
        """
        Allow updates to the domain -> onion address mapping
        """
        record = Record.get_or_404(domain=g.domain, record_id=record_id)

        # Remove the onion address from domain we are removing the last DNS record
        # containing the current onion address.
        if record.is_onion_mapping and (record.is_onion_mapping == g.domain.onion_address):
            # Check if any other TXT records also match this onion address
            if Record.query.filter_by(domain=g.domain,
                                      record_type="TXT",
                                      value=record.value).count() == 1:
                # Last mapping with this onion address, remove onion address from the domain
                g.domain.update(onion_address=None)

        record.delete()
        return {"message": "Record has been deleted"}
