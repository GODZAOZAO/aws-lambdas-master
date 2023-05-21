from authenticate import *
from database import *
from response import *
from calorieninja import get_automatic_calorie_info, get_manual_calorie_info
from logger import log_nutritional_data, delete_nutritional_data, get_nutritional_data, log_nutritional_points, delete_nutritional_points
from datetime import date
"""
@author Luke Jordan (bruceli)
"""


"""
@param querystring
    Expects "name" (required) and "date" (optional)
@param claims
"""
def DELETE_calorie(querystring: dict, claims: dict):

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

    name = querystring["name"] if "name" in querystring else None
    if not name:
        return error_response(msg="name is missing from querystring. This is required during a DELETE.", code="404")
    user_profile = delete_nutritional_data(user_profile, name, target_date=target_date)
    if not user_profile:
        return error_response(msg="User wants to delete something not found or was out of range.", code="404")
    
    # Check whether points should be changed after deletion
    user_profile = delete_nutritional_points(user_profile, target_date)

    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()




"""
Post the manual entry of calories or the calorieninja query

@param querystring = the query string part of the request.
    Expects "calorieninja" only or the associated keys with the calorieninja output (requiring name and calories)
@param claims = the deciphered json of the authorization token
"""
def POST_calorie(querystring: dict, claims: dict):
    # Get the date
    target_date = ""
    if "date" in querystring:
        target_date = querystring["date"]
        del querystring["date"]
    else:
        target_date = str(date.today())

    # Get the nutritional information of the post request
    nutrition = {}
    if "calorieninja" in querystring:
        query: str = querystring["calorieninja"].strip()
        nutrition = get_automatic_calorie_info(query)
    else:
        nutrition = get_manual_calorie_info(querystring)
        if not nutrition:
            return error_response(msg=f"Manual food entry ---> {str(list(querystring.keys()))} <--- had an invalid key or did not have the required 'name' and 'calories' field.", code="404")

    # Get the authentication token's indicated username
    param_username = claims["cognito:username"].strip()

    # Fetch the user profile from dynamodb
    user_profile = database_get_items([param_username])["Responses"]["profiles"][0]


    # Log the nutritional data
    user_profile = log_nutritional_data(user_profile, nutrition, target_date=target_date)
    if not user_profile:
        return error_response(msg="User wants to edit something out of range.", code="404")
    
    # Check nutritional value and give points
    user_profile = log_nutritional_points(user_profile, target_date)

    # Update DynamoDB with our updated profile
    database_place_item(user_profile)

    return success_response()


def GET_calorie(querystring: dict, claims: dict):
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

    return get_nutritional_data(user_profile, target_date.strip())



"""
Handle everything pertaining to food/intaking calories
"""
def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Perform the GET or POST or DELETE
    """
    request_type = event['context']['http-method']
    querystring = event['params']['querystring']
    if request_type == "GET":
        return GET_calorie(querystring, claims)
    elif request_type == "POST":
        return POST_calorie(querystring, claims)
    elif request_type == "DELETE":
        return DELETE_calorie(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET or POST or DELETE", code="401")