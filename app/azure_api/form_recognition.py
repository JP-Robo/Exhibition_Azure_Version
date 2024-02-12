import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# TODO: is it usefull to change the models, for now I just added the prebuilt-receipt
def call_API_Receipt(img_path):

    key = os.environ["FORMULAR_KEY"]
    endpoint = os.environ["FORMULAR_ENDPOINT"]

    print("Keys exists")

    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with open(img_path, 'rb') as img:
      print("image could be opened")
      poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", img)

    return poller.result()


def get_receipt_info_str(img_path):
  try:
    result = call_API_Receipt(img_path)
    result = str(result.to_dict())
  except:
    result = "api call not working,..."
  return result
