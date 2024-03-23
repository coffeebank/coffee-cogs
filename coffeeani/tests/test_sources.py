import unittest
from unittest.mock import patch, Mock
import asyncio

from coffeeani_utils.sources import anilist, batoto, mangadex

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

class TestSources():
    def test_search_result_basics_exist(self, item):
        self.assertIsNotNone(item['link'])
        self.assertIsInstance(item['link'], str)
        self.assertIsNotNone(item['title'])
        self.assertIsInstance(item['title'], str)
        self.assertIsNotNone(item['description'])
        self.assertIsInstance(item['description'], str)


class TestAnilist(unittest.TestCase):
    def test_get_anilist_data_anime(self):
        results, data = asyncio.run(anilist.anilist_search_anime_manga("ANIME", "Arichan the Ant"))
        self.assertIsNotNone(data)
        for item in results:
            TestSources.test_search_result_basics_exist(self, item)

    def test_get_anilist_data_anime_false(self):
        results = asyncio.run(anilist.anilist_search_anime_manga("ANIME", LOREM_IPSUM))
        self.assertEquals(results, None)

    def test_get_anilist_data_manga(self):
        results, data = asyncio.run(anilist.anilist_search_anime_manga("MANGA", "Give My Regards to Black Jack"))
        self.assertIsNotNone(data)
        for item in results:
            TestSources.test_search_result_basics_exist(self, item)

    def test_get_anilist_data_manga_false(self):
        results = asyncio.run(anilist.anilist_search_anime_manga("MANGA", LOREM_IPSUM))
        self.assertEquals(results, None)


class TestBatoto(unittest.TestCase):
    def test_get_batoto_data_manga(self):
        results, data = asyncio.run(batoto.batoto_search_manga("Give My Regards to Black Jack"))
        self.assertIsNotNone(data)
        for item in results:
            TestSources.test_search_result_basics_exist(self, item)

    def test_get_batoto_data_manga_false(self):
        results = asyncio.run(batoto.batoto_search_manga(LOREM_IPSUM))
        self.assertEquals(results, None)


if __name__ == "__main__":
    unittest.main()
