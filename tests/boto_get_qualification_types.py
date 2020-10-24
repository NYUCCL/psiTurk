"""
set aws config vars in ~/.aws/config under `[default]` section, including
default region as REGION

    [default]
    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    REGION=us-east-1
"""
import boto3
client = boto3.client('mturk')
paginator = client.get_paginator('list_qualification_types')
qualification_types = []
for page in paginator.paginate(MustBeRequestable=False):
    print(page)
    import sys
    sys.exit()
