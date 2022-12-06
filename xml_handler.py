import xml.dom.minidom
from xml.dom.minidom import *


def get_inner_data(element: Element):
    result = {}
    for base_node in element.childNodes:
        if isinstance(base_node, Text):
            if "\n" in base_node.data:
                pass
            else:
                result[element.tagName] = base_node.data
        elif isinstance(base_node, Element):
            inner = {}
            for i in base_node.childNodes:
                if isinstance(i, Element):
                    if len(i.childNodes) > 1:
                        inner[i.tagName] = {}
                        for j in i.childNodes:
                            if isinstance(j, Text):
                                pass
                            else:
                                inner[i.tagName][j.tagName] = get_inner_data(j).get(j.tagName)
                    else:
                        inner[i.tagName] = i.childNodes[0].data
                    result[base_node.tagName] = inner
                else:
                    if "\n" in i.data:
                        pass
                    else:
                        result[base_node.tagName] = i.data
    return result


def gather_data_for_tags(tags):
    workflow = []
    counter = 0
    for tag in tags:
        data = {}
        for node in tag.childNodes:
            if isinstance(node, Element):
                if len(node.childNodes) > 1:
                    data[f"{node.tagName}"] = get_inner_data(node)
                else:
                    if not len(node.childNodes) == 0:
                        data[f"{node.tagName}"] = node.childNodes[0].data
                counter += 1
            else:
                pass
        workflow.append(data)
    return workflow


def handler(tag_name, file_path):
    dom = xml.dom.minidom.parse(file_path)
    tags = dom.getElementsByTagName(tag_name)
    workflow = gather_data_for_tags(tags)

    return workflow
