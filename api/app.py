import os
import io
import json
from flask import Request, Response
from dotenv import load_dotenv
import google.generativeai as genai
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions

# Load environment variables
load_dotenv()

def transcribe(file_buffer, api_key):
    try:
        deepgram = DeepgramClient(api_key)
        payload = {"buffer": file_buffer}
        options = PrerecordedOptions(model="nova-2", smart_format=True)
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        json_file = response.to_json(indent=4)
        data = json.loads(json_file)
        question = data['results']['channels'][0]['alternatives'][0]['transcript']
        return generate_response_with_llm(question)
    except Exception as e:
        return {"error": str(e)}

def generate_response_with_llm(query):
    try:
        prompt_s = "Answer the question"
        prompt_e = f"\n\nQuestion: {query}\nAnswer:"
        full_prompt = prompt_s + prompt_e
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        response = llm_model.generate_content(full_prompt)
        return text_to_speech(response.text, os.getenv("DEEPGRAM_API_KEY"))
    except Exception as e:
        return {"error": str(e)}

def text_to_speech(text, api_key):
    try:
        deepgram = DeepgramClient(api_key=api_key)
        options = SpeakOptions(model="aura-asteria-en", encoding="linear16", container="wav")
        response = deepgram.speak.v("1").generate_audio(text, options)
        return response.audio
    except Exception as e:
        return {"error": str(e)}

def handler(request: Request):
    if request.method == 'POST':
        # Get the audio file from the request
        file = request.files['audio']
        audio_buffer = io.BytesIO(file.read())

        # Process the audio file
        deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        result = transcribe(audio_buffer, deepgram_api_key)

        if 'response' in result:
            generated_audio = result
            return Response(
                generated_audio,
                mimetype="audio/wav",
                headers={"Content-Disposition": "attachment;filename=outputspeech.wav"}
            )
        else:
            return {
                "statusCode": 500,
                "body": json.dumps(result)
            }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }
