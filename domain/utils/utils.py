import boto3
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
    try:
        s3_bucket.Object("sh-woody-poc-xml", f"{file_name_sns}.xml").load()
    except ClientError:
        return False
    return True


def remove_special_characters(phrase: str) -> str:
    """
    This function removes unnecessary emojis and illegal characters from phrase

    :param:
        phrase: sentence that needs to be checked for special characters

    :return:
        str : without special characters
    """
    all_words = phrase.split()
    result = ["".join(ch for ch in word if ch.isalnum()) for word in all_words]
    words = (" ".join(result)).split()
    return " ".join(words)


def find_dict_by_id(list_dict, id_val) -> {}:
    """
    Finds the dictionary in the list that has the given id value.
    Returns the dictionary or None if not found

    :param:
        list_dict: list of dictionaries
        id_val: value of id field
    :return:
        dict: found dictionary or else None
    """
    id_dict = {}
    for d in list_dict:
        if "@id" in d:
            id_dict[d["@id"]] = d
    if id_val in id_dict:
        return id_dict[id_val]
    return None
