import requests
import time
from api_secrets import API_KEY_ASSEMBLYAI

# Define the upload endpoint URL for AssemblyAI
upload_endpoint = 'https://api.assemblyai.com/v2/upload'

# Define the transcript endpoint URL for AssemblyAI
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

# Create headers with authorization only using the API key
headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

# Create headers with authorization and content-type set to application/json
headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

# Define the chunk size for file upload (5MB)
CHUNK_SIZE = 5_242_880  # 5MB


def upload(filename):
    """
    Upload a file to AssemblyAI and return the upload URL.

    Args:
        filename (str): The name of the file to upload.

    Returns:
        str: The upload URL.
    """
    def read_file(filename):
        """
        Read a file in chunks and yield the data.

        Args:
            filename (str): The name of the file to read.

        Yields:
            bytes: The chunk of data read from the file.
        """
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    # Upload the file to AssemblyAI and get the upload response
    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    # Return the upload URL from the response
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    """
    Transcribe an audio file using AssemblyAI and return the transcript ID.

    Args:
        audio_url (str): The URL of the audio file to transcribe.

    Returns:
        str: The transcript ID.
    """
    # Create a transcript request with the audio URL
    transcript_request = {
        'audio_url': audio_url
    }

    # Post the transcript request to AssemblyAI and get the response
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    # Return the transcript ID from the response
    return transcript_response.json()['id']


def poll(transcript_id):
    """
    Poll AssemblyAI for the transcript status and return the response.

    Args:
        transcript_id (str): The ID of the transcript to poll.

    Returns:
        dict: The transcript status response.
    """
    # Create the polling endpoint URL
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    # Get the polling response from AssemblyAI
    polling_response = requests.get(polling_endpoint, headers=headers)
    # Return the polling response
    return polling_response.json()


def get_transcription_result_url(url):
    """
    Transcribe an audio file and poll for the result until it's completed or failed.

    Args:
        url (str): The URL of the audio file to transcribe.

    Returns:
        tuple: A tuple containing the transcript data and error (if any).
    """
    # Transcribe the audio file and get the transcript ID
    transcribe_id = transcribe(url)
    while True:
        # Poll AssemblyAI for the transcript status
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            # Return the transcript data if completed
            return data, None
        elif data['status'] == 'error':
            # Return the error if failed
            return data, data['error']
        
        # Wait for 30 seconds before polling again
        print("waiting for 30 seconds")
        time.sleep(30)


def save_transcript(url, title):
    """
    Transcribe an audio file and save the transcript to a file.

    Args:
        url (str): The URL of the audio file to transcribe.
        title (str): The title of the transcript file.

    Returns:
        None
    """
    # Get the transcript data and error (if any)
    data, error = get_transcription_result_url(url)
    
    if data:
        # Save the transcript to a file
        filename = title + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])
        print('Transcript saved')
    elif error:
        # Print the error if failed
        print("Error!!!", error)