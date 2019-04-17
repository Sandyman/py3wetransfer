import json
import logging
import requests
from .exc import WeTransferError
from .http import HttpClient


LOG = logging.getLogger("py3-wetransfer")
LOG.addHandler(logging.NullHandler())
LOG.setLevel(logging.INFO)


class WeTransferBase(HttpClient):
    WE_ENDPOINT_DEV = 'https://dev.wetransfer.com'

    def __init__(self, api_key, user_identifier=None):
        super().__init__()

        self.__x_api_key = api_key
        self.__user_identifier = user_identifier

        self.__token = None

        self.__authorize()

    def __authorize(self):
        """
        Authorize user based on x-api-key only. Store returned bearer token for future use.
        :return: None
        """
        address = self.endpoint('authorize')
        headers = self.__base_authorization_headers()
        kwargs = {'headers': headers}
        if self.__user_identifier is not None:
            kwargs['data'] = {'user_identifier': self.__user_identifier}

        r = requests.post(address, **kwargs)
        body = json.loads(r.text)
        if r.status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        self.__token = 'Bearer %s' % body['token']

    def endpoint(self, method):
        """
        Get endpoint for certain API method. Version v2.
        :param method: method to append to endpoint
        :return: endpoint for method
        """
        return '%s/%s/%s' % (self.WE_ENDPOINT_DEV, 'v2', method)

    def __base_authorization_headers(self):
        """
        Get base authorization headers.
        :return: headers
        """
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.__x_api_key
        }
        return headers

    def authorization_headers(self):
        """
        Get authorization headers.
        :return: headers
        """
        base_headers = self.__base_authorization_headers()
        headers = {'Authorization': self.__token}
        return {**headers, **base_headers}