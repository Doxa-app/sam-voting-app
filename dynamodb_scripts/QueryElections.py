
#
#  Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  This file is licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License. A copy of
#  the License is located at
# 
#  http://aws.amazon.com/apache2.0/
# 
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#  CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.
#
from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
#dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('Election')

print("Query Election table")

response = table.query(
    KeyConditionExpression=Key('ElectionName').eq("APAC_Tech_Summit")
)

for i in response[u'Items']:
    print(f'Election name is {i["ElectionName"]}')
    print(f'Election name type is {type(i["ElectionName"])}')
    print(f'Voters are {i["Voters"]}')
    print(f'Voters type is {type(i["Voters"])}')
    print(f'Election is { "Enabled" if i["Enabled"] else "Disabled"}')