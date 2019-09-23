
import boto3
import json
import os

from boto3.dynamodb.conditions import Key, Attr

print('Loading function')

dynamodb = boto3.resource('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000") if os.getenv("AWS_SAM_LOCAL") else boto3.resource('dynamodb')

# parameters from the env variables
election_name =  os.environ['ELECTION_NAME']
votes_table_name = os.environ.get('VOTES_TABLE_NAME', 'Vote')

print(f'Votes table name is: {votes_table_name}')
print(f'Election name is: {election_name}')
print(f'Using { "local" if os.getenv("AWS_SAM_LOCAL") else "remote" } database')

votes_table = dynamodb.Table(votes_table_name)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': { "message": str(err) } if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def get_voter_info(voter_alias):
    # get the election info from the table
    response = votes_table.query(
        KeyConditionExpression=Key('ElectionName').eq(election_name) & Key('VoterAlias').eq(voter_alias)
    )
    if len(response[u'Items']) > 0:
        item = response[u'Items'][0]
        return item
    else:
        return None

def process_vote(voter_alias):
    # check for a valid voter name in request
    info = get_voter_info(voter_alias)

    if not info:
        return respond(None, {})

    return respond(None, { "Votes": list(info['Candidates'])})

def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

	TableName provided by template.yaml.

    To scan a DynamoDB table, make a GET request with optional query string parameter.
	To put, update, or delete an item, make a POST, PUT, or DELETE request respectively,
	passing in the payload to the DynamoDB API as a JSON body.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    operation = event['httpMethod']
    if operation in ['GET']:
        try:
            voter_alias = event['queryStringParameters']['voterAlias']
            print(f'Found voter alias: {voter_alias}')
            return process_vote(voter_alias)
        except KeyError:
            return respond(ValueError('Query param "voterAlias" not found in GET request'))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))