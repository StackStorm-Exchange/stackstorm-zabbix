#!/usr/bin/env python

from lib.foreman import ForemanHosts


class ForemanHostSearch(ForemanHosts):

    def run(self, extended, running, query_filter=None):
        return True, dict(hosts=self.hosts("hosts", extended, running, params=query_filter))
