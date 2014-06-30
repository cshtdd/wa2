from unittest import TestCase
from extapi.apikeyreader import ApiKeyReader


class TestApiKeyReader(TestCase):
    def test_key_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            ApiKeyReader().key()
