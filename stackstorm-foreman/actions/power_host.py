#!/usr/bin/env python

from lib.foreman import ForemanAPI


class ForemanPowerHost(ForemanAPI):
    def __init__(self, config):
        super(ForemanPowerHost, self).__init__(config=config)

    def run(self, host, action):
        return self.put(endpoint="{}/{}/power".format('hosts', host), params={"power_action": action})
