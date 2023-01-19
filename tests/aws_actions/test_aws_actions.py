import os
import unittest
import json

from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from domain.aws_actions.aws_actions import authenticate_for_hive, send_data_to_hive, file_in_s3_bucket

with open("../utils/test_input_prepare_data.json", "r") as file:
    test_cases_prepare_data = json.load(file)


class TestAuthenticateForHive(unittest.TestCase):
    @patch("domain.aws_actions.aws_actions.get_credentials_to_authenticate")
    @patch.object(os.environ, "get", return_value="http://test_url.com")
    @patch("requests.post")
    def test_authenticate_for_hive_success(self, mock_post, mock_get, mock_get_credentials):
        mock_get_credentials.return_value = ("username", "password")
        mock_post.return_value.json.return_value = {"token": "valid_token"}
        mock_post.return_value.ok = True

        result = authenticate_for_hive()

        self.assertEqual(result, {"token": "valid_token"})
        mock_post.assert_called_once_with("http://test_url.com",
                                          headers={"Content-Type": "application/json-patch+json"},
                                          json={"loginName": "username", "password": "password"})

    @patch("domain.aws_actions.aws_actions.get_credentials_to_authenticate")
    @patch.object(os.environ, "get", return_value="http://test_url.com")
    @patch("requests.post")
    def test_authenticate_for_hive_failure(self, mock_post, mock_get, mock_get_credentials):
        mock_get_credentials.return_value = ("username", "password")
        mock_post.return_value.json.return_value = {"error": "Invalid credentials"}
        mock_post.return_value.ok = False

        result = authenticate_for_hive()

        self.assertEqual(result, {"error": "Invalid credentials"})
        mock_post.assert_called_once_with("http://test_url.com",
                                          headers={"Content-Type": "application/json-patch+json"},
                                          json={"loginName": "username", "password": "password"})

    @patch("domain.aws_actions.aws_actions.get_credentials_to_authenticate")
    @patch.object(os.environ, "get", return_value="http://test_url.com")
    @patch("requests.post")
    def test_authenticate_for_hive_exception(self, mock_post, mock_get, mock_get_credentials):
        mock_get_credentials.return_value = ("username", "password")
        mock_post.side_effect = Exception("Error connecting to the server")

        result = authenticate_for_hive()

        self.assertEqual(result, None)
        mock_post.assert_called_once_with("http://test_url.com",
                                          headers={"Content-Type": "application/json-patch+json"},
                                          json={"loginName": "username", "password": "password"})
        mock_get_credentials.assert_called_once()


class TestSendDataToHive(unittest.TestCase):

    @patch("domain.aws_actions.aws_actions.authenticate_for_hive")
    def test_authenticate_for_hive_called(self, mock_auth):
        metadata = {"key1": "value1", "key2": "value2"}
        send_data_to_hive(metadata)
        mock_auth.assert_called_once()

    @patch("requests.put")
    @patch("domain.aws_actions.aws_actions.authenticate_for_hive")
    def test_send_data_to_hive_success(self, mock_put, mock_authenticate_for_hive):
        mock_authenticate_for_hive.return_value = "TEST_TOKEN"
        mock_put.return_value.status_code = 200
        metadata = {"key1": "value1", "key2": "value2"}
        response = send_data_to_hive(metadata)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"], metadata)

    @patch("requests.put")
    @patch("domain.aws_actions.aws_actions.authenticate_for_hive")
    def test_send_data_to_hive_failure(self, mock_put, mock_authenticate_for_hive):
        mock_authenticate_for_hive.return_value = "TEST_TOKEN"
        mock_put.side_effect = Exception("Error sending data")
        metadata = {"key1": "value1", "key2": "value2"}
        response = send_data_to_hive(metadata)
        self.assertEqual(response, None)


class TestFileInS3Bucket(unittest.TestCase):
    @patch.object(os.environ, "get", return_value="TEST_BUCKET")
    @patch("boto3.resource")
    def test_file_exists(self, mock_boto3_resource, mock_get):
        mock_object = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.Object.return_value = mock_object
        mock_boto3_resource.return_value = mock_bucket

        result = file_in_s3_bucket("test_file")

        mock_boto3_resource.assert_called_once_with("s3")
        mock_bucket.Object.assert_called_once_with("TEST_BUCKET", "test_file.xml")
        mock_object.load.assert_called_once()
        self.assertTrue(result)

    @patch.object(os.environ, "get", return_value="TEST_BUCKET")
    @patch("boto3.resource")
    def test_file_not_exists(self, mock_boto3_resource, mock_get):
        mock_bucket = MagicMock()
        mock_bucket.Object.side_effect = ClientError({"Error": {"Code": "404"}}, "load")
        mock_boto3_resource.return_value = mock_bucket

        result = file_in_s3_bucket("test_file")

        mock_boto3_resource.assert_called_once_with("s3")
        mock_bucket.Object.assert_called_once_with("TEST_BUCKET", "test_file.xml")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
