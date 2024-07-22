import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions

# Load environment variables
load_dotenv()

# Function to transcribe audio file
def transcribe(audio_file, api_key):
    try:
        # Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key)

        with open(audio_file, "rb") as file:
            buffer_data = file.read()

        payload = {
            "buffer": buffer_data,
        }

        # Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # Call the transcribe_file method
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        json_file = response.to_json(indent=4)

        data = json.loads(json_file)
        question = data['results']['channels'][0]['alternatives'][0]['transcript']
        generate_response_with_llm(question, api_key)

    except Exception as e:
        print(f"Exception: {e}")

# Function to convert text to speech
def text_to_speech(text, api_key, output_file):
    try:
        # Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key=api_key)

        # Configure the options
        options = SpeakOptions(
            model="aura-asteria-en",
            encoding="linear16",
            container="wav"
        )

        # Call the save method on the speak property
        response = deepgram.speak.v("1").save(output_file, {"text": text}, options)

    except Exception as e:
        print(f"Exception: {e}")

# Function to generate a response with LLM
def generate_response_with_llm(query, api_key):
    try:
        prompt_s = "Answer the question"
        prompt_e = f"\n\nQuestion: {query}\nAnswer:"
        full_prompt = prompt_s + prompt_e

        # Configure the LLM
        genai.configure(api_key="AIzaSyD5bAMQtc4AdjMu17qLk2uoesl35p2-QoU")
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        response = llm_model.generate_content(full_prompt)
        text_to_speech(response.text, api_key, 'outputspeech.wav')

    except Exception as e:
        print(f"Exception: {e}")

# Main execution logic
if __name__ == "__main__":
    audio_file = 'output.wav'
    api_key = "b70621f540af91d45e0722ae36aaa50938d296df"
    transcribe(audio_file, api_key)