import os

class Config(object):
    SECRET_KEY = b'secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESTFUL_JSON = {'indent': 4, 'sort_keys': False}
    BUNDLE_ERRORS = True
    ERROR_404_HELP = False

    # The domain under which subdomains will be issued.
    SUBDOMAIN_HOST = "oniongate.com"

    MIN_SUBDOMAIN_LENGTH = 5
    A_RECORD_TTL = 120
    TXT_RECORD_TTL = 3600
    USE_ALIAS_RECORDS = False

    # The label which holds the A and AAAA records point to the online proxies
    PROXY_ZONE = "proxy.oniongate.com"

    # A list of public domains and subdomains which cannot be registered on this resolver
    DOMAIN_BLACKLIST = [
        SUBDOMAIN_HOST,
        'proxy',
        '_onion',
    ]

    # A list of onion address which cannot be registered
    RESTRICTED_ONIONS = []

    # Only allow registration of subdomains for now to prevent
    # potential security issues.
    FQDN_REGISTRATION_CLOSED = True


class ProdConfig(Config):
    ENV = 'prod'
    SECRET_KEY = os.environ.get('ANONSMS_SECRET_KEY')


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

class TestConfig(Config):
    ENV = 'test'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_ECHO = True
