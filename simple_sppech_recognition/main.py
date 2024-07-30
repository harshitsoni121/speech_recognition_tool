import requests
from api_02 import *

# The filename of the audio file to be uploaded and processed
filename = "a1.wav"

# Upload the audio file to the server and get the URL of the uploaded file
# using the 'upload' function from the 'api_02' module
audio_url = upload(filename)

# Save the transcript of the audio file, using the provided 'file_title' as the name
# by calling the 'save_transcript' function with 'audio_url' and 'file_title' as arguments
save_transcript(audio_url, 'file_title')