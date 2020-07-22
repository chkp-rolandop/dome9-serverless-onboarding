import requests
import json
import boto3
import botocore
import argparse
import sys
from urllib.parse import unquote

DEFAULT_REGION = "us-east-1"
ADD_ACCOUNT_API = "/serverless/accounts"
ACCOUNT_TRUST_API = "/AccountTrust/assumable-roles"


def load_config(config_file):
    with open(config_file, "r") as data_file:
        conf = json.loads(data_file.read())
    return conf


def safe_loads(content):
    try:
        return json.loads(content)
    except:
        raise Exception("Failed to parse response")


def is_account_trust(base_url, api_key, api_secret):
    headers = {
        'Accept': 'application/json'
    }
    url = base_url + ACCOUNT_TRUST_API
    try:
        response = requests.request("GET", url, headers=headers, auth=(api_key, api_secret))
        print("Validate account status code: {} ".format(response.status_code))
        if response.status_code != 200:
            return False
        return True
    except:
        print("Account validation failed, please make sure you using a valid base-url and try again...")
        exit(1)


def add_account(base_url, cloud_account_id, api_key, api_secret):
    payload = {'cloudAccountId': cloud_account_id}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    url = base_url + ADD_ACCOUNT_API
    response = requests.request("POST", url, headers=headers, auth=(api_key, api_secret), json=payload)
    print("Add account status code: {} ".format(response.status_code))
    if response.status_code != 201:
        raise Exception("Failed to add_account, content: {}".format(str(response.content)))
    content = safe_loads(response.content)
    # account already connected to serverless
    if content['crossAccountRoleTemplateURL'] is None:
        print(content['reason'])
        exit(0)
    return content['crossAccountRoleTemplateURL']


def get_cross_account_template(cross_account_url):
    try:
        cross_account_template = cross_account_url.split("templateURL=")[1]
    except:
        raise Exception("Failed to get cross account template")
    return unquote(cross_account_template)


def create_cross_account_stack(cf_client, stack_name, template_url):
    cf_client.create_stack(StackName=stack_name, TemplateURL=template_url, Capabilities=["CAPABILITY_NAMED_IAM"])
    return


def wait_for_created_stack(cf_client, stack_name):
    waiter = cf_client.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_name)
    return


def onboarding(base_url, cf_client, aws_account, cloud_account_id, api_key, api_secret):
    # 1. create account and get cross account template
    print("Start add account " + cloud_account_id + " ...")
    cross_account_url = add_account(base_url, cloud_account_id, api_key, api_secret)
    cross_account_template = get_cross_account_template(cross_account_url)

    # 2. create cross account stack
    stack_name = "ProtegoAccount-Dome9Serverless-" + aws_account
    flag = False
    while not flag:
        try:
            create_cross_account_stack(cf_client, stack_name, cross_account_template)
            flag = True
        except botocore.exceptions.ClientError:
            print("there aren't any permissions to create the cloudformation:")
            print("enter 1 to try again")
            print("enter 2 to enter specific credentials for the subaccount")
            print("enter 3 to skip this subaccount")
            num = str(input())
            if num == "2":
                key = str(input("amazon api key: "))
                secret = str(input("amazon api secret: "))
                cf_client = session.client('cloudformation', region_name="us-east-1", aws_access_key_id = key, aws_secret_access_key = secret)
            elif num == "3":
                sys.exit()


    # 3. wait for created stack
    print("Create cross account stack in progress- this may take a few minutes, please wait...")
    wait_for_created_stack(cf_client, stack_name)
    print("Stack created successfully!")

    headers = {
      'Accept': 'application/json'
    }
    r = requests.get('https://api.dome9.com/v2/serverless/accounts/' + cloud_account_id, params={}, headers = headers, auth=(api_key, api_secret))

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(
        description="Onboarding script"
    )

    parser.add_argument("-c", "--cloud_account_id", required=True, help="The D9 cloud account_id")
    parser.add_argument("-p", "--profile", default=None, required=False, help="The AWS Profile")
    parser.add_argument("-k", "--api_key", required=True, help="The D9 API key")
    parser.add_argument("-s", "--api_secret", required=True, help="The D9 API secret key")
    parser.add_argument("-b", "--base_url", required=True, help="Dome9 base URL")
    parser.add_argument("-r", "--region", default=DEFAULT_REGION, required=False, help="The AWS region")
    parser.add_argument("-i", "--amazon_api_key", required=True, help="Amazon Sub account role key")
    parser.add_argument("-j", "--amazon_api_secret", required=True, help="Amazon Sub account role secret")
    parser.add_argument("-t", "--amazon_token", required=False, help="Amazon Sub account role token")

    parser.set_defaults(conf=load_config)
    args = parser.parse_args()

    profile = None if args.profile == "None" else args.profile
    region = None if args.region == "None" else args.region
    amazon_token = None if args.amazon_token == "None" else args.amazon_token
    cloud_account_id = args.cloud_account_id
    base_url = args.base_url.rstrip('/')
    api_key = args.api_key
    api_secret = args.api_secret

    if is_account_trust(base_url, api_key, api_secret):
        print("Account validation success!")
    else:
        raise Exception("Account validation failed, please make sure your Api key and secret are valid and try again...")

    session_params = {}
    if profile is not None:
        print("Profile is not None - profile is {}".format(profile))
        session_params["profile_name"] = profile
    if region is not None:
        print("Region is not None - region is {}".format(region))
        session_params["region_name"] = region
    print("Using session params {}".format(str(session_params)))

    session = boto3.session.Session(**session_params)

    if amazon_token != None:
        cf_client = session.client('cloudformation', region_name=region, aws_session_token=args.amazon_token , aws_access_key_id = args.amazon_api_key, aws_secret_access_key = args.amazon_api_secret)
        sts_client = session.client('sts', region_name=region, aws_session_token=args.amazon_token , aws_access_key_id = args.amazon_api_key, aws_secret_access_key = args.amazon_api_secret)
    else:
        cf_client = session.client('cloudformation', region_name=region, aws_access_key_id = args.amazon_api_key, aws_secret_access_key = args.amazon_api_secret)
        sts_client = session.client('sts', region_name=region, aws_access_key_id = args.amazon_api_key, aws_secret_access_key = args.amazon_api_secret)


    # get aws account id from profile
    aws_account = sts_client.get_caller_identity().get('Account')
    if not aws_account:
        print("AWS account is missing, please define profile (-p)")
        sys.exit(1)

    onboarding(base_url, cf_client, aws_account, cloud_account_id, api_key, api_secret)
