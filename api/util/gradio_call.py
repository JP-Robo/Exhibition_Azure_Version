from gradio_client import Client
import os
# to start and stop a space: 
# https://huggingface.co/docs/huggingface_hub/main/en/guides/manage-spaces
# api.pause_space(repo_id=repo_id)
# api.restart_space(repo_id=repo_id)

# def call_gradio_api(audio_path):
#       client = Client("harishrb/Translate-To-Spanish", hf_token=os.environ["HF_token"])
#       result = client.predict("Hello there, I miss u")

def call_gradio_api(audio_path):
    client = Client("https://jen5000-speech-gradio.hf.space/--replicas/gd7mm/")
    result = client.predict(
            audio_path,	# str (filepath on your computer (or URL) of file) in 'Audio file' Audio component
            "transcribe",	# str  in 'Task' Radio component
            api_name="/predict"
    )
    print(result)
    return result

