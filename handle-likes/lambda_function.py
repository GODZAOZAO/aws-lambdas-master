from authenticate import *
from database import *
from response import *
from logger import log_like_data, delete_like_data, get_like_data
from datetime import date

"""
Claimed user will get the likes of "username" specified up to the target_date
@param date (OPTIONAL)
@param "username" (OPTIONAL)
"""
def GET_likes(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        param_username = claims["cognito:username"].strip()
        # return error_response(msg="Missing the \"username\" parameter. This is required for liking.", code="404")
    
    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    param_profile = potential_profiles[0]
    return get_like_data(param_profile, target_date)


"""
Claimed user will post a like to the "username" specified at the target_date
@param date (OPTIONAL)
@param "username" (REQUIRED)
"""
def POST_likes(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    # Get the username. Username is required.
    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        return error_response(msg="Missing the \"username\" parameter. This is required for liking.", code="404")

    # If the username chosen is equal to the calling user, throw an error.
    if param_username == claims["cognito:username"].strip():
        return error_response(msg="User cannot like himself.", code="404")
    
    # Get the profile. Check if it exists
    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    param_profile = potential_profiles[0]
    claimed_username = claims["cognito:username"].strip()

    # The calling user can only encourage if the param user is following calling user.
    if claimed_username not in param_profile["following"]:
        return error_message(msg=f"{param_username} is not following {claimed_username}, so {claimed_username} cannot like {param_username}.", code="404")

    param_profile = log_like_data(param_profile, claimed_username, target_date=target_date)
    if not param_profile:
        return error_response(msg=f"{param_username} does not have a log on the specified date, {target_date}, or it is out of range.", code="404")
    database_place_item(param_profile)
    return success_response()


"""
Claimed user will remove a like from the "username" at the target_date
"""
def DELETE_likes(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        return error_response(msg="Missing the \"username\" parameter. This is required for removing a like.", code="404")

    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    param_profile = potential_profiles[0]
    claimed_username = claims["cognito:username"].strip()
    
    param_profile = delete_like_data(param_profile, claimed_username, target_date=target_date)
    if not param_profile:
        return error_response(msg=f"{claimed_username} never liked {param_username} on {target_date}", code="404")
    database_place_item(param_profile)
    return success_response()

"""
Lambda Handler for LIKES
"""
def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Execute GET, POST, and DELETE
    """
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "GET":
        return GET_likes(querystring, claims)
    elif request_type == "POST":
        return POST_likes(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_likes(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET or POST or DELETE", code="401")