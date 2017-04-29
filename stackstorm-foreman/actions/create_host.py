#!/usr/bin/env python

from lib.foreman import ForemanAPI
from time import time


class NewHost(ForemanAPI):
    def __init__(self, config):
        super(NewHost, self).__init__(config=config)

    def run(self, unattended, provision_method, name, hostconfig):

        hostconfig['provision_method'] = provision_method
        payload = {"host": hostconfig}

        if unattended:
            sec, ms = str(time()).split('.')
            suffix = str(int(sec) + int(ms))
            hostconfig['name'] = name + suffix
        else:
            hostconfig['name'] = name

        return self.post(endpoint='hosts', verify_ssl=self.verify_ssl, payload=payload)
