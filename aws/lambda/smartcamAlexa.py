# Lambda function to handle incoming requests by the Alexa Skill Kit
# This function uses the two other lambda functions "smartcamIdentifyPerson" (to ask who rang the door) and "smartcamTagPerson" (to tell the system who rang the door, and store the association for this face)
# Alexa Skill Kit Documentation, this code is based on this sample: https://developer.amazon.com/de/docs/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html

# Imports
from __future__ import print_function
from botocore.vendored import requests
import boto3
import botocore

# Variables
s3BucketName = 'smartcams3'
collectionId = '2' # Unique user ID or similar, so faces are stored separately. This allows separate cameras to be used at separate locations.


# Helpers that build all of the responses
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# Functions that control the skill's behavior

# Welcome response: If the skill is called without an action, tell user the possible actions.
def get_welcome_response(locale):
    if locale == 'en-US':
        card_title = "Welcome"
        speech_output = "Ask me who rang the door or tell me who rang the door. I'm always learning."
        reprompt_text = "For example, say: Alexa, ask smart camera who rang the door?"
    if locale == 'de-DE':
        card_title = "Willkommen"
        speech_output = "Frage mich wer geklingelt hat oder sag mir nach dem Klingeln wer geklingelt hat. Ich lerne mit."
        reprompt_text = "Sage zum Beispiel: Alexa, frage schlaue Kamera wer geklingelt hat?"
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# Session has ended (stop or cancel intent), say goodbye
def handle_session_end_request(locale):
    if locale == 'en-US':
        card_title = "Session Ended"
        speech_output = "Thank you for using the smart camera."
    if locale == 'de-DE':    
        card_title = "Session Ended"
        speech_output = "Vielen Dank, dass du die schlaue Klingel benutzt hast."

    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

# Function used to tag the person who rang the door, i.e. give the face a name
def tag_person(intent, session, locale):
    if 'NameOfPerson' in intent['slots']:
        # Only if a name was supplied by the user, do: 
        NameOfPerson = intent['slots']['NameOfPerson']['value']
        # Send request with name of person to smartcamTagPerson lambda function which will save the name of the person for the last face
        result = requests.post('http://d35xafoveji7v.cloudfront.net/prod/smartcamTagPerson', data=NameOfPerson)
        
        # Build Alexa response
        reprompt_text = ""
        
        if 'NO_IMAGE_FOUND' in str(result.text):
            if locale == 'en-US':
                speech_output = "No image was uploaded by the camera."
            if locale == 'de-DE':
                speech_output = "Es wurde kein Bild von der Kamera hochgeladen."
        elif 'NO_FACE' in str(result.text):
            if locale == 'en-US':
                speech_output = "No face was found on the uploaded image."
            if locale == 'de-DE':
                speech_output = "Es wurde kein Gesicht im hochgeladenen Bild gefunden."
        else:            
            if locale == 'en-US':
                speech_output = "Thank you. I will remember that " + NameOfPerson + " rang the door."
            if locale == 'de-DE':    
                speech_output = "Danke. Ich weiss jetzt, dass " + NameOfPerson + " geklingelt hat."
        
    else:
        # No name supplied, return Alexa response
        if locale == 'en-US':
            speech_output = "I did not understand you. Try again."
            reprompt_text = "Example: Alexa, tell smart camera that Peter rang the door."
        if locale == 'de-DE':    
            speech_output = "Ich habe dich leider nicht verstanden. Bitte probier es nochmal."
            reprompt_text = "Sag zum Beispiel: Alexa, sage schlaue Kamera dass Peter geklingelt hat."

    should_end_session = True
    return build_response({}, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))

# Function used to get the name of the person who rang the door, so you can ask Alexa who rang the door
def get_last_person(intent, session, locale):
    # Initialize S3 client to get name, stored in a file, identified by lambda function smartcamIdentifyPerson/smartcamTagPerson
    s3Resource = boto3.resource('s3', region_name='eu-west-1')
    NameOfPerson = ''
    try: 
        obj = s3Resource.Object(s3BucketName, str(collectionId)+'_response.txt')
        NameOfPerson = obj.get()['Body'].read()
    except Exception, e:
        #NameOfPerson = str(e)
        pass

    if NameOfPerson and NameOfPerson == 'NO_FACE':
        if locale == 'en-US':
            speech_output = 'The camera could not detect any face.'
        if locale == 'de-DE':
            speech_output = 'Die Kamera konnte kein Gesicht erkennen.'
    elif NameOfPerson and NameOfPerson != 'UNKNOWN':
        if locale == 'en-US':
            speech_output = NameOfPerson + ' rang the door.'
        if locale == 'de-DE':
            speech_output = NameOfPerson + ' hat geklingelt.'
    else:
        if locale == 'en-US':
            speech_output = "I did not recognize this person. Please tell me who rang the door. For example, say: Alexa, tell smart camera that the person is Peter."
        if locale == 'de-DE':
            speech_output = "Ich habe die Person leider nicht erkannt. Sage mir bitte wer geklingelt hat. Sage dazu zum Beispiel: Alexa, sage Kamera dass Peter geklingelt hat."
        
    should_end_session = True
    return build_response({}, build_speechlet_response(intent['name'], speech_output, None, should_end_session))

# --------------- Events ------------------
def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return get_welcome_response(launch_request['locale'])

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    locale = intent_request['locale']

    # Dispatch to skill's intent handlers
    if intent_name == "TagPersonIntent":
        return tag_person(intent, session, locale)
    elif intent_name == "WhoRangAtTheDoorIntent":
        return get_last_person(intent, session, locale)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(locale)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request(locale)
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session. Is not called when the skill returns should_end_session=true """
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

# Lambda function, main handler
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter. """
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
        
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
