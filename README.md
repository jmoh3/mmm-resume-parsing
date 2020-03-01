# mmm-resume-parsing
Uses resume data to match students to topics that are most relevant for them, created for [ACM Member-to-Meeting Matcher (MMM)](https://github.com/acm-uiuc/mmm).

## Deploy

Before deploying, you'll need to set up an AWS account and credentials.

In order to deploy the you endpoint simply run

```bash
serverless deploy
```

The expected result should be similar to:

```bash
Serverless: Packaging service...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading service .zip file to S3 (758 B)...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
..........
Serverless: Stack update finished...

Service Information
service: resume-api
stage: dev
region: us-east-1
api keys:
  None
endpoints:
  POST - https://f7r5srabr3.execute-api.us-east-1.amazonaws.com/dev/
functions:
  parse_resume: resume-api-dev-parse_resume
 layers:
  None
 ```
