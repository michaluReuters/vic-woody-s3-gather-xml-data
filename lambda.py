import os

from xml_handler import *


def lambda_handler(event, context):

    content = event["Records"][0]["Sns"]["RequestData"]
    with open("/tmp/tmpFile.xml", "w") as file:
        file.write(content)
    with open("/tmp/tmpFile.xml", "r"):
        workflows = {"sources": handler("sources", "/tmp/tmpFile.xml")}
        result = [workflows]
    os.system("rm /tmp/tmpFile.xml")
    return result
