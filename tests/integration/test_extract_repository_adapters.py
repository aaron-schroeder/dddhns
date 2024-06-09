import os
import unittest

import pandas as pd

from dddhns.ports.repository import AbstractExtractRepository
from dddhns.domain import model
from dddhns.adapters.repository.extract.strava import \
    StravaJSONFileExtractRepository
from dddhns.adapters.repository.extract.file import \
    GPXFileExtractRepository


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


# @unittest.skip('Not sure how to test this just yet. Been using real files.')
class TestStravaJSONFileExtractRepository(unittest.TestCase):
    def setUp(self):
        # TODO: seed some dummy data instead.
        self.path = os.path.join(THIS_DIR, 'data/strava')
        # self.path = '/home/aaron/strava-api-scraper/strava/data/'
        # '/mnt/c/Users/Aaron/Dropbox/activity_files/raw/strava_api/streams/'

        self.repo = StravaJSONFileExtractRepository(self.path)
    
    def test_find_all(self):
        result = self.repo.find_all()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], model.ActivityData)
        
    def test_get(self):
        result = self.repo.get(1234567890)
        self.assertIsInstance(result, model.ActivityData)


@unittest.skip('just noodlin')
class TestGPXFileExtractRepository(unittest.TestCase):
    def setUp(self):
        self.path = '/path/to/data/dir'
        self.repo = GPXFileExtractRepository(self.path)
    
    def test_find_all(self):
        result = self.repo.find_all()
        # Hmm. Wondering if it makes sense to still return a single
        # ActivityData instance with a multi-activity timeseries
        # attached. It still fits the bill, but could complicate things.
        self.assertIsInstance(result, model.ActivityData)
        
    # Now I don't understand how to test it. 
    def test_get_by_fname(self):
        # Honestly, seeing it here makes me think the name needs even
        # more description: ...JSON*Directory*Activity...
        result = self.repo.get_by_fname('fake.json')
        self.assertIsInstance(result, model.ActivityData)