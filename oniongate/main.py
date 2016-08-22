"""
Serve the static pages for the web service
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@main_bp.route('/domains/add', methods=['GET'])
def add_domain():
    return render_template('add_domain.html')
