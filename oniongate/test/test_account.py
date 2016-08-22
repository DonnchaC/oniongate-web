# -*- coding: utf-8 -*-
import pytest


def test_index(client):
    """
    Test if the index page loads
    """

    rv = cleint.get(url_for('main.index'))
    assert rv.status_code == 200


def test_create_account(client):
    pass


def test_load_account_from_form(client):
    """
    Load an account from the homepage form
    """
    pass


def test_load_account_from_url():
    """
    Load an account from a bookmarked URL
    """
    pass


def test_logout(client):
    """
    Test logging out of account
    """
    pass


def test_account_delete(client):
    """
    Test deleting an account and the associated data
    """
    pass


def test_create_phone_number(client):
    """
    Test creating a new phone number
    """
    pass

#     rv = testapp.post('/login', data=dict(
#         username='admin',
#         password="supersafepassword"
#     ), follow_redirects=True)

#     assert rv.status_code == 200
#     assert 'Logged in successfully.' in str(rv.data)

# def test_login_fail(self, testapp):
#     """ Tests if the login form fails correctly """

#     rv = testapp.post('/login', data=dict(
#         username='admin',
#         password=""
#     ), follow_redirects=True)

#     assert rv.status_code == 200
#     assert 'Invalid username or password' in str(rv.data)
