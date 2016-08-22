from functools import wraps

from flask import current_app, request
from flask_restful import abort
from itsdangerous import JSONWebSignatureSerializer, BadSignature

def create_jwt(payload):
    """
    Create a signed JSON Web Token
    """
    serializer = JSONWebSignatureSerializer(current_app.secret_key, algorithm_name='HS256')
    return serializer.dumps(payload)

def load_jwt(token):
    """
    Verify and load a signed JSON Web Token
    """
    serializer = JSONWebSignatureSerializer(current_app.secret_key, algorithm_name='HS256')
    return serializer.loads(token)

def read_auth_header(header_prefix='Bearer'):
    """
    Try to read the JWT from the Authorization header
    """
    auth_header_value = request.headers.get('Authorization', None)
    if not auth_header_value:
        return

    parts = auth_header_value.split()
    if parts[0].lower() != header_prefix.lower() or len(parts) != 2:
        abort(401, message='Invalid JWT header')
    return parts[1]

def jwt_domain():
    """
    Require a valid JWT token to be present in the request
    """
    token = read_auth_header()
    if token is None:
        abort(401, message='Authorization Required: Request does not contain '
              'an access token')

    try:
        payload = load_jwt(token)
    except BadSignature:
        abort(401, message='Invalid authorization token')
    return payload['domain']

def auth_domain():
    """
    Verify the user is trying to update the domain authorized in the JWT
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            authorized_domain = jwt_domain()
            if request.view_args.get('domain_name', '').lower() != authorized_domain:
                abort(401, message='Your update token is not valid for this domain')
            return fn(*args, **kwargs)
        return decorator
    return wrapper

