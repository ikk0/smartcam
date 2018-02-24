Setup: AWS
==================

First of all, log into [AWS](https://console.aws.amazon.com/console/home), or create an AWS account if you don't have one yet.

The settings must be made in the "EU (Ireland)" region (or any other region that supports Alexa skills - but currently not too many regions support Alexa skills).

#### S3 Setup
* Go to [S3](https://s3.console.aws.amazon.com/s3/home)
* Set up a new bucket using a name such as "smartcam123", and remember this bucket name for later on. No special settings must be made, just create the bucket.

#### Lambda Setup
* Go to [Lambda](https://eu-west-1.console.aws.amazon.com/lambda/home)
* You will need to set up three lambda functions. The setup is almost the same for all three, just different function names + code is used for each lambda function.
* You will need to set up a role in IAM that has access to S3, CloudWatch, Rekognition, Lambda
* Now set up the three lambda functions (check out the code if you're interested, it's documented):
* Function 1 / Name "smartcamAlexa" / Runtime: Python 2.7 / Code: https://raw.githubusercontent.com/ikk0/smartcam/master/aws/lambda/smartcamAlexa.py
* Function 2 / Name "smartcamIdentifyPerson" / Runtime: Python 3.6 / Code: https://raw.githubusercontent.com/ikk0/smartcam/master/aws/lambda/smartcamIdentifyPerson.py
* Function 3 / Name "smartcamTagPerson" / Runtime: Python 3.6 / Code: https://raw.githubusercontent.com/ikk0/smartcam/master/aws/lambda/smartcamTagPerson.py
IMPORTANT: In each of the three functions, search for "smartcams3" (variable s3BucketName) and replace it with the bucket name you selected during S3 setup in the previous step.

### API Gateway Setup
* Go to [API Gateway](https://eu-west-1.console.aws.amazon.com/apigateway/home)
* Create a new API, give it any name. (A sample swagger schema can be seen [here](https://raw.githubusercontent.com/ikk0/smartcam/master/aws/api_gateway/swagger.json))
* Create two new resources: smartcamIdentifyPerson and smartcamTagPerson
* For each of the two resources, create two new methods. Type "ANY". 
* Configure them as "Lambda Function" and enable "Use Lambda Proxy integration"
* Select your Lambda region (previous setup, should be EU (Ireland) most likely) and enter the ARN of the two lambda functions you created, respectively matching the name.
* In the "Settings" tab of your API, in the "Binary Media Types" section enter "image/jpeg"
* Now go into the main API screen again and from the "Actions" dropdown select "Deploy API". Deploy to "production".
* Now go into the "Stages" section and select the prod API. Write down the "Invoke URL" , it will look something like this: https://w12312331.execute-api.eu-central-1.amazonaws.com/prod

#### CloudFront Setup
As Arduino does not properly support HTTPS connections, we must set up a "proxy" server that is available via HTTP and forwards requests to our HTTPS-only API Gateway endpoint.
* Go to [CloudFront](https://console.aws.amazon.com/cloudfront/home)
* Set up a new CloudFront distribution, with the settings described [here](https://stackoverflow.com/a/44901263/1320365).
* For the "Origin" field, enter the hostname you figured out as the "Invoke URL" in the last step of the previous "API Gateway" step, for example: w12312331.execute-api.eu-central-1.amazonaws.com
* Save the CloudFront Distribution and wait for it to be distributed. Via CloudFront, our API we created in API Gateway can be called from HTTP (from the Arduino) now
* Write down the hostname of the CloudFront distribution you created, for example: d123x23x23.cloudfront.net

#### Update Lambda Function, Arduino code
Now that we set up the CloudFront distribution, we must enter the URL to call our API into the Arduino code (so it can upload the image) as well as update the "smartcamAlexa" lambda function you created, so it can tag faces. 
* Open the [Arduino Code](https://github.com/ikk0/smartcam/blob/master/arduino/camera_sketch.ino) and look for:
response += "Host: d123x23x23.cloudfront.net\r\n";
Replace the hostname (d123x23x23.cloudfront.net) with the hostname of YOUR CloudFront distribution.
* Upload the sketch to your Arduino. Don't forget to update the IP settings, etc.
* Open the "smartcamAlexa" lambda function and look for:
lambdaUrl = 'http://d123123123v.cloudfront.net/prod/smartcamTagPerson'
Again, replace the hostname (d123x23x23.cloudfront.net) with the hostname of YOUR CloudFront distribution.
* Save the lambda function

#### AWS Rekognition Setup
Luckily, AWS Rekognition does not require any setup. ;-)

Now, proceed setting up the [Alexa Skill](https://github.com/ikk0/smartcam/blob/master/alexa_setup.md).
