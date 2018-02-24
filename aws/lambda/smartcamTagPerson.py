### smartcamTagPerson: Lambda function used to assign a name to a previously identified face, using AWS Rekognition (face tagging) and S3 (Retrieve last picture taken)
### This lambda function is triggered by the user via Alexa, via the lambda function called by Alexa (Lambda function "smartcamAlexa", EU-Ireland region)

# Imports
import os
import urllib
import boto3
import json

# Variables
s3BucketName = 'smartcams3'
collectionId = '2' # Unique user ID or similar, so faces are stored separately. This allows separate cameras to be used at separate locations.

# API Clients
rekognition = boto3.client('rekognition', region_name='eu-west-1')
s3 = boto3.client('s3', region_name='eu-west-1')

# Lambda function
def lambda_handler(event, context):
    # Name of person to assign to the last face found, sent to the lambda function via POST data
    nameOfPerson = urllib.parse.unquote_plus(event['body'])

    try:
        # Call AWS Rekognition API and assign name to faces using ExternalImageId. Picture has been uploaded to S3 by "smartcamIdentifyPerson" lambda function before.
        rekognition.index_faces(
            CollectionId = collectionId,
            Image={
    			"S3Object": {
    				"Bucket": s3BucketName,
    				"Name": collectionId+'_last_image.jpg',
    			}
    		},
            ExternalImageId=nameOfPerson
        )
    except rekognition.exceptions.InvalidS3ObjectException:
        return response('NO_IMAGE_FOUND')
    except rekognition.exceptions.InvalidParameterException as e:
        # Handle exceptions such as if no face was found
        exc = str(e)
        if exc.find("no faces") == -1:
            return response('NO_FACE')
        else:
            return response('AWS API Error: ' + exc)
    
    # Delete image from S3
    s3.delete_object(Bucket=s3BucketName, Key=collectionId+'_last_image.jpg')
    
    # Save name found in S3
    s3.put_object(Bucket=s3BucketName, Key=collectionId+'_response.txt', Body=nameOfPerson)
    
    # Return response confirming tag/name
    return response('OK: '+nameOfPerson)

# Helper function to return AWS API Gateway conform response
def response(body, status = 200):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": body
    }    
