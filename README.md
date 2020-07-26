# Dome9 Serverless onboarding Automation of AWS Accounts 
### This solution automatically enables "serverless" feature across multiple onboarded Dome9 accounts

The script probes all AWS accounts that have already been onboarded into Dome9 and checks whether "serverless" feature is enabled or not.   
Accounts that aren't enabled, are being proceccesed and enabled one by one.
The script is using AWS credentials of the root account of "AWS organization" and onboards each sub account in the organization by assuming the default role "OrganizationAccountAccessRole" in each such subaccount and by running a CFT stack that creates the necassery roles and access policies for Dome9 to monitor "serverless" inside the account. The script was built to prompt for AWS credentials (i.e. Access Key and Secret) if it fails to do so with the pre-loaded ones. This is also adequate for situations where you are oboarding multiple accounts with different Root acount credentials.


# Requirements  
Dome9 V2 API Credentials  
Cross-Account role in each sub account with proper permissions (onboarding-policy.json file includes minimum permissions policy)  
Python v3.8 or later with the following  
  - pip  
  - boto3  
  - botocore  
  - requests  
  - argparse  
git  2.17 or later  
aws cli version 2 or later  

### Assumptions
The following assumptions are made about the environment to be successful running the script.  
AWS accounts have been already onboarded into Dome9 - either manually or using [Onboarding-Scripts](https://github.com/dome9/onboarding-scripts)  
Any sub account in AWS Organizations has a cross-account access role in the child account with a consistent name (e.g. the default "OrganizationAccountAccessRole"). The parent account will assume the role in the child account. Not having a consistent role name will require running the script multiple times.  

### Setup  
#### Step 1: Clone the repo   
Clone this repo into your local environment:  
git clone https://github.com/amit-schnitzer/dome9-serverless-onboarding.git  
Navigate to the script subdirectory:  
cd dome9-serverless-onboarding  

#### Step 2: Create and export Dome9 API Credentials  
Generate a Dome9 API token [here](https://secure.dome9.com/v2/settings/credentials)  
Add your token to environment variable  
    export d9id=12345678-1234-1234-1234-123456789012
    export d9secret=abcdefghijklmnopqrstuvwx
#### Step 3: AWS Credentials  
  export AWS_ACCESS_KEY_ID=AK00012300012300TEST  
  export AWS_SECRET_ACCESS_KEY=Nnnnn12345nnNnn67890nnNnn12345nnNnn67890  
Attach the following IAM Policy to the service-linked role or IAM user that you created.

'''

    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:ListPolicies",
                "lambda:CreateFunction",
                "iam:ListRole*",
                "cloudformation:Create*",
                "logs:DescribeLogGroups",
                "lambda:GetLayerVersion",
                "lambda:GetFunction",
                "iam:CreateRole",
                "s3:CreateBucket",
                "iam:AttachRolePolicy",
                "lambda:GetFunctionConfiguration",
                "iam:PutRolePolicy",
                "logs:CreateLogGroup",
                "cloudformation:Describe*",
                "iam:CreatePolicy",
                "s3:PutEncryptionConfiguration",
                "s3:GetObject",
                "iam:PassRole",
                "iam:DeleteRolePolicy",
                "cloudformation:List*",
                "logs:PutRetentionPolicy",
                "s3:DeleteBucket",
                "iam:GetRole*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:*:*:*"
        }
    ]
}
'''

Note: If you would like the parent AWS account to be onboarded in Dome9 by the script you will need to also attach the same IAM policy as the child accounts, as seen in the Assumptions section above.

Operation
To run the script, review the run modes of the script and the arguments for each mode.

Run Modes
The first argument in the command string determines the run mode of the script. Below is a list of the available run modes. Syntax: python d9_onboard_aws.py <mode> [options]

Run Mode	Description
local	Onboard the AWS account running the script only
crossaccount	Onboard an AWS account using Assume-Role
organizations	Onboard parent and child accounts and attach them to Dome9 organizational units mapped from AWS Organizations metadata
Global and Mode-specific Arguments
Below are the global and mode-specific arguments.

Global Global arguments are required for all run modes.

Argument	Description	Default value
--region	AWS Region Name for Dome9 CFT deployment.	us-east-1
--d9mode	readonly/readwrite: Dome9 mode to onboard AWS account as.	readonly
Note: If global arguments are missing, the script will assume default values.

Local Mode

Argument	Description	Example value
--name	Cloud account friendly name in quotes (required)	"AWS PROD"
Crossaccount Mode

Argument	Description	Example value
--account	Cloud account number (required)	987654321012
--name	Cloud account friendly name in quotes (required)	"AWS PROD"
--role	AWS cross-account access role for Assume-Role (required)	MyRoleName
Organizations Mode

Argument	Description	Example value
--role	AWS cross-account access role for Assume-Role (required)	MyRoleName
--ignore-ou	Ignore AWS Organizations OUs and place accounts in root.	
--ignore-failures	Ignore onboarding failures and continue.
