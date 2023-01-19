import json
import logging
import os
import boto3
import requests

from botocore.exceptions import ClientError


def file_in_s3_bucket(file_name_sns) -> bool:
    """
    Checks if specified file exists in s3 bucket

    :param:
        file_name_sns: file that needs to be checked

    :return:
        bool: status
    """
    s3_bucket = boto3.resource("s3")
    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
    try:
        s3_bucket.Object(s3_bucket_name, f"{file_name_sns}.xml").load()
    except ClientError:
        return False
    return True


def get_credentials_to_authenticate(client=boto3.client("secretsmanager", region_name="eu-west-2")) -> ():
    """
    This function gathers information on username and password from Security manager

    :return:
        (): username, password
    """
    secret_name = os.environ.get("SECRET_NAME")
    secret_username = os.environ.get("LOGIN_NAME")
    secret_password = os.environ.get("PASSWORD_FOR_LOGIN")
    response = client.get_secret_value(SecretId=secret_name)
    username = json.loads(response["SecretString"]).get(secret_username)
    password = json.loads(response["SecretString"]).get(secret_password)
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
            "Content-Type": "application/json-patch+json",
        }
        requests_body = {
            "loginName": credentials[0],
            "password": credentials[1]
        }
        url = os.environ.get("AUTHENTICATION_URL")
        r = requests.post(url, headers=headers, json=requests_body)
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
        logging.info(f"Trying to send data with token")
        print(f"Trying to send data with token")

        headers = {
            "Content-Type": "application/json-patch+json",
            "Accept": "text/plain",
            "Authorization": f"Bearer {str(auth_token)}"
        }
        url = os.environ.get("UPDATE_URL")
        requests.put(url, headers=headers, json=metadata)
        logging.info(f"Request send with body: {metadata}")
        print(f"Request send with body: {metadata}")
        return {
            "status": 200,
            "body": metadata
        }
    except Exception as exc:
        logging.error(f"There has been an error with Updating data to Hive! Error is: {exc}")
        print(f"There has been an error with Updating data to Hive! Error is: {exc}")
