"""
@author Luke Jordan (bruceli)
"""

from datetime import date
from caloriesburned import get_automatic_exercise_info, get_manual_exercise_info
from authenticate import *
from database import *
from response import *
from logger import log_exercise_data, get_exercise_data, delete_exercise_data, log_exercise_points, delete_exercise_points


def POST_exercise(querystring: dict, claims: dict):

    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
        del querystring["date"]
    else:
        target_date = str(date.today())

    activity = get_manual_exercise_info(querystring)
    if not activity:
        return error_response(msg=f"Manual exercise entry ---> {str(list(querystring.keys()))} <--- had an invalid key or did not have the required 'activity' field.", code="404")
    
    # Get the authentication token's indicated username
    param_username = claims["cognito:username"].strip()

    # Fetch the user profile from dynamodb
    user_profile = database_get_items([param_username])["Responses"]["profiles"][0]

    user_profile = log_exercise_data(user_profile, activity, target_date=target_date)
    if not user_profile:
        return error_response(msg="User wants to edit something out of range.", code="404")
    
    # Check calories burned and give points accordingly to users
    user_profile = log_exercise_points(user_profile, target_date)
    
    database_place_item(user_profile)

    return success_response()

def GET_exercise(querystring: dict, claims: dict):
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

    return get_exercise_data(user_profile, target_date.strip())


def DELETE_exercise(querystring: dict, claims: dict):
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

    activity = querystring["activity"].strip() if "activity" in querystring else None
    if not activity:
        return error_response(msg="When deleting an exercise, you must provide an \"activity\" name.", code="404")
    duration_min = str(querystring["duration_min"]).strip() if "duration_min" in querystring else None
    calories_burned = str(querystring["calories_burned"]).strip() if "calories_burned" in querystring else None
    user_profile = delete_exercise_data(user_profile, activity, target_date, calories_burned=calories_burned, duration_min=duration_min)
    if not user_profile:
        return error_response(msg="User wants to delete something not found or was out of range.", code="404")
    
    # Check calories burned after exercise deletion
    user_profile = delete_exercise_points(user_profile, target_date)
    
    database_place_item(user_profile)

    return success_response()


def lambda_handler (event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "POST":
        return POST_exercise(querystring, claims)
    elif request_type == "GET":
        return GET_exercise(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_exercise(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected POST", code="401")
    