import requests
import os


def whisper_transcribe(filename):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": "Bearer " + os.environ["HF_token"]}
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

# output = whisper_transcribe("sample1.flac")