#!/usr/bin/env python

from lib.foreman import ForemanHosts


class PuppetHostSearch(ForemanHosts):

    def run(self, environment, extended, running, query_filter=None):
        return True, dict(hosts=self.hosts('environments/{}/hosts'.format(environment), extended, running=running, params=query_filter))