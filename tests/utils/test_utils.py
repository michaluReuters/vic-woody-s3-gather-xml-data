import unittest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from domain.utils.utils import file_in_s3_bucket, remove_special_characters, find_dict_by_id


class TestFileInS3Bucket(unittest.TestCase):
    @patch("boto3.resource")
    def test_file_exists(self, mock_boto3_resource):
        mock_object = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.Object.return_value = mock_object
        mock_boto3_resource.return_value = mock_bucket

        result = file_in_s3_bucket("test_file")

        mock_boto3_resource.assert_called_once_with("s3")
        mock_bucket.Object.assert_called_once_with("sh-woody-poc-xml", "test_file.xml")
        mock_object.load.assert_called_once()
        self.assertTrue(result)

    @patch("boto3.resource")
    def test_file_not_exists(self, mock_boto3_resource):
        mock_bucket = MagicMock()
        mock_bucket.Object.side_effect = ClientError({"Error": {"Code": "404"}}, "load")
        mock_boto3_resource.return_value = mock_bucket

        result = file_in_s3_bucket("test_file")

        mock_boto3_resource.assert_called_once_with("s3")
        mock_bucket.Object.assert_called_once_with("sh-woody-poc-xml", "test_file.xml")
        self.assertFalse(result)


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
