#!/usr/bin/env python

from st2actions.runners.pythonrunner import Action
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RequestsMethod(object):
    @staticmethod
    def method(method, url, auth=None, verify_ssl=False, headers=None, params=None, json=None):
        methods = {'get': requests.get,
                   'post': requests.post,
                   'put': requests.put}

        if not params:
            params = dict()

        if not json:
            json = dict()

        requests_method = methods.get(method)
        response = requests_method(url, auth=auth, headers=headers, params=params, json=json, verify=verify_ssl)
        if response.status_code:
            return response.json()
        else:
            return response.text


class ForemanAPI(Action):
    def __init__(self, config):
        super(ForemanAPI, self).__init__(config=config)
        self.url = self.config.get('url', None)
        self.username = self.config.get('username', None)
        self.password = self.config.get('password', None)
        self.verify_ssl = self.config.get('verify_ssl', False)

        self._headers = {"Accept": "version=2,application/json"}

    def running_hosts(self, hosts):
        for host in hosts:
            try:
                hostname = host.get('name')
            except AttributeError:
                hostname = host

            host_status = self.get("hosts/{0}/vm_compute_attributes".format(hostname),
                                   verify_ssl=self.verify_ssl).get('state')
            if host_status.lower() not in ['shutoff']:
                yield host

    def _get(self, endpoint, params=None, *args, **kwargs):
        api_url = "{url}/{api_ext}/{endpoint}".format(url=self.url, api_ext='api', endpoint=endpoint)
        return RequestsMethod.method('get',
                                     url=api_url,
                                     auth=(self.username, self.password),
                                     verify_ssl=self.verify_ssl,
                                     headers=self._headers,
                                     params=params)

    def _post(self, endpoint, params=None, payload=None, *args, **kwargs):
        api_url = "{url}/{api_ext}/{endpoint}".format(url=self.url, api_ext='api', endpoint=endpoint)
        return RequestsMethod.method('post',
                                     url=api_url,
                                     auth=(self.username, self.password),
                                     verify_ssl=self.verify_ssl,
                                     headers=self._headers,
                                     params=params,
                                     json=payload)

    def _put(self, endpoint, params=None, payload=None, *args, **kwargs):
        api_url = "{url}/{api_ext}/{endpoint}".format(url=self.url, api_ext='api', endpoint=endpoint)
        return RequestsMethod.method('put',
                                     url=api_url,
                                     auth=(self.username, self.password),
                                     verify_ssl=self.verify_ssl,
                                     headers=self._headers,
                                     params=params,
                                     json=payload)

    def get(self, *args, **kwargs):
        return self._get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self._put(*args, **kwargs)


class ForemanHosts(ForemanAPI):
    def __init__(self, config):
        super(ForemanHosts, self).__init__(config=config)

    def hosts(self, endpoint, extended, running, params):
        hosts_raw = self.get(endpoint, params=params, verify_ssl=self.verify_ssl).get('results')
        if running:
            hosts = [host for host in self.running_hosts(hosts_raw)]
        else:
            hosts = hosts_raw

        if not extended:
            try:
                return [host.get('name') for host in hosts]
            except AttributeError:
                return [host for host in hosts]

        return hosts
