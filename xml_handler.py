import xml.dom.minidom
from xml.dom.minidom import *


def get_inner_data(tags):
    '''
    Function to grab inner data from xml tag. Function works on recursion to get
    content from each tag.
    :param tags: tags that are going to be processed
    :return: dictionary of content inside each tag
    '''
    data = {}
    counter = 0
    for tag in tags:
        if len(tag.childNodes) == 0:
            if isinstance(tag, Text) and "\n" not in tag.data:
                return tag.data
            else:
                pass
        elif len(tag.childNodes) == 1:
            if isinstance(tag.childNodes[0], Element):
                data[tag.childNodes[0].tagName] = get_inner_data(tag.childNodes)
            elif isinstance(tag.childNodes[0], Text):
                if "\n" in tag.childNodes[0].data:
                    pass
                else:
                    data[tag.tagName] = tag.childNodes[0].data
        elif len(tag.childNodes) > 1:
            for node in tag.childNodes:
                if isinstance(node, Text) and "\n" in node.data:
                    pass
                else:
                    if node.tagName in data.keys():
                        data[f"{node.tagName}_{counter}"] = get_inner_data(node.childNodes)
                        counter += 1
                    else:
                        data[node.tagName] = get_inner_data(node.childNodes)

    return data


def handler(tag_name: str, file_path) -> {}:
    dom = xml.dom.minidom.parse(file_path)
    tags = dom.getElementsByTagName(tag_name)
    data = get_inner_data(tags)
    return data
