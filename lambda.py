import os

from xml_handler import *


def lambda_handler(event, context):

    # content = event["Records"][0]["Sns"]["RequestData"]
    content = "<workflows><workflow><name>John</name></workflow><metadata><value>Test_1</value></metadata></workflows>"
    with open("/tmp/tmpFile.xml", "w") as file:
        file.write(content)
    with open("/tmp/tmpFile.xml", "r"):
        workflows = {"workflow": handler("workflow", "./test_input.xml")}
        result = [workflows]
    os.system("rm /tmp/tmpFile.xml")
    return result

if __name__ == '__main__':
    print(lambda_handler("", ""))
