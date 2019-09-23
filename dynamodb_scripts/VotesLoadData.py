
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

table = dynamodb.Table('Vote')

with open("vote_data.json") as json_file:
    voters = json.load(json_file)
    for voter in voters:
        vote_name = voter['vote_name']
        voter_alias = voter['voter_alias']
        candidates = set(voter['candidates'])
        print(f'Set size is {len(candidates)}')
        print(f"Adding vote name: '{vote_name}' and voter_alias: '{voter_alias}' with candidates: {candidates}")
        
        table.put_item(
           Item={
               'ElectionName': vote_name,
               'VoterAlias': voter_alias,
               'Candidates': candidates
            },
            ConditionExpression=Attr('VoterAlias').not_exists()
        )


#            ConditionExpression="attribute_not_exists(#a) AND size(info.candidates) < :max_candidates",
#            ExpressionAttributeNames= {
#                "#a": "voter_alias"
#            },            
#            ExpressionAttributeValues={
#                ":max_candidates": 5
#            }         