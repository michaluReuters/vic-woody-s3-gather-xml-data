from aws_lambda_powertools import Logger

logger = Logger()


def prepare_data(data):
    """
    Prepares metadata according to Hive Api spec

    :param:
        data: parsed data from s3 xml file

    :return:
        prepared metadata for sending
    """

    logger.info("Preparing parsed data...")
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
    custom_metadata["social_user_metadata_CHAR"] = list(filter(lambda x: "usermetadata" in x["@id"], metadata))[0][
        "value"]
    result = {
        "id": id_data,
        "name": name,
        "customMetadata": custom_metadata
    }
    logger.info(f"Parsed data prepared: {custom_metadata}\n Returning result: {result}")
    return result


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
