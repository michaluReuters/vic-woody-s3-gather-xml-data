import json
import logging

import boto3
import requests

from domain.utils.utils import remove_special_characters, find_dict_by_id


def prepare_data(data):
    """
    Prepares metadata according to Hive Api spec

    :param:
        data: parsed data from s3 xml file

    :return:
        prepared metadata for sending
    """

    logging.info("Preparing parsed data...")
    print("Preparing parsed data...")
    id_data = data["id"]
    metadata = data["metadatas"]["metadata"]
    name = remove_special_characters(
        find_dict_by_id(metadata, "mm_source_name")["value"]
    )

    required_fields = [
        "social_source_uri",
        "social_author",
        "social_network",
        "social_description",
    ]

    custom_metadata = {f"{key}_CHAR": find_dict_by_id(metadata, key)["value"] for key in required_fields}
    custom_metadata["social_publish_date_CHAR"] = find_dict_by_id(metadata, "mm_source_date")["value"]
    custom_metadata["social_user_CHAR"] = data["workflow"]["user"]["name"]
    custom_metadata["social_user_metadata_CHAR"] = list(filter(lambda x: "usermetadata" in x['@id'], metadata))[0][
        "value"]
    result = {
        "id": id_data,
        "name": name,
        "customMetadata": custom_metadata
    }
    logging.info(f"Parsed data prepared: {custom_metadata}\n Returning result: {result}")
    print(f"Parsed data prepared: {custom_metadata}\n Returning result: {result}")
    return result


def get_credentials_to_authenticate(client=boto3.client('secretsmanager', region_name="eu-west-2")) -> ():
    """
    This function gathers information on username and password from Security manager

    :return:
        (): username, password
    """
    response = client.get_secret_value(SecretId='ppe_hive_api_credentials')
    username = json.loads(response['SecretString']).get('HIVE_LOGINNAME')
    password = json.loads(response['SecretString']).get('HIVE_LOGINPWD')
    return username, password


def authenticate_for_hive() -> {}:
    """
    This function  runs basic authentication for Hive application

    :return:
        str : Valid Token to authenticate
    """
    credentials = get_credentials_to_authenticate()

    try:
        logging.info("Sending request to authenticate")
        print("Sending request to authenticate")
        headers = {
            'Content-Type': 'application/json-patch+json',
        }
        requests_body = {
            "loginName": credentials[0],
            "password": credentials[1]
        }
        r = requests.post('http://app.sobeyhive.int:6446/api/v2/authentication', headers=headers, json=requests_body)
        logging.info("Authentication succeed!")
        print("Authentication succeed!")
        return r.json()
    except Exception as exc:
        logging.error(f"There has been an error with Authentication! Error is: {exc}")
        print(f"There has been an error with Authentication! Error is: {exc}")


def send_data_to_hive(metadata):
    """
    This function sends prepared metadata to hive api

    :param
        metadata: Prepared data according to api spec
    """
    try:
        auth_resp = authenticate_for_hive()
        auth_token = auth_resp["data"]["token"]
        logging.info(f"Trying to send data with token: {auth_token}")
        print(f"Trying to send data with token: {auth_token}")

        headers = {
            'Content-Type': 'application/json-patch+json',
            'Accept': 'text/plain',
            'Authorization': f"Bearer {str(auth_token)}"
        }

        r = requests.put('http://app.sobeyhive.int:6446/api/v2/metadata/material?force=true', headers=headers,
                         json=metadata)
        logging.info(f"Request send with body: {metadata}")
        print(f"Request send with body: {metadata}")
        return {
            "status": 200,
            "body": metadata
        }
    except Exception as exc:
        logging.error(f"There has been an error with Updating data to Hive! Error is: {exc}")
        print(f"There has been an error with Updating data to Hive! Error is: {exc}")