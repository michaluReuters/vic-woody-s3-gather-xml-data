import json

from xml_handler import *


def handler(event):

    workflow = handler("workflow", "./test_input.xml")
    print(json.dumps(
        workflow[0],
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ))
    print("=============")

