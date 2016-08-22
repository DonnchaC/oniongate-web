from collections import OrderedDict

from flask import current_app
from flask_restful import fields, inputs, marshal_with, reqparse, Resource, abort
from sqlalchemy import exc

from .. import validators
from ..models import Proxy


new_proxy_parser = reqparse.RequestParser()
new_proxy_parser.add_argument(
    'ip_address', type=validators.ip_address, required=True, location='json',
)


proxy_fields = OrderedDict([
    ('ip_address', fields.String),
    ('ip_type', fields.Integer),
    ('date_created', fields.DateTime('iso8601')),
    ('last_checked', fields.DateTime('iso8601')),
    ('last_succesful_check', fields.DateTime('iso8601')),
    ('updated_since_synced', fields.Boolean),
    ('online', fields.Boolean)
])


class Proxies(Resource):
    @marshal_with(proxy_fields)
    def get(self, ip_address=None):
        """
        View listing of all available proxies
        """
        if ip_address:
            return Proxy.get_or_404(ip_address)

        # Display online proxies first, then order by creation date
        return Proxy.query.order_by(Proxy.online.desc(), Proxy.date_created).all()

    @marshal_with(proxy_fields)
    def post(self):
        """
        Add a new proxy to the proxy list
        """
        args = new_proxy_parser.parse_args()
        ip_address = args.ip_address

        try:
            proxy = Proxy.create(ip_address=str(ip_address),
                                 ip_type=ip_address.version)
        except exc.IntegrityError:
            return abort(422, message="Proxy {} already exists".format(str(ip_address)))

        return proxy

