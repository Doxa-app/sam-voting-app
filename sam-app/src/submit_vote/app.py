
import boto3
import json
import os

from boto3.dynamodb.conditions import Key, Attr

print('Loading function')
dynamodb = boto3.resource('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000") if os.getenv("AWS_SAM_LOCAL") else boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000") if os.getenv("AWS_SAM_LOCAL") else boto3.client('dynamodb')

# parameters from the env variables
election_name =  os.environ['ELECTION_NAME']
election_table_name = os.environ.get('ELECTION_TABLE_NAME', 'Election')
votes_table_name = os.environ.get('VOTES_TABLE_NAME', 'Vote')
max_votes_per_voter = os.environ.get('MAX_VOTES_PER_VOTER', 3)

print(f'Election table name is: {election_table_name}')
print(f'Votes table name is: {votes_table_name}')
print(f'Election name is: {election_name}')
print(f'Max votes per voter is: {max_votes_per_voter}')
print(f'Using { "local" if os.getenv("AWS_SAM_LOCAL") else "remote" } database')

election_table = dynamodb.Table(election_table_name)
votes_table = dynamodb.Table(votes_table_name)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': { "message": str(err) } if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def get_election_info():
    # get the election info from the table
    response = election_table.query(
        KeyConditionExpression=Key('ElectionName').eq(election_name)
    )
    if len(response[u'Items']) > 0:
        item = response[u'Items'][0]
        return item
    else:
        return None

def get_voter_info(voter):
    # get the election info from the table
    response = votes_table.query(
        KeyConditionExpression=Key('ElectionName').eq(election_name) & Key('VoterAlias').eq(voter)
    )
    if len(response[u'Items']) > 0:
        item = response[u'Items'][0]
        return item
    else:
        return None

def is_election_enabled(info):
    if info:
        return info['Enabled']
    else:
        return False

def is_viable_voter(voter, info):
    print("Checking if viable voter")
    if info:
        return voter in info['Candidates']
    else:
        return False

def add_new_vote(voter_name, candidate_name):

    # get the existing voter info
    voter_info = get_voter_info(voter_name)
    if not voter_info:
        print(f'Voter "{voter_name}" not found. Put new voter entry "{candidate_name}" in table')
        votes_table.put_item(
            Item={
                'ElectionName': election_name,
                'VoterAlias': voter_name,
                'Candidates': set([candidate_name])
            },
            ConditionExpression=Attr('VoterAlias').not_exists()
        )
    else:
        # check if already voted for same candidate
        candidates = voter_info['Candidates']
        if candidate_name in candidates:
            return respond(ValueError(f'Already voted for candidate: {candidate_name}'))

        # add the new entry
        print(f'Voter "{voter_name}" found. Updating existing entry')
        try:
            votes_table.update_item(
                Key={
                    'ElectionName': election_name,
                    'VoterAlias': voter_name
                },
                UpdateExpression="ADD #cd :vote",
                ConditionExpression=Attr('Candidates').size().lt(max_votes_per_voter),
                ExpressionAttributeNames={
                    "#cd": "Candidates"
                },
                ExpressionAttributeValues={
                    ":vote": set([candidate_name])
                },
            )
        except dynamodb_client.exceptions.ConditionalCheckFailedException:
            return respond(ValueError('Max number of votes reached'))

    return respond(None, "Vote added successfully")

def process_vote(payload):
    # check for a valid voter name in request
    voter_alias = payload['VoterAlias']
    if not voter_alias:
        return respond(ValueError('Must include a voter name in request'))
    print(f'Voter alias is {voter_alias}')
    # check for a valid candidate name in request
    candidate_alias = payload['CandidateAlias']
    if not candidate_alias:
        return respond(ValueError('Must include a candidate name in request'))
    print(f'Candidate alias is {candidate_alias}')

    # get election info
    election = get_election_info()
    if not election:
        return respond(ValueError(f'Election name: "{election_name}" not found'))
    print(f'Election is {election}')

    # validate voter and candidate names
    if not (is_viable_voter(voter_alias, election) and is_viable_voter(candidate_alias, election)):
        return respond(ValueError(f'Username not found'))

    return add_new_vote(voter_alias, candidate_alias)

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
    if operation in ['POST']:
        payload = json.loads(event['body'])
        return process_vote(payload)
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))