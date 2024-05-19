import base64
import functions_framework

import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import urllib.request

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/chat.bot']



# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    request = base64.b64decode(cloud_event.data["message"]["data"])
    request_type = cloud_event.data["message"]["attributes"]["request_type"]
    uri=""
    mime_type=""
    uri1=""
    mime_type1=""
    uri2=""
    mime_type2=""
    if request_type == "File":
        uri = cloud_event.data["message"]["attributes"]["uri"]
        mime_type = cloud_event.data["message"]["attributes"]["mime_type"]
    if request_type =="Compare":
        uri1 = cloud_event.data["message"]["attributes"]["uri1"]
        mime_type1 = cloud_event.data["message"]["attributes"]["mime_type1"]
        uri2 = cloud_event.data["message"]["attributes"]["uri2"]
        mime_type2 = cloud_event.data["message"]["attributes"]["mime_type2"]

    space_name = cloud_event.data["message"]["attributes"]["spacename"]

    if request_type == "File":
        print(request)
        print(uri)
        print(mime_type)
        print(space_name)
    
        url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
        req = urllib.request.Request(url)
        req.add_header("Metadata-Flavor", "Google")
        current_project = urllib.request.urlopen(req).read().decode()

        print(current_project)

        vertexai.init(project=current_project, location="us-central1")

        video1 = Part.from_uri(mime_type=mime_type, uri=uri)

        print("Starting Execution")

        model = GenerativeModel("gemini-1.5-pro-preview-0409")
        responses = model.generate_content(
            [video1, ""f"{request}"""],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )

        print("Execution Complete")

        fileresponse = ''  
        for response in responses:
            print(response.text)
            fileresponse += response.text

        print(fileresponse)
    
        CREDENTIALS = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)

        response = {
                                        "actionResponse": {
                                            "type": "NEW_MESSAGE",
                                        },
                                        "text": f"{fileresponse}",
                                    }


        # Build a service endpoint for Chat API.
        chat = build('chat', 'v1', credentials=CREDENTIALS)
        chat.spaces().messages().create(
            parent=space_name,
            body=response).execute()
    
    if request_type == "Compare":
        url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
        req = urllib.request.Request(url)
        req.add_header("Metadata-Flavor", "Google")
        current_project = urllib.request.urlopen(req).read().decode()

        print(current_project)

        vertexai.init(project=current_project, location="us-central1")
        file1 = Part.from_uri(mime_type=mime_type1, uri=uri1)
        file2 = Part.from_uri(mime_type=mime_type2, uri=uri2)

        print("Starting Execution")

        model = GenerativeModel("gemini-1.5-pro-preview-0409")
        responses = model.generate_content(
            [file1,file2, ""f"{request}"""],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )

        print("Execution Complete")

        fileresponse = ''  
        for response in responses:
            print(response.text)
            fileresponse += response.text

        print(fileresponse)
    
        CREDENTIALS = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)

        response = {
                                        "actionResponse": {
                                            "type": "NEW_MESSAGE",
                                        },
                                        "text": f"{fileresponse}",
                                    }


        # Build a service endpoint for Chat API.
        chat = build('chat', 'v1', credentials=CREDENTIALS)
        chat.spaces().messages().create(
            parent=space_name,
            body=response).execute()





generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


