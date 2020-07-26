# Dome9 Serverless onboarding Automation of AWS Accounts 
### This solution automatically enables "serverless" feature across multiple onboarded Dome9 accounts

The script probes all AWS accounts that have already been onboarded into Dome9 and checks whether "serverless" feature is enabled or not.   
Accounts that aren't enabled, are being proceccesed and enabled one by one.
The script is using AWS credentials of the root account of "AWS organization" and onboards each sub account in the organization by assuming the default role "OrganizationAccountAccessRole" in each such subaccount and by running a CFT stack that creates the necassery roles and access policies for Dome9 to monitor "serverless" inside the account. The script was built to prompt for AWS credentials (i.e. Access Key and Secret) if it fails to do so with the pre-loaded ones. This is also adequate for situations where you are oboarding multiple accounts with different Root acount credentials.


# Requirements  
Dome9 V2 API Credentials  
Cross-Account role in each sub account to be enabled with the following permissions policy 
******************************************************************************************************************************
{  
    "Version": "2012-10-17",  
    "Statement": [  
        {  
            "Sid": "onboarding1",  
            "Effect": "Allow",  
            "Action": [  
                "iam:GetRole*",  
                "iam:PassRole",  
                "iam:ListRole*",  
                "iam:CreateRole",  
                "iam:CreatePolicy",  
                "iam:ListPolicies",  
                "iam:PutRolePolicy",  
                "iam:AttachRolePolicy",  
                "iam:DeleteRolePolicy",  
                "lambda:GetFunction",  
                "lambda:CreateFunction",  
                "lambda:GetLayerVersion",  
                "lambda:GetFunctionConfiguration",  
                "logs:CreateLogGroup",  
                "logs:DescribeLogGroups",  
                "logs:PutRetentionPolicy",  
                "cloudformation:List*",  
                "cloudformation:Create*",  
                "cloudformation:Describe*",  
                "s3:GetObject",  
                "s3:CreateBucket",  
                "s3:DeleteBucket",  
                "s3:PutEncryptionConfiguration"  
            ],  
            "Resource": "*"  
        },  
        {  
            "Sid": "onboarding2",  
            "Effect": "Allow",  
            "Action": "sns:Publish",  
            "Resource": "arn:aws:sns:*:*:*"  
        }  
    ]  
}  
**************************************************************************************************************
Python v3.8 or later  
git  2.17 or later  
aws cli version 2 or later  
python 3.8 with the following packages  
  - pip  
  - boto3  
  - botocore  
  - requests  
  - argparse  

### Assumptions
The following assumptions are made about the environment to be successful running the script.

AWS Organizations Onboarding
Any account in AWS Organizations has a cross-account access role in the child account with a consistent name (e.g. the default "OrganizationAccountAccessRole"). The parent account will assume the role in the child account. Not having a consistent role name will require running the script multiple times.  

### Cross-account Onboarding
Setup
Step 1: Clone the repo and Install Dependencies
Clone this repo into your local environment:
git clone https://github.com/amit-schnitzer/dome9-serverless-onboarding.git
Navigate to the script subdirectory:
cd dome9-serverless-onboarding
Using PIP, install the following python dependencies:
boto3
botocore
requests
# Install python dependencies
pip3 install boto3 requests #Run as 'sudo' if you receive errors.
Step 3: Setup Dome9 Environment Variables
Create your Dome9 V2 API Credentials here.
Set the environment variables.
# Dome9 V2 API Credentials Example
export d9id=12345678-1234-1234-1234-123456789012
export d9secret=abcdefghijklmnopqrstuvwx
Step 4: Setup AWS Credentials for Parent AWS Account
Get IAM Credentials
Option 1: Run the script on an AWS resource which uses a service-linked role. The script will dynamically find the credentials without the need to specify environment variables.
Option 2: Create IAM User access keys and set the environment variables.
  # AWS Credentials Example
  export AWS_ACCESS_KEY_ID=AK00012300012300TEST
  export AWS_SECRET_ACCESS_KEY=Nnnnn12345nnNnn67890nnNnn12345nnNnn67890
Attach the following IAM Policy to the service-linked role or IAM user that you created.
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "D9FULLAUTOMATIONPARENT",
            "Effect": "Allow",
            "Action": [
                "sts:*",
                "organizations:Describe*",
                "organizations:List*"
            ],
            "Resource": "*"
        }
    ]
}
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
