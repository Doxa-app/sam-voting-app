
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

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url="http://localhost:8000")
#dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('Election')

with open("election_data.json") as json_file:
    elections = json.load(json_file)
    for e in elections:
        name = e['ElectionName']
        enabled = e['Enabled']
        candidates = set(e['Candidates'])
        print(f"Adding election name: {name} and enabled: {enabled} and voters: {candidates}")

        table.put_item(
           Item={
               'ElectionName': name,
               'Enabled': enabled,
               'Candidates': candidates
            },
            ConditionExpression=Attr('ElectionName').not_exists()
        )
