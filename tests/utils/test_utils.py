import unittest

from parameterized import parameterized
from domain.utils.utils import remove_special_characters, find_dict_by_id, prepare_data
from tests.aws_actions.test_aws_actions import test_cases_prepare_data


class TestPrepareData(unittest.TestCase):
    @parameterized.expand(test_cases_prepare_data)
    def test_prepare_data(self, data, expected_output):
        result = prepare_data(data)
        self.assertEqual(result, expected_output)


class TestRemoveSpecialCharacters(unittest.TestCase):
    def test_remove_special_characters(self):
        self.assertEqual(remove_special_characters("Hello World ! How are you today?"),
                         "Hello World How are you today")
        self.assertEqual(remove_special_characters("This is a test #1"), "This is a test 1")
        self.assertEqual(remove_special_characters("Can you remove these symbols: !@#$%^&*()_-+="),
                         "Can you remove these symbols")

    def test_remove_emoji(self):
        self.assertEqual(remove_special_characters("Hello World 😊"), "Hello World")
        self.assertEqual(remove_special_characters("I love 🍕"), "I love")


class TestFindDictById(unittest.TestCase):
    def test_find_dict_by_id(self):
        # Test case 1: check if the function returns the correct dictionary
        list_dict = [{"@id": 1, "name": "John Doe"}, {"@id": 2, "name": "Jane Doe"}]
        id_val = 1
        expected_output = {"@id": 1, "name": "John Doe"}
        self.assertEqual(find_dict_by_id(list_dict, id_val), expected_output)

        # Test case 2: check if the function returns None if the id value is not found
        list_dict = [{"@id": 1, "name": "John Doe"}, {"@id": 2, "name": "Jane Doe"}]
        id_val = 3
        expected_output = None
        self.assertEqual(find_dict_by_id(list_dict, id_val), expected_output)

        # Test case 3: check if the function returns None if the list is empty
        list_dict = []
        id_val = 1
        expected_output = None
        self.assertEqual(find_dict_by_id(list_dict, id_val), expected_output)


if __name__ == "__main__":
    unittest.main()
