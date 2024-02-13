from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
# # from IPhython.display import Image
import os


def call_API_Captions(img_path):

    cred = CognitiveServicesCredentials(os.environ["VISIONS_KEY"])
    client = ComputerVisionClient(endpoint=os.environ["VISION_ENDPOINT"], credentials=cred)

    with open(img_path, "rb") as img:
        # TODO: check out other options
        result = client.describe_image_in_stream(img).as_dict()

    return result
