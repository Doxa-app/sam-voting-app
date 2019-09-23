#!/usr/local/bin/python3

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
import sys, getopt

import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def check_table_exists(dynamodb_client, election_table, vote_table):

    existing_tables = dynamodb_client.list_tables()['TableNames']
    print(f'Existing tables are {existing_tables}')

    # create Election table if not exists
    if election_table not in existing_tables:
        print(f'Creating new table with name: {election_table}')
        table = dynamodb_client.create_table(
            TableName=election_table,
            KeySchema=[
                {
                    'AttributeName': 'ElectionName',
                    'KeyType': 'HASH'  #Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ElectionName',
                    'AttributeType': 'S'
                },

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    else:
        print(f'Table with name: {election_table} already exists')

    # check the vote table exists
    if vote_table not in existing_tables:
        print(f'Creating new table with name: {vote_table}')
        table = dynamodb_client.create_table(
            TableName=vote_table,
            KeySchema=[
                {
                    'AttributeName': 'ElectionName',
                    'KeyType': 'HASH'  #Partition key
                },
                {
                    'AttributeName': 'VoterAlias',
                    'KeyType': 'RANGE'  #Range key
                },               
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ElectionName',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'VoterAlias',
                    'AttributeType': 'S'
                },        
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    else:
        print(f'Table with name: {vote_table} already exists')

def load_election_table(dynamodb, table_name, use_local, filename):
    
    table = dynamodb.Table(table_name)
    with open(filename) as json_file:
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
    

def main(argv):
    election_table = 'Election'
    vote_table = 'Vote'
    use_local = True
    filename = "election_data.json"
    try:
      opts, args = getopt.getopt(argv,"he:v:r:f:",["election-table=","vote-table=","remote-mode=", "file="])
    except getopt.GetoptError:
        print(f'{sys.argv[0]} [-e <election-table>] [-v <election-table>] [-r] [-f <filename>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(f'{sys.argv[0]} [-e <election-table>] [-v <election-table>] [-r] [-f <filename>]')
            sys.exit()
        elif opt in ("-e", "--election-table"):
            election_table = arg
        elif opt in ("-v", "--vote-table"):
            vote_table = arg            
        elif opt in ("-r", "--remote-mode"):
            use_local = False
        elif opt in ("-f", "--file"):
            filename = arg  
    print(f'Election Table name is {election_table}')
    print(f'Vote Table name is {vote_table}')
    print(f'Local mode is {use_local}')
    print(f'Data filename is {filename}')

    # create the dynamodb client
    dynamodb_client = boto3.client('dynamodb', endpoint_url="http://localhost:8000") if use_local else boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if use_local else boto3.resource('dynamodb')

    # check the the tables exist
    check_table_exists(dynamodb_client, election_table, vote_table)
    # load the election table with data
    load_election_table(dynamodb, election_table, use_local, filename)

if __name__ == "__main__":
   main(sys.argv[1:])
