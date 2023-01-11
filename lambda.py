import json
import boto3
from botocore.exceptions import ClientError
from xml_handler import handler
import logging
import requests


def lambda_handler(event, context):
    event_dict = json.loads(event["Records"][0]["Sns"]["Message"])
    logging.info(f"Incoming event to be processed: {event_dict}")
    print(f"Incoming event to be processed: {event_dict}")

    data = {}
    file_name_sns = event_dict["body"]["metadata"].get("name")
    hive_material_id = event_dict["body"]["metadata"].get("id")
    data["file_name"] = file_name_sns
    data["id"] = hive_material_id

    if not file_in_s3_bucket(file_name_sns):
        logging.info(f"Could not find resource in s3 for: {file_name_sns}.xml")
        print(f"Could not find resource in s3 for: {file_name_sns}.xml")
        data["workflows"] = None
        data["sources"] = None
        return data

    s3_client = boto3.client("s3")
    object_key = f"{file_name_sns}.xml"
    file_content = s3_client.get_object(
        Bucket="sh-woody-poc-xml", Key=object_key)["Body"].read().decode("UTF-8")
    ready_file_content = "".join(line.strip() for line in file_content.splitlines())

    workflows = handler("workflow", ready_file_content)
    sources = handler("metadatas", ready_file_content)

    data["workflow"] = workflows.get("workflow")
    data["metadatas"] = sources.get("metadatas")

    send_data_to_hive(prepare_data(data))


def filter_user_metadata(pair):
    """
    Function to filter if pair contains wanted key
    :param pair: key value pair from parsed data dictionary
    :return: boolean status
    """
    wanted_key = "usermetadata"
    key, value = pair
    if wanted_key in str(key):
        return True
    else:
        return False


def prepare_data(data):
    """
    Prepares metadata according to Hive Api spec
    :param data: parsed data from s3 xml file
    :return: prepared metadata for sending
    """

    logging.info("Preparing parsed data...")
    print("Preparing parsed data...")
    id_data = data["id"]
    name = data["metadatas"].get("mm_source_name")
    custom_metadata = {
        "social_source_uri_CHAR": data["metadatas"].get("social_source_uri"),
        "social_author_CHAR": data["metadatas"].get("social_author"),
        "social_network_CHAR": data["metadatas"].get("social_network"),
        "social_description_CHAR": data["metadatas"].get("social_description"),
        "social_publish_date_CHAR": data["metadatas"].get("mm_source_date"),
        "social_user_CHAR": data["workflow"]["user"]["name"],
    }

    filtered_data = dict(filter(filter_user_metadata, data["metadatas"].items()))
    custom_metadata["social_user_metadata_CHAR"] = list(filtered_data.values())[0]

    result = {
        "id": id_data,
        "name": name,
        "customMetadata": custom_metadata
    }
    logging.info(f"Parsed data prepared: {custom_metadata}\n Returning result: {result}")
    print(f"Parsed data prepared: {custom_metadata}\n Returning result: {result}")
    return result


def authenticate_for_hive():
    """
    Basic authentication for Hive application
    :return: Valid Token to authenticate
    """
    try:
        logging.info("Sending request to authenticate")
        print("Sending request to authenticate")
        headers = {
            'Content-Type': 'application/json-patch+json',
        }
        requests_body = {
            "loginName": "test",
            "password": "test"
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
    Sends prepared metadata to hive api
    :param metadata: Prepared data according to api spec
    :return: None
    """
    try:
        auth_resp = authenticate_for_hive()
        auth_token = auth_resp["data"]["token"]
        print(f"Trying to send data with token: {auth_token}")

        headers = {
            'Content-Type': 'application/json-patch+json',
            'Accept': 'text/plain',
            'Authorization': f"Bearer {str(auth_token)}"
        }

        r = requests.put('http://app.sobeyhive.int:6446/api/v2/metadata/material?force=true', headers=headers,
                         json=metadata)
        print(r.json())
    except Exception as exc:
        logging.error(f"There has been an error with Updating data to Hive! Error is: {exc}")
        print(f"There has been an error with Updating data to Hive! Error is: {exc}")


def file_in_s3_bucket(file_name_sns):
    """
    Checks if specified file exists in s3 bucket
    :param file_name_sns: file that needs to be checked
    :return: boolean status
    """

    s3_bucket = boto3.resource("s3")
    try:
        s3_bucket.Object("sh-woody-poc-xml", f"{file_name_sns}.xml").load()
    except ClientError:
        return False
    return True
