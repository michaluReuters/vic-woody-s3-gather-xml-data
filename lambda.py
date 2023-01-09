import json
import os
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
    # file_name_sns = event_dict["body"]["metadata"].get("name")
    file_name_sns = "060A2B340101010501010D80130000002C290782BCC7CDBC7B5B5AE2504224B6"
    hive_material_id = event_dict["body"]["metadata"].get("id")
    s3 = boto3.client("s3")
    data["file_name"] = file_name_sns
    data["id"] = hive_material_id

    if not file_in_s3_bucket(file_name_sns, s3):
        logging.info(f"Could not find resource in s3 for: {file_name_sns}.xml")
        print(f"Could not find resource in s3 for: {file_name_sns}")
        data["workflows"] = None
        data["sources"] = None
        return data

    s3resource = boto3.resource("s3")
    file_path = f"/tmp/{file_name_sns}.xml"
    s3resource.Bucket("sh-woody-poc-xml").download_file(f"{file_name_sns}.xml", file_path)
    workflows = handler("workflow", file_path)
    sources = handler("sources", file_path)

    data["workflow"] = workflows.get('workflow')
    data["sources"] = sources.get('sources')

    os.system(f"rm /tmp/{file_name_sns}.xml")

    send_data_to_hive(prepare_data(data))

def filter_usermetadata(pair):
    wanted_key = "usermetadata"
    key, value = pair
    if wanted_key in str(key):
        return True
    else:
        return False
def prepare_data(data):
    logging.info("Preparing parsed data...")
    print("Preparing parsed data...")
    id_data = data["id"]
    # name = data["sources"]["source"]["metadatas"].get("mm_source_name")
    name = "CHANGED name"
    # custom_metadata = {
    #     "social_source_uri_CHAR": data["sources"]["source"]["metadatas"].get("social_source_uri"),
    #     "social_author_CHAR": data["sources"]["source"]["metadatas"].get("social_author"),
    #     "social_network_CHAR": data["sources"]["source"]["metadatas"].get("social_network"),
    #     "social_description_CHAR": data["sources"]["source"]["metadatas"].get("social_description"),
    #     "social_publish_date_CHAR": data["sources"]["source"]["metadatas"].get("mm_source_date"),
    #     "social_user_CHAR": data["workflow"]["user"]["name"],
    # }
    custom_metadata = {
        "social_source_uri_CHAR": "TEST",
        "social_author_CHAR": "TEST",
        "social_network_CHAR": "TEST",
        "social_description_CHAR": "TEST",
        "social_publish_date_CHAR": "TEST",
        "social_user_CHAR": "TEST",
    }

    filtered_data = dict(filter(filter_usermetadata, data["sources"]["source"]["metadatas"].items()))
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



def send_data_to_hive(data):
    try:
        auth_resp = authenticate_for_hive()
        auth_token = auth_resp["data"]["token"]
        print(f"Trying to send data with token: {auth_token}")

        headers = {
            'Content-Type': 'application/json-patch+json',
            'Accept': 'text/plain',
            'Authorization': f"Bearer {str(auth_token)}"
        }

        r = requests.put('http://app.sobeyhive.int:6446/api/v2/metadata/material?force=true', headers=headers, json=data)
        print(r.json())
    except Exception as exc:
        logging.error(f"There has been an error with Updating data to Hive! Error is: {exc}")
        print(f"There has been an error with Updating data to Hive! Error is: {exc}")


def file_in_s3_bucket(file_name_sns, s3):
    s3_bucket = boto3.resource("s3")
    try:
        s3_bucket.Object("sh-woody-poc-xml", f"{file_name_sns}.xml").load()
    except ClientError:

        my_bucket = s3_bucket.Bucket("sh-woody-poc-xml")
        for my_bucket_object in my_bucket.objects.all():
            print(my_bucket_object.key)
        return False
    return True


if __name__ == '__main__':
    print(authenticate_for_hive())
