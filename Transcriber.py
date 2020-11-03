#!/usr/bin/python

from pprint import pprint
import os
import ntpath
import sys
import json
import speech_recognition as sr

print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))
location = os.path.dirname(os.path.abspath(__file__))
sound_string = sys.argv[1]
sound_location = sound_string
sound_name = ntpath.basename(sound_string)
out_location = os.path.dirname(sound_string)

print('Sound name', sound_name)

r = sr.Recognizer()
harvard = sr.AudioFile(sound_location)
with harvard as source:
    audio = r.record(source)

# recognize speech using Google Cloud Speech
g_cloud_json = open('{path}/Assets/ninth-archway-293722-0ebb76c3ed3e.json'.format(path=location))
GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(g_cloud_json))

try:
    print("Google Cloud Speech recognition results:")
    out = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)  # pretty-print the recognition result
    # out = r.recognize_google(audio)
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))

pprint(out)

file_out = open('{path}/{name}.rtf'.format(name=sound_name, path=out_location), 'w')
file_out.write(out)
file_out.close()
