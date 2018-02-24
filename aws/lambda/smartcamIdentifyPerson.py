### smartcamIdentifyPerson: Lambda function used to translate images/faces to names, using AWS Rekognition (Face recognition) and S3 (Temporary image storage). 
### This lambda function is triggered by the user via Alexa, via the lambda function called by Alexa (Lambda function "smartcamAlexa", EU-Ireland region)

# Imports
import os
import urllib
import boto3
import json
import base64
import botocore

# Variables
s3BucketName = 'smartcams3'
collectionId = '2' # Unique user ID or similar, so faces are stored separately. This allows separate cameras to be used at separate locations.

# API Clients
rekognition = boto3.client('rekognition', region_name='eu-west-1')
s3 = boto3.client('s3', region_name='eu-west-1')
s3Resource = boto3.resource('s3', region_name='eu-west-1')

# Lambda function
def lambda_handler(event, context):
    # Check if no image was sent, if so, return last response
    if not event.get('body', ''):
        obj = s3Resource.Object(s3BucketName, collectionId + '_response.txt')
        return response(obj.get()['Body'].read().decode('utf-8'))
        
    # The following line can be used to create a new collection in AWS rekognition (each "camera owner" has its own collection of faces)
    #rekognition.create_collection(CollectionId=collectionId)
    

    # Image is sent base64 encoded because of AWS API Gateway proxy behavior
    image_bytes = base64.b64decode(event['body'])
    # Upload image to S3 so it can be tagged later on
    s3.put_object(Body=image_bytes, Bucket=s3BucketName, Key=collectionId+'_last_image.jpg')
    try:
        # Call AWS Rekognition API and search for faces in image
        foundFaces = rekognition.search_faces_by_image(
            CollectionId = collectionId,
            Image={'Bytes': image_bytes},
            MaxFaces=1,
        )
    except rekognition.exceptions.InvalidParameterException as e:
        # Handle exceptions such as if no face was found
        exc = str(e)
        if "no faces" in exc:
            s3.put_object(Bucket=s3BucketName, Key=collectionId+'_response.txt', Body='NO_FACE')
            return response('NO_FACE')
        else:
            s3.put_object(Bucket=s3BucketName, Key=collectionId+'_response.txt', Body='UNKNOWN')
            return response('AWS API Error: ' + exc)
    
    # Let's see if any of the faces found has been tagged already. If so, return the name.
    if len(foundFaces['FaceMatches']) > 0:
        foundNames = ""
        for faceMatch in foundFaces['FaceMatches']:
            name = faceMatch['Face']['ExternalImageId']
            if not name:
                name = 'UNKNOWN'
            #foundNames += name + "," # Theoretically it is possible to identify multiple faces
            foundNames = name
        # Save names found so you can ask Alexa multiple times who rang the door
        s3.put_object(Bucket=s3BucketName, Key=collectionId+'_response.txt', Body=foundNames.strip(","))
        print(foundNames.strip(","))
        # Return name of person found
        return response("OK|"+foundNames.strip(","))
    else:
        # No faces on image have been tagged yet, return UNKNOWN
        foundNames = "UNKNOWN"
        s3.put_object(Bucket=s3BucketName, Key=collectionId+'_response.txt', Body=foundNames.strip(","))
        return response("OK|"+foundNames.strip(","))
        

# Helper function to return AWS API Gateway conform response
def response(body, status = 200):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": body
    }
