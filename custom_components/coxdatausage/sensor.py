"""
Cox Data Usage Sensor

Example config:

- platform: Cox
  name: Cox Data Usage
  username: !secret cox_username
  password: !secret cox_password

Based on this: https://github.com/lachesis/comcast/blob/master/comcast.py

"""

import calendar
import datetime as dt
import json
import logging
import re

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_USERNAME, CONF_PASSWORD)
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from . import cox_login, async_call_api

_LOGGER = logging.getLogger(__name__)

DATA_USAGE_URL = 'https://www.cox.com/internet/mydatausage.cox'

DEFAULT_ICON = 'mdi:chart-line'

MIN_TIME_BETWEEN_UPDATES = dt.timedelta(minutes=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default='Cox'): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

ATTR_USED_DATA = 'Used data'
ATTR_TOTAL_DATA = 'Total data'
ATTR_DAYS_IN_MONTH = 'Days this month'
ATTR_DAYS_LEFT = 'Days Left in Cycle'
ATTR_UTILIZATION = 'Percentage Used'
ATTR_CURRENT_AVG_GB = 'Average GB Used Per Day'
ATTR_REMAINING_AVG_GB = 'Average GB Remaining Per Day'

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the sensor."""
    _LOGGER.debug('Cox: async_setup_platform')

    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    device = CoxDataUsage(hass, name, username, password)

    result = await device.async_update()
    if result is False:
        return

    async_add_devices([device])

class CoxDataUsage(Entity):
    """Representation of the sensor."""

    def __init__(self, hass, name, username, password):
        """Initialize the sensor."""

        self._hass = hass
        self._name = name
        self._username = username
        self._password = password

        self._identifier = f"cox_{username}"

        self._state = STATE_UNKNOWN
        self._state_attributes = None

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"sn_{self._identifier}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return "GB"

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return DEFAULT_ICON

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return additional information about the sensor."""
        return self._state_attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch the latest data."""

        self._state = STATE_UNKNOWN
        self._state_attributes = {}

        session = requests.session()
        session.verify = False

        self.session = session

        # perform the login
        response = await cox_login(self._hass, session, self._username, self._password)
        if response is None:
            return False

        # get the data usage
        response = await async_call_api(self._hass, session, DATA_USAGE_URL)
        if response is None:
            return False
        
        script_var = re.findall(r'var.utag_data={\s*(.*?)}\n', response.text, re.DOTALL | re.MULTILINE)
        json_str = "{" + script_var[0] + "}"
        response_object = json.loads(json_str)
        # Add total days in the current month
        now = dt.datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]

        usage = float(response_object['dumUsage'])
        limit = float(response_object['dumLimit'])
        days_left = float(response_object['dumDaysLeft'])
        utilization = response_object['dumUtilization']
        current_avg_gb = round((usage/max((days_in_month - days_left), 1)), 2)
        remaining_avg_gb = round((limit - usage) / max(days_left, 1), 2)

        self._state = usage
        self._state_attributes = {
            ATTR_USED_DATA: usage,
            ATTR_TOTAL_DATA: limit,
            ATTR_UTILIZATION: utilization,
            ATTR_DAYS_IN_MONTH: days_in_month,
            ATTR_DAYS_LEFT: days_left,
            ATTR_CURRENT_AVG_GB: current_avg_gb,
            ATTR_REMAINING_AVG_GB: remaining_avg_gb
        }

        return True
