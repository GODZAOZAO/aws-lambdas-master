"""
@author Luke Jordan (bruceli)
"""

from authenticate import *
from database import *
from response import *

"""
Loop through each key in the querystring,
then update accordingly.

@param anything that settings should havve
"""
def POST_settings(querystring, claims):
    claimed_username = claims["cognito:username"].strip()

    user_profile = database_get_items([claimed_username])["Responses"]["profiles"][0]

    for querystring_key in querystring:
        if querystring_key in user_profile["settings"]:
            user_input = str(querystring[querystring_key]).strip().lower()
            user_input = True if user_input == "0" or user_input == "true" else False
            user_profile["settings"][querystring_key] = user_input

    database_place_item(user_profile)
    return success_response()



"""
Update the settings of the user
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
        return POST_settings(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected POST", code="401")