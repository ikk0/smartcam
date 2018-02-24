Setup: Alexa Skill
==================

* Log into [Alexa Developer Console](https://developer.amazon.com/edw/home.html#/)
* Click "Alexa Skills Kit"
* Add a new skill
* Tab "Skill Information"
* "Name": Smart Camera
* "Invocation Name": smart camera
* Click "Next"
* Tab "Interaction Model"
* "Intent Schema": [Download here, then paste into field](https://raw.githubusercontent.com/ikk0/smartcam/master/alexa/intent_schema.json)
* Click "Add Slot Type", name it "LIST_OF_NAMES" and paste the contents of the following [name file](https://raw.githubusercontent.com/ikk0/smartcam/master/alexa/list_of_names.txt) into the list. 
* "Sample Utterances": [Download here, then paste into field](https://github.com/ikk0/smartcam/blob/master/alexa/sample_utterances.txt)
* Click "Next"
* Tab "Configuration"
* "Service Endpoint Type": Select "AWS Lambda ARN" and enter the ARN of the "smartcamAlexa" Lambda function (created during the [AWS Setup Guide](https://github.com/ikk0/smartcam/blob/master/aws_setup.md)), it will look something like this: "arn:aws:lambda:eu-west-1:132456789798:function:smartcamAlexa". Don't change any of the other settings.
* Click "Next"
* Tab "Test"
* You can test the skill there, everything should work fine. For example, enter "Alexa, ask smart camera who rang the door?"
* Click "Next"
* Publishing Information / Privacy Settings can be made according to your requirements.
* Save the skill. You're set! Test it using your linked Alexa device, as a test skill you can immediately test it on your own account.
