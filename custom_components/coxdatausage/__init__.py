"""This is a sensor to retrieve data on internet limits from cox"""

import logging
from functools import partial

import requests

_LOGGER = logging.getLogger(__name__)

SCOPE = "openid internal" #okta-login.js from cox login page
HOST_NAME = "www.cox.com" #okta-login.js
REDIRECT_URI = f"https://{HOST_NAME}/authres/code" #okta-login.js
AJAX_URL = f"https://{HOST_NAME}/authres/getNonce?onsuccess=" #okta-login.js
BASE_URL = 'https://cci-res.okta.com/' #okta-login.js
CLIENT_ID = '0oa1iranfsovqR6MG0h8' #okta-login.js
ISSUER = f"{BASE_URL}/oauth2/aus1jbzlxq0hRR6jG0h8" #okta-login.js
ON_SUCCESS_URL = "https%3A%2F%2Fwww.cox.com%2Fresaccount%2Fhome.html" #okta-login.js

async def cox_login(hass, session, username, password):

    data = {
        "username": username,
        "password": password,
        "options": {
            "multiOptionalFactorEnroll": False,
            "warnBeforePasswordExpired": False
        }
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = await async_call_api(hass, session, f"{AJAX_URL}{ON_SUCCESS_URL}")
    if response is None:
        return None

    nonceVal = response.text

    response = await async_call_api(hass, session, f"{BASE_URL}api/v1/authn", json=data, headers=headers)
    if response is None:
        return None

    sessionToken = response.json()['sessionToken']

    params = {
        'client_id': CLIENT_ID,
        'nonce': nonceVal,
        'redirect_uri': REDIRECT_URI,
        'response_mode': 'query',
        'response_type': 'code',
        'sessionToken': sessionToken,
        'state': 'https%3A%2F%2Fwww.cox.com%2Fwebapi%2Fcdncache%2Fcookieset%3Fresource%3Dhttps%3A%2F%2Fwww.cox.com%2Fresaccount%2Fhome.cox',
        'scope': SCOPE
    }

    response = await async_call_api(hass, session, f"{ISSUER}/v1/authorize", params=params, allow_redirects=True)
    if response is None:
        return None

    return response

async def async_call_api(hass, session, url, **kwargs):
    """Calls the given api and returns the response data"""
    kwargs['timeout'] = 10
    kwargs['verify'] = True
    try:
        req_func = session.get
        if kwargs.get("data") or kwargs.get("json"):
            req_func = session.post
        partial_req = partial(req_func, url, **kwargs)
        response = await hass.loop.run_in_executor(None, partial_req)
    except (requests.exceptions.RequestException, ValueError):
        _LOGGER.warning(
            'Request failed for url %s',
            url)
        return None

    if response.status_code != 200:
        _LOGGER.warning(
            'Invalid status_code %s from url %s',
            response.status_code, url)
        _LOGGER.warning(response.text)
        return None

    return response
