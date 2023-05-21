"""
@author Luke Jordan (bruceli)
"""

from authenticate import *
from database import *
from response import *
from logger import log_encourage_data, get_encourage_data
from datetime import date

"""
Claimed user will get the enouragement of "username" specified up to the target_date
@param date (OPTIONAL)
@param "username" (OPTIONAL)
"""
def GET_encourage(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    # The username is the CALLING USER'S username if "username" is not specified
    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        param_username = claims["cognito:username"].strip()
        # return error_response(msg="Missing the \"username\" parameter. This is required for encouragement.", code="404")
    
    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    param_profile = potential_profiles[0]
    return get_encourage_data(param_profile, target_date)


"""
Claimed user will post an encouragement to the "username" specified at the target_date
@param "date" (OPTIONAL)
@param "username" (REQUIRED)
@param "type" (REQUIRED)
"""
def POST_encourage(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    param_username = str(querystring["username"]).strip() if "username" in querystring else None
    if param_username is None:
        return error_response(msg="Missing the \"username\" parameter. This is required for encouragement.", code="404")
    
    param_type = str(querystring["type"]).strip() if "type" in querystring else None
    if param_type is None:
        return error_response(msg="Missing the \"type\" parameter. This is required for encouragement.", code="404")

    potential_profiles = database_get_items([param_username])["Responses"]["profiles"]
    if len(potential_profiles) == 0:
        return error_response(msg=f"{param_username} does not exist", code="404")
    
    param_profile = potential_profiles[0]
    claimed_username = claims["cognito:username"].strip()

    # The calling user can only encourage if the param user is following calling user.
    if claimed_username not in param_profile["following"]:
        return error_response(msg=f"{param_username} is not following {claimed_username}, so {claimed_username} cannot encourage {param_username}.", code="404")

    param_profile = log_encourage_data(param_profile, claimed_username, param_type, target_date=target_date)
    if not param_profile:
        return error_response(msg=f"{param_username} does not have a log on the specified date, {target_date}, or it is out of range.", code="404")
    database_place_item(param_profile)
    return success_response()


def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Perform the GET and POST for encouragement
    """
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "GET":
        return GET_encourage(querystring, claims)
    elif request_type == "POST":
        return POST_encourage(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET or POST", code="401")