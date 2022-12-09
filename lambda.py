import os

from xml_handler import *


def lambda_handler(event, context):

    content = event["Records"][0]["Sns"]["RequestData"]
    with open("/tmp/tmpFile.xml", "w") as file:
        file.write(content)
    with open("/tmp/tmpFile.xml", "r"):
        workflows = handler("workflow", "/tmp/tmpFile.xml")
        sources = handler("sources", "/tmp/tmpFile.xml")
        result = {
            "workflow": workflows,
            "sources": sources
        }
    os.system("rm /tmp/tmpFile.xml")
    return result
