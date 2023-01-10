import xml.dom.minidom
from xml.dom.minidom import *


def get_inner_data(tags):
    """
    Function to grab inner data from xml tag. Function works on recursion to get
    content from each tag.
    :param tags: tags that are going to be processed
    :return: dictionary of content inside each tag
    """
    data = {}
    counter = 0
    for tag in tags:
        if len(tag.childNodes) == 0:
            if isinstance(tag, Text) and "\n" not in tag.data:
                return tag.data
            else:
                pass

        elif len(tag.childNodes) == 1:
            if not isinstance(tag, Text):
                data[tag.tagName] = get_inner_data(tag.childNodes)

        elif len(tag.childNodes) > 1:
            inner = {}
            for node in tag.childNodes:
                if isinstance(node, Text) and "\n" in node.data:
                    pass
                elif isinstance(node, Text) and "\n" not in node.data:
                    data[tag.tagName] = tag.childNodes[0].data
                else:
                    if node.tagName == 'metadata':
                        inner[node.getAttribute('id')] = get_inner_data(node.childNodes).get('value')
                    elif node.tagName in data.keys():
                        data[f"{node.tagName}_{counter}"] = get_inner_data(node.childNodes)
                        counter += 1
                    else:
                        inner[node.tagName] = get_inner_data(node.childNodes)
            data[tag.tagName] = inner
    return data


def get_main_tag_data(tags):
    return [get_inner_data([tag]) for tag in tags]


def handler(tag_name: str, file_content) -> {}:
    dom = xml.dom.minidom.parseString(file_content)
    tags = dom.getElementsByTagName(tag_name)
    data = get_main_tag_data(tags)[0]
    return data
