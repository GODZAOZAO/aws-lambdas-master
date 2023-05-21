"""
@author Luke Jordan (bruceli)
"""

from authenticate import *
from database import *
from response import *
from datetime import date
from logger import log_post_data, delete_post_data, get_post_data

"""
TODO Need to implement this
"""
def DELETE_post (querystring: dict, claims: dict):

    # Get the authentication token's indicated username
    param_username = claims["cognito:username"].strip()

    # Fetch the user profile from dynamodb
    user_profile = database_get_items([param_username])["Responses"]["profiles"][0]

    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    post = querystring["post"] if "post" in querystring else None
    if not post:
        return error_response(msg="post missing from querystring. This is required.", code="404")
    time = querystring["time"] if "time" in querystring else None
    user_profile = delete_post_data(user_profile, post, target_date=target_date, time=time)
    if not user_profile:
        return error_response(msg="User wants to delete something not found or was out of range.", code="404")
    
    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()

"""
QUERYSTRING
@param post (REQUIRED)
@param date (OPTIONAL)
"""
def POST_post(querystring: dict, claims: dict):

    if "post" not in querystring:
        return error_response(msg="The user's 'post' is a required parameter.", code="401")

    # Get the authentication token's indicated username
    param_username = claims["cognito:username"].strip()

    # Fetch the user profile from dynamodb
    user_profile = database_get_items([param_username])["Responses"]["profiles"][0]

    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())
    
    # Log the post data
    user_profile = log_post_data(user_profile, querystring["post"], target_date=target_date)
    if not user_profile:
        return error_response(msg="User wants to edit something out of range.", code="404")
    
    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()

"""
QUERYSTRING
@param date (OPTIONAL)
@param username (OPTIONAL)
"""
def GET_post(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    # The calling user
    this_user = claims["cognito:username"].strip()

    # Whether the calling user can view the profile
    can_view = False

    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        # Since the username is not specified, the calling user wants to get his own posts.
        can_view = True
        param_username = this_user
    
    if param_username == this_user:
        can_view = True

    # Fetch the profiles associated with the 'param_username'.
    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    # If there are no profiles, that means that the username does not exist.
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    # Get the first profile.
    param_profile = potential_profiles[0]

    # If can_view is False, it means we want ANOTHER user's posts.
    # As per the user story, the calling user can only see the other person's posts
    # If the calling user is a "friend". In other words, param_profile must be following 
    # this user. 
    if (not can_view and this_user in param_profile["following"]) or can_view:
        return get_post_data(param_profile, target_date.strip())

    return error_response(msg=f"{param_username} is not following this user.", code="401")


"""
POST, GET, and DELETE the posts of a user.

TODO Everyone that the user is following can see the post, else,
we need to throw an error.

"""
def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Perform the POST request for the username
    """
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "POST":
        return POST_post(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_post(querystring, claims)
    elif request_type == "GET":
        return GET_post(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET, DELETE, or POST", code="401")