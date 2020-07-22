import boto3
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description="Creates an AWS sub account to the user organization."
    )

    parser.add_argument("-n", "--name", required=True, help="The friendly name of the member account.")
    parser.add_argument("-e", "--email", required=True,
                        help="The email address of the owner to assign to the new member account.")
    args = parser.parse_args()

    # print the input arguments
    for arg in vars(args):
        print (arg + " : " + str(getattr(args, arg)))

    while True:
        data = str(input("Are you sure you want to create the account " + args.name + " in your organization? [yes/no] "))
        if data == "no":
            print("Account was not created.")
            return
        if data == "yes":
            break

    org_client = boto3.client("organizations")

    res = org_client.create_account(
        Email=args.email,
        AccountName=args.name
    )

    if not res.get("ResponseMetadata",{}).get("HTTPStatusCode") == 200:
        print("Failed to create account.")
        print(res)
        return

    create_account_request_id = res.get("CreateAccountStatus").get("Id")

    print("Request account name : " + res.get("CreateAccountStatus").get("AccountName"))
    print("Waiting for account to be created ....")

    while True:
        describe_res = org_client.describe_create_account_status(CreateAccountRequestId=create_account_request_id)
        account_state = describe_res.get("CreateAccountStatus").get("State")
        if not account_state == "IN_PROGRESS":
            break
        time.sleep(1)

    if account_state == "FAILED":
        print("Failed to create account : " + describe_res.get("CreateAccountStatus").get("FailureReason"))
        print(describe_res)
        return


    print("Account created.")

    print(describe_res)


    # This is the default role name
    role_name = "OrganizationAccountAccessRole"

    new_account_id = describe_res.get("CreateAccountStatus").get("AccountId")
    switch_role_url = "https://signin.aws.amazon.com/switchrole?account=" + str(new_account_id) + "&roleName=" + str(role_name) + "&displayName=yourNewAccount"

    print(switch_role_url)

if __name__ == '__main__':
    main()
