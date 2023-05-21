"""
@author Luke Jordan (bruceli)
"""

import boto3
from datetime import date

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('profiles')

"""
Get the items in the database by using a list of emails and usernames

How to interpret response:
    ["Responses"]["profiles"][1]["username"] would get the second item's username

"""
def database_get_items(list_usernames):

    keys = [{'username': itm} for itm in list_usernames]
        
    return dynamodb.batch_get_item(
        RequestItems={
            table.name: {
                'Keys': keys
            }
        }
    )

"""
Initialize a blank profile for a email and username
"""
def database_init_profile(email, username):
    response = database_get_items([username])
    if len(response["Responses"]["profiles"]) == 0:
        item = {
            'username': username,
            'email': email,
            'total_points': 0,
            'following': {},
            'login': {
                'last_login': str(date.today()),
                'login_streak': 1
            },
            'logs': [],
            'personal': {    
                'sex': 'other',
                'first': 'FirstName',
                'last': 'LastName',
                'height_cm': 160,
                'target_weight_kg': 75,
                'target_calorie_consumed': 2000,
                'target_calorie_exercise': 500
            },
            'settings': {
                'is_profile_public': True,
                'is_email_public': False,
                'is_logs_public': True,
                'is_following_public': True,
                'is_login_public': True,
                'is_sex_public': True,
                'is_first_public': False,
                'is_last_public': False,
                'is_height_public': False,
                'is_target_weight_public': True,
                'is_target_calorie_consumed_public': True,
                'is_target_calorie_exercised_public': True
            }
        }
        table.put_item(
            Item=item
        )
        return item
    return response["Responses"]["profiles"][0]
    
"""
Places an item into the DynamoDB table.
If the item already exists, it updates it.
"""
def database_place_item(item):
    return table.put_item(
        Item=item
    )


"""
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('profiles')

def get_dummy_item():
    return dynamodb.batch_get_item(
        RequestItems={
            table.name: {
                'Keys': [
                    {
                        'email': 'mindwipe007@gmail.com',
                        'username': 'bruceli'
                    }
                ]
            }
        }
    )

def place_dummy_item():
    return table.put_item(
        Item={
            'email': 'mindwipe007@gmail.com',
            'username': 'mindwipe007',
            'logs': [
                { 'day': 1 }
            ],
            'following': [
                {
                    'email': 'luke@outersystems.com',
                    'username': 'luke'
                }
            ],
            'login': {
                'login_streak': 1000,
                'last_login': 1
            },
            'settings': {
                'bb': True
            }
        }
    )


def lambda_handler(event, context):
    # TODO implement
    # return get_dummy_item()["Responses"]["profiles"][0]["username"]
    return place_dummy_item()
"""