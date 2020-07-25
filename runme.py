import requests
import json
import os
import argparse
import boto3
import botocore

role_name = "OrganizationAccountAccessRole"
apiKey = os.environ["d9id"]
apiSecret = os.environ["d9secret"]

headers = {
  'Accept': 'application/json'
}
r = requests.get('https://api.dome9.com/v2/CloudAccounts', params={

}, headers = headers, auth=(apiKey, apiSecret))
accounts = r.json()
keys = []
key = ""
secret = ""
for account in accounts:
    if account["serverlessEnabled"] == False:
        print(account)
        sts_client = boto3.client('sts')
        flag = False
        assumed_role_object = {}
        i = 0
        while not flag:
            try:
                assumed_role_object=sts_client.assume_role(
                RoleArn="arn:aws:iam::%s:role/%s"%(account["externalAccountNumber"], role_name),
                RoleSessionName="AssumeRoleSession" + account["externalAccountNumber"]
                )
                flag = True
            except botocore.exceptions.ClientError:
                try:
                    sts_client = session.client('sts', region_name="us-east-1", aws_access_key_id = key, aws_secret_access_key = secret)
                    aws_account = sts_client.get_caller_identity().get('Account')
                    if aws_account == account["externalAccountNumber"]:
                        os.system("python3 onboarding_d9.py -i %s -j %s -c %s -k %s -s %s -b https://api.dome9.com/v2"%(creds["AccessKeyId"], creds["SecretAccessKey"], account["id"], apiKey, apiSecret))
                        break
                except:
                    pass
                if i >= (len(keys) - 1):
                    print("couldn't assume role into this subaccount please specify valid credentials to organization of this subaccount or of this subaccount")
                    key = str(input("amazon api key: "))
                    secret = str(input("amazon api secret: "))
                    keys.append({"key": key, "secret": secret})
                    sts_client = boto3.client('sts', aws_access_key_id = key, aws_secret_access_key = secret)
                else:
                    sts_client = boto3.client('sts', aws_access_key_id = keys[i]["key"], aws_secret_access_key = keys[i]["secret"])
                    i += 1
        creds = assumed_role_object['Credentials']
        os.system("python3 onboarding_d9.py -i %s -j %s -t %s -c %s -k %s -s %s -b https://api.dome9.com/v2"%(creds["AccessKeyId"], creds["SecretAccessKey"], creds["SessionToken"], account["id"], apiKey, apiSecret))
