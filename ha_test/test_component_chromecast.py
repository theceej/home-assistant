"""
ha_test.test_component_chromecast
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests Chromecast component.
"""
# pylint: disable=too-many-public-methods,protected-access
import logging
import unittest

import homeassistant as ha
from homeassistant.const import (
    SERVICE_TURN_OFF, SERVICE_VOLUME_UP, SERVICE_VOLUME_DOWN,
    SERVICE_MEDIA_PLAY_PAUSE, SERVICE_MEDIA_PLAY, SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_NEXT_TRACK, SERVICE_MEDIA_PREV_TRACK, ATTR_ENTITY_ID,
    CONF_HOSTS)
import homeassistant.components.chromecast as chromecast
from helpers import mock_service


def setUpModule():   # pylint: disable=invalid-name
    """ Setup to ignore chromecast errors. """
    logging.disable(logging.CRITICAL)


class TestChromecast(unittest.TestCase):
    """ Test the chromecast module. """

    def setUp(self):  # pylint: disable=invalid-name
        self.hass = ha.HomeAssistant()

        self.test_entity = chromecast.ENTITY_ID_FORMAT.format('living_room')
        self.hass.states.set(self.test_entity, chromecast.STATE_NO_APP)

        self.test_entity2 = chromecast.ENTITY_ID_FORMAT.format('bedroom')
        self.hass.states.set(self.test_entity2, "Youtube")

    def tearDown(self):  # pylint: disable=invalid-name
        """ Stop down stuff we started. """
        self.hass.stop()

    def test_is_on(self):
        """ Test is_on method. """
        self.assertFalse(chromecast.is_on(self.hass, self.test_entity))
        self.assertTrue(chromecast.is_on(self.hass, self.test_entity2))

    def test_services(self):
        """
        Test if the call service methods conver to correct service calls.
        """
        services = {
            SERVICE_TURN_OFF: chromecast.turn_off,
            SERVICE_VOLUME_UP: chromecast.volume_up,
            SERVICE_VOLUME_DOWN: chromecast.volume_down,
            SERVICE_MEDIA_PLAY_PAUSE: chromecast.media_play_pause,
            SERVICE_MEDIA_PLAY: chromecast.media_play,
            SERVICE_MEDIA_PAUSE: chromecast.media_pause,
            SERVICE_MEDIA_NEXT_TRACK: chromecast.media_next_track,
            SERVICE_MEDIA_PREV_TRACK: chromecast.media_prev_track
        }

        for service_name, service_method in services.items():
            calls = mock_service(self.hass, chromecast.DOMAIN, service_name)

            service_method(self.hass)
            self.hass.pool.block_till_done()

            self.assertEqual(1, len(calls))
            call = calls[-1]
            self.assertEqual(chromecast.DOMAIN, call.domain)
            self.assertEqual(service_name, call.service)

            service_method(self.hass, self.test_entity)
            self.hass.pool.block_till_done()

            self.assertEqual(2, len(calls))
            call = calls[-1]
            self.assertEqual(chromecast.DOMAIN, call.domain)
            self.assertEqual(service_name, call.service)
            self.assertEqual(self.test_entity,
                             call.data.get(ATTR_ENTITY_ID))

    def test_setup(self):
        """
        Test Chromecast setup.
        We do not have access to a Chromecast while testing so test errors.
        In an ideal world we would create a mock pychromecast API..
        """
        self.assertFalse(chromecast.setup(
            self.hass, {chromecast.DOMAIN: {CONF_HOSTS: '127.0.0.1'}}))
