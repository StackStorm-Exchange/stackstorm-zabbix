import yaml
import json

from st2tests.base import BaseActionTestCase


class ZabbixBaseActionTestCase(BaseActionTestCase):
    __test__ = False

    def setUp(self):
        super(ZabbixBaseActionTestCase, self).setUp()

        self._full_config = self.load_yaml('full.yaml')
        self._blank_config = self.load_yaml('blank.yaml')

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))

    @property
    def full_config(self):
        return self._full_config

    @property
    def blank_config(self):
        return self._blank_config
