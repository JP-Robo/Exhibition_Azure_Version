from gradio_client import Client
import os



def call_gradio_api(audio_path):
    client = Client("https://jen5000-speech-gradio.hf.space/--replicas/gd7mm/")
    result = client.predict(
            audio_path,	# str (filepath on your computer (or URL) of file) in 'Audio file' Audio component
            "transcribe",	# str  in 'Task' Radio component
            api_name="/predict"
    )
    print(result)
    return result

