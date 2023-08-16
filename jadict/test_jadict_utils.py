import unittest

from jadict_utils import *

class TestRomajiConversion(unittest.TestCase):

    def test_basic_hiragana(self):
        self.assertEqual(to_romaji('あ'), 'a')
        self.assertEqual(to_romaji('き'), 'ki')
        self.assertEqual(to_romaji('す'), 'su')

    def test_basic_katakana(self):
        self.assertEqual(to_romaji('ア'), 'a')
        self.assertEqual(to_romaji('キ'), 'ki')
        self.assertEqual(to_romaji('ス'), 'su')

    def test_special_characters(self):
        self.assertEqual(to_romaji('し'), 'shi')
        self.assertEqual(to_romaji('ち'), 'chi')
        self.assertEqual(to_romaji('つ'), 'tsu')
        self.assertEqual(to_romaji('シ'), 'shi')
        self.assertEqual(to_romaji('チ'), 'chi')
        self.assertEqual(to_romaji('ツ'), 'tsu')

    def test_combined_characters(self):
        self.assertEqual(to_romaji('きゃ'), 'kya')
        self.assertEqual(to_romaji('しゅ'), 'shu')
        self.assertEqual(to_romaji('チャ'), 'cha')
        self.assertEqual(to_romaji('キュ'), 'kyu')

    def test_long_vowels(self):
        self.assertEqual(to_romaji('とう'), 'tou')
        # self.assertEqual(to_romaji('トー'), 'tou')

if __name__ == '__main__':
    unittest.main()
