import os
import boto3
from botocore.exceptions import ClientError
from xml_handler import handler


def lambda_handler(event, context):
    data = {}
    file_name_sns = event["body"]["metadata"]["name"]
    hive_material_id = event["body"]["metadata"]["materialId"]
    s3 = boto3.client("s3")
    data["file_name"] = file_name_sns
    data["materialId"] = hive_material_id

    if not file_in_s3_bucket(file_name_sns, s3):
        data["workflows"] = None
        data["sources"] = None
        return data

    s3resource = boto3.resource("s3")
    file_path = f"/tmp/{file_name_sns}"
    s3resource.Bucket("sh-woody-poc-xml").download_file(file_name_sns, file_path)
    workflows = handler("workflow", file_path)
    sources = handler("sources", file_path)

    data["workflow"] = workflows
    data["sources"] = sources

    os.system(f"rm /tmp/{file_name_sns}")
    return data


def file_in_s3_bucket(file_name_sns, s3):
    try:
        s3.head_object(Bucket="sh-woody-poc-xml", Key=file_name_sns)
    except ClientError:
        return False
    return True
