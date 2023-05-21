from authenticate import *
from database import *
from response import *
from logger import log_following_data, delete_following_data


"""
Gets all the people you are following
"""
def GET_following(querystring: dict, claims: dict):
    claimed_username = claims["cognito:username"].strip()
    user_profile = database_get_items([claimed_username])["Responses"]["profiles"][0]
    return user_profile["following"]

"""
Adds a user you wish to follow. If the user does not exist, you cannot follow them.
"""
def POST_following(querystring: dict, claims: dict):
    follower_to_add = str(querystring["follower"]).strip() if "follower" in querystring else None
    if follower_to_add is None:
        return error_response(msg="Missing the \"follower\" parameter. This is required.", code="404")
    potential_profiles = database_get_items([follower_to_add])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{follower_to_add} does not exist", code="404")
    
    claimed_username = claims["cognito:username"].strip()
    user_profile = database_get_items([claimed_username])["Responses"]["profiles"][0]
    user_profile = log_following_data(user_profile, follower_to_add)
    database_place_item(user_profile)
    return success_response()

"""
Deletes a user you are following.
"""
def DELETE_following(querystring: dict, claims: dict):
    follower_to_delete = str(querystring["follower"]).strip() if "follower" in querystring else None
    if follower_to_delete is None:
        return error_response(msg="Missing the \"follower\" parameter. This is required.", code="404")
    
    claimed_username = claims["cognito:username"].strip()
    user_profile = database_get_items([claimed_username])["Responses"]["profiles"][0]
    user_profile = delete_following_data(user_profile, follower_to_delete)
    if not user_profile:
        return error_response(msg=f"{claimed_username} is not following {follower_to_delete}, so I can not delete it.", code="404")
    database_place_item(user_profile)
    return success_response()

def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Perform the POST request for followers
    """
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "GET":
        return GET_following(querystring, claims)
    elif request_type == "POST":
        return POST_following(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_following(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET or POST or DELETE", code="401")