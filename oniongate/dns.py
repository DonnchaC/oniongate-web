"""
Scripts for loading domain->onion mappings and generating zone files
"""
import os
import time

from flask import current_app, render_template_string, Markup
import zone_file

from .models import Domain, Proxy


def read_if_exists(filename):
    """
    Read the contents of a file if it exists
    """
    try:
        with open(filename, 'r') as file_handler:
            return file_handler.read().strip()
    except FileNotFoundError:
        current_app.logger.info("Could not open file %s", filename)
        return

def build_zone_base_template(zone):
    """
    Load template files from the zone file directory and create the base NS and static records
    """
    template_data = []
    zone_dir = current_app.config['zone_dir']

    base_template = read_if_exists(os.path.join(zone_dir, 'base_zone.j2'))
    if base_template:
        template_data.append(base_template)

    zone_template = read_if_exists(os.path.join(zone_dir, '{}.zone.j2'.format(zone)))
    if zone_template:
        template_data.append(zone_template)

    template = '\n'.join(template_data)

    # Use Markup to mark the string as safe, we're not generating HTML
    return render_template_string(Markup(template), origin=zone)


def select_proxy_a_records(record_label):
    """
    Select online A and AAAA records to include in a zone
    """
    records = {'a': [], 'aaaa': []}
    for proxy in Proxy.query.filter_by(online=True).all():
        # Create a dict with the values for the A or AAAA record.
        record = {
            'name': record_label,
            'ttl': current_app.config["A_RECORD_TTL"],
            'ip': proxy.ip_address,
        }
        if proxy.ip_type == '4':
            records["a"].append(record)
        elif proxy.ip_type == '6':
            records["aaaa"].append(record)
    return records


def generate_zone_file(zone_name):
    """
    Generate a zone file containing all the records for a zone.
    """
    # Load the base records for the zone from a static zone file
    zone_base = build_zone_base_template(zone_name)
    records = zone_file.parse_zone_file(zone_base)

    # Check if we are generating the zone that returns proxy A records
    proxy_domain = current_app.config["PROXY_ZONE"]
    if proxy_domain.endswith(zone_name):
        # Determine the subdomain where proxy A records will be listed
        proxy_subdomain = proxy_domain.split(zone_name)[0].strip(".")

        # Add all online entry proxies to round-robin on this subdomain
        proxy_records  = select_proxy_a_records(proxy_subdomain)
        for record_type in ["a", "aaaa"]:
            records[record_type].extend(proxy_records[record_type])

    # Add all subdomains and associated TXT records for this zone
    domains = Domain.query.filter_by(zone=zone_name, deleted=False).all()
    for domain in domains:
        # Create the CNAME or ALIAS record pointing to the proxy
        record = {'name': domain.subdomain, 'ttl': current_app.config["A_RECORD_TTL"]}
        if current_app.config.get("USE_ALIAS_RECORDS"):
            record["host"] = current_app.config["PROXY_ZONE"]
            records["alias"].append(record)
        else:
            record["alias"] = current_app.config["PROXY_ZONE"]
            records["cname"].append(record)

        # Create the TXT record with the domain->onion address mapping
        records["txt"].append({
            'name': domain.txt_label,
            'txt': "onion={}".format(domain.onion_address),
            'ttl': current_app.config["TXT_RECORD_TTL"]
        })

    # Fixes a bug in `zone_file` which places the SOA record inside a list
    records["soa"] = records["soa"].pop()

    # Bump the serial number in the SOA
    records["soa"]["serial"] = int(time.time())

    return zone_file.make_zone_file(records)
