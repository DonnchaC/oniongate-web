"""
Serve the static pages for the web service
"""

from flask import Blueprint, render_template

from .models import Domain, Proxy

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    """
    Prepare some stats for the home page
    """
    percent_online_domains, percent_online_proxies = 0, 0
    recent_domains = Domain.recent_public_domains(10)
    num_domains_issued = Domain.query.filter_by(deleted=False).count()
    online_domains = Domain.query.filter_by(service_online=True, deleted=False).count()

    num_entry_proxies = Proxy.query.count()
    online_entry_proxies = Proxy.query.filter_by(online=True).count()

    if num_domains_issued:
        percent_online_domains = online_domains / num_domains_issued
        print(percent_online_domains)
    if num_entry_proxies:
        percent_online_proxies = online_entry_proxies / num_entry_proxies

    return render_template('index.html', recent_domains=recent_domains,
                           num_domains_issued=num_domains_issued,
                           percent_online_domains=percent_online_domains,
                           num_entry_proxies=num_entry_proxies,
                           percent_online_proxies=percent_online_proxies)


@main_bp.route('/domains/add', methods=['GET'])
def add_domain():
    return render_template('add_domain.html')
