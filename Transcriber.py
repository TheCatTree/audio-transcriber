#!/usr/bin/python

import os
import ntpath
import sys
import json
import concurrent.futures
import speech_recognition as sr
from pprint import pprint
from pydub import AudioSegment
from pydub.utils import make_chunks
from os import path

print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))
location = os.path.dirname(os.path.abspath(__file__))
sound_string = sys.argv[1]
sound_location = sound_string
sound_name = ntpath.basename(sound_string)
out_location = os.path.dirname(sound_string)

print('Sound name', sound_name)
r = sr.Recognizer()

# Test for mp3
name, extension = os.path.splitext(sound_name)
print('File extension:', extension )

if extension.lower() == ".mp3":
    print("Changing MP3 to Wav.")
    temp_sound = AudioSegment.from_mp3(sound_location)
    temp_out = '{path}/temp/temp_mptowav.wav'.format(path=location)
    temp_sound.export(temp_out, format="wav")
    sound_location = temp_out

# Brake audio, into 40 second chunks.
temp_sound = AudioSegment.from_file(sound_location, format="wav")
chunks =  make_chunks(temp_sound,40000)
print("Number of Chunks",len(chunks))

# Export chunks
for i, chunk in enumerate(chunks):
    chunk_name = "chunk{0}.wav".format(i)
    print ("exporting", chunk_name)
    chunk.export("{path}/temp/{name}".format(path=location,name=chunk_name), format="wav")



def transcribe(chunk_id):
    harvard = sr.AudioFile("{path}/temp/chunk{number}.wav".format(path=location,number=chunk_id))
    with harvard as source:
        audio = r.record(source)

    # recognize speech using Google Cloud Speech
    g_cloud_json = open('{path}/credentials/googlecloud.json'.format(path=location))
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(g_cloud_json))

    try:
        out = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)  # pretty-print the recognition result
        pprint("Google Cloud Speech recognition results chunk {0}:".format(chunk_id))
        pprint("Chunk:{0} {1}".format(chunk_id, out))
        # out = r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))

    
    
    return {
        "idx": chunk_id,
        "text": out
    }

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    all_text  = executor.map(transcribe, range(len(chunks)))

transcript = ""
for text in sorted(all_text, key=lambda  x:  x['idx']):
    transcript = transcript + "{0}".format(text)

with open('{path}/{name}.rtf'.format(name=sound_name, path=out_location), 'w') as file_out: 
    file_out.write(transcript)

