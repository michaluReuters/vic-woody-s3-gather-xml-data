import xmltodict


def xml_to_dict(xml_string: str) -> dict:
    """
    Converts an XML string to a dictionary.

    :param:
        xml_string (str): The string containing the XML file.

    :return:
        dict: A dictionary representing the structure of the XML file.

    :raises:
        xmltodict.expat.ExpatError: If the provided string is not a valid XML.
    """

    return xmltodict.parse(xml_string)


def find_deep_value_bfs(data, key):
    """
    This function uses Breadth First Search (BFS) algorithm to search for a value associated with a specified key in
    a nested dictionary.It starts at the top level of the dictionary and visits each level of the dictionary
    breadth-first until it finds the key or all levels have been visited.

    :param:
        data (dict): The nested dictionary to search through.
        key (str): The key to search for.

    :return:
        any : The value associated with the specified key. Returns None if the key is not found.
        """
    queue = [data]
    while queue:
        current = queue.pop(0)
        if isinstance(current, dict):
            if key in current:
                return current[key]
            for value in current.values():
                queue.append(value)
    return None


def find_specified_tag_in_xml(data_xml: str, tag_name: str) -> {}:
    """
    This function is a combination of two above functions to get specified tag from xml string input

    :param:
        data_xml: string containing xml data
        tag_name: specified tag to get

    :return:
        dict : data that is stored in specified tag if provided, else None
    """

    if tag_name:
        return find_deep_value_bfs(xml_to_dict(data_xml), tag_name)
    else:
        return None
