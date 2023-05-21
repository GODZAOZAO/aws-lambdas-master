"""
@author Luke Jordan (bruceli)
"""

from authenticate import *
from database import *
from response import *
from datetime import date
from logger import log_weight_data, delete_weight_data, get_weight_data, log_weight_points

"""
QUERYSTRING
@param weight_kg (required)
@param time (optional)
"""
def DELETE_weight(querystring: dict, claims: dict):

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

    weight_kg = querystring["weight_kg"] if "weight_kg" in querystring else None
    if not weight_kg:
        return error_response(msg="weight_kg missing from querystring. This is required.", code="404")
    time = querystring["time"] if "time" in querystring else None
    user_profile = delete_weight_data(user_profile, weight_kg, target_date=target_date, time=time)
    if not user_profile:
        return error_response(msg="User wants to delete something not found or was out of range.", code="404")
    
    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()

"""
QUERYSTRING
@param weight_kg (required)
@param date (optional)
"""
def POST_weight(querystring: dict, claims: dict):

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
    
    # Log the weight data
    user_profile = log_weight_data(user_profile, querystring["weight_kg"], target_date=target_date)
    if not user_profile:
        return error_response(msg="User wants to edit something out of range.", code="404")
    
    # Check the weight data and give points
    user_profile = log_weight_points(user_profile, target_date)
    
    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()

"""
QUERYSTRING
@param date
"""
def GET_weight(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
    else:
        target_date = str(date.today())

    # Get the authentication token's indicated username
    param_username = claims["cognito:username"].strip()

    # Fetch the user profile from dynamodb
    user_profile = database_get_items([param_username])["Responses"]["profiles"][0]

    return get_weight_data(user_profile, target_date.strip())

    

"""
POST the weight of the person
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
        return POST_weight(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_weight(querystring, claims)
    elif request_type == "GET":
        return GET_weight(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET, DELETE, or POST", code="401")