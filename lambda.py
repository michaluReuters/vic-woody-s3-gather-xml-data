import json
import logging
import os
import boto3

from domain.aws_actions.aws_actions import file_in_s3_bucket, send_data_to_hive
from domain.utils.utils import prepare_data
from domain.utils.xml_handler import *


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
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    file_content = s3_client.get_object(
        Bucket=bucket_name, Key=object_key)["Body"].read().decode("UTF-8")
    ready_file_content = "".join(line.strip() for line in file_content.splitlines())

    workflows = find_specified_tag_in_xml(ready_file_content, "workflow")
    sources = find_specified_tag_in_xml(ready_file_content, "sources")
    data["workflow"] = workflows
    data["metadatas"] = sources["source"]["metadatas"]

    send_data_to_hive(prepare_data(data))
