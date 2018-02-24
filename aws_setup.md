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

### API Gateway Setup

#### CloudFront Setup
As Arduino does not properly support HTTPS connections, we must set up a "proxy" server that is available via HTTP and forwards requests to our HTTPS-only lambda endpoint.
* Go to [CloudFront](https://console.aws.amazon.com/cloudfront/home)
* 

#### AWS Rekognition Setup
Luckily, AWS Rekognition does not require any setup. ;-)
