import unittest
import json
from parameterized import parameterized
from unittest.mock import patch
from domain.aws_actions.aws_actions import prepare_data, authenticate_for_hive, send_data_to_hive

with open("./test_input_prepare_data.json", "r") as file:
    test_cases_prepare_data = json.load(file)


class TestPrepareData(unittest.TestCase):
    @parameterized.expand(test_cases_prepare_data)
    def test_prepare_data(self, data, expected_output):
        result = prepare_data(data)
        self.assertEqual(result, expected_output)


class TestAuthenticateForHive(unittest.TestCase):
    @patch('domain.aws_actions.aws_actions.get_credentials_to_authenticate')
    @patch('requests.post')
    def test_authenticate_for_hive_success(self, mock_post, mock_get_credentials):
        mock_get_credentials.return_value = ('username', 'password')
        mock_post.return_value.json.return_value = {'token': 'valid_token'}
        mock_post.return_value.ok = True

        result = authenticate_for_hive()

        self.assertEqual(result, {'token': 'valid_token'})
        mock_post.assert_called_once_with('http://app.sobeyhive.int:6446/api/v2/authentication',
                                          headers={'Content-Type': 'application/json-patch+json'},
                                          json={'loginName': 'username', 'password': 'password'})

    @patch('domain.aws_actions.aws_actions.get_credentials_to_authenticate')
    @patch('requests.post')
    def test_authenticate_for_hive_failure(self, mock_post, mock_get_credentials):
        mock_get_credentials.return_value = ('username', 'password')
        mock_post.return_value.json.return_value = {'error': 'Invalid credentials'}
        mock_post.return_value.ok = False

        result = authenticate_for_hive()

        self.assertEqual(result, {'error': 'Invalid credentials'})
        mock_post.assert_called_once_with('http://app.sobeyhive.int:6446/api/v2/authentication',
                                          headers={'Content-Type': 'application/json-patch+json'},
                                          json={'loginName': 'username', 'password': 'password'})

    @patch('domain.aws_actions.aws_actions.get_credentials_to_authenticate')
    @patch('requests.post')
    def test_authenticate_for_hive_exception(self, mock_post, mock_get_credentials):
        mock_get_credentials.return_value = ('username', 'password')
        mock_post.side_effect = Exception("Error connecting to the server")

        result = authenticate_for_hive()

        self.assertEqual(result, None)
        mock_post.assert_called_once_with('http://app.sobeyhive.int:6446/api/v2/authentication',
                                          headers={'Content-Type': 'application/json-patch+json'},
                                          json={'loginName': 'username', 'password': 'password'})
        mock_get_credentials.assert_called_once()


class TestSendDataToHive(unittest.TestCase):

    @patch('domain.aws_actions.aws_actions.authenticate_for_hive')
    def test_authenticate_for_hive_called(self, mock_auth):
        metadata = {"key1": "value1", "key2": "value2"}
        send_data_to_hive(metadata)
        mock_auth.assert_called_once()

    @patch('requests.put')
    @patch('domain.aws_actions.aws_actions.authenticate_for_hive')
    def test_send_data_to_hive_success(self, mock_put, mock_authenticate_for_hive):
        mock_authenticate_for_hive.return_value = "TEST_TOKEN"
        mock_put.return_value.status_code = 200
        metadata = {"key1": "value1", "key2": "value2"}
        response = send_data_to_hive(metadata)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"], metadata)

    @patch('requests.put')
    @patch('domain.aws_actions.aws_actions.authenticate_for_hive')
    def test_send_data_to_hive_failure(self, mock_put, mock_authenticate_for_hive):
        mock_authenticate_for_hive.return_value = "TEST_TOKEN"
        mock_put.side_effect = Exception("Error sending data")
        metadata = {"key1": "value1", "key2": "value2"}
        response = send_data_to_hive(metadata)
        self.assertEqual(response, None)


if __name__ == '__main__':
    unittest.main()
