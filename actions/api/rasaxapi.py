# -*- coding: utf-8 -*-
from typing import Text
import requests
import logging

from rasa_sdk import Tracker

from actions import config

logger = logging.getLogger(__name__)


class RasaXAPI:
    """Class to connect to the Rasa X API"""

    def __init__(
        self,
        schema: Text = config.rasa_x_host_schema,
        host: Text = config.rasa_x_host,
        username: Text = config.rasa_x_username,
        password: Text = config.rasa_x_password,
    ):
        self.schema = schema
        self.host = host
        self.username = username
        self.password = password

    def get_auth_header(self):
        """Get authorization header with bearer token"""
        url = f"{self.schema}://{self.host}/api/auth"
        payload = {"username": self.username, "password": self.password}
        response = requests.post(url, json=payload)
        try:
            authtoken = response.json()["access_token"]
            header = {"Authorization": f"Bearer {authtoken}"}
            return header
        except Exception as e:
            logger.debug(
                f"Failed to fetch authorization header from Rasa X, using empty auth error: {e}"
            )
            return {}

    def flag_message(self, tracker: Tracker) -> requests.Response:
        """Flag a message in Rasa X for review"""
        auth_header = self.get_auth_header()
        endpoint2 = (f"{self.schema}://{self.host}/api/conversations/{tracker.sender_id}/messages")
        message_timestamp = requests.get(url=endpoint2, headers=auth_header).json()['messages'][-2]['timestamp']
        endpoint = (
            f"{self.schema}://{self.host}/api/conversations/{tracker.sender_id}/messages/{message_timestamp}/flag"
        )
        response = requests.put(url=endpoint, headers=auth_header)
        return response
        
