"""
@author Luke Jordan (bruceli)
"""

from authenticate import *
from database import *
from response import *
from logger import get_own_profile, get_other_profile, initialize_personal_profile

"""
Gets the profile of a user or the calling user.

@param querystring = the query string part of the request (See bottom of the document)
@param claims = the deciphered json of the authorization token
"""
def GET_profile(querystring: dict, claims: dict):
    # Username and email derived from the authentication token
    claimed_username = claims["cognito:username"].strip()

    # Username and email passed in from API call
    param_username = ""
    if 'username' not in querystring:
        param_username = claimed_username
    else:
        param_username = querystring["username"].strip()

    # The user is trying to fetch HIS OWN PROFILE INFO. Return it all.
    if claimed_username == param_username:
        # return personal user info
        # If there does not exist such a user, so create one. 
        user_profile = database_init_profile(claims["email"].strip(), claimed_username)

        user_profile = get_own_profile(user_profile)

        database_place_item(user_profile)

        user_profile["logs"] = [user_profile["logs"][-1]] # Get the most recent log 

        return user_profile

    # The user is trying to fetch ANOTHER USER'S INFO. Return limited info.
    # TODO Edit the returned values based on the profile's privacy settings
    elif claimed_username != param_username:
        
        other_profiles = database_get_items([param_username])["Responses"]["profiles"]
        
        # User does not exist
        if len(other_profiles) == 0:
            return error_response(msg=f"{param_username} does not exist.", code="404")
        
        other_profile = other_profiles[0]
        other_profile = get_other_profile(other_profile)
        return other_profile
    
    return error_response(msg="Reached end of GET-profile lamdba function. Something went really wrong.")


def POST_profile(querystring, claims):
    # Username and email derived from the authentication token
    claimed_username = claims["cognito:username"].strip()
    user_profile = database_init_profile(claims["email"].strip(), claimed_username)
    user_profile = get_own_profile(user_profile)
    user_profile = initialize_personal_profile(user_profile, querystring)
    database_place_item(user_profile)
    return success_response()



"""
GET User profile 

@param event
@param context

QUERYSTRING
@param username = *OPTIONAL* username of the user to get info about

HEADER
@param Authorization = Authorization token.

    - If token is invalid,
        Then,
            Return FALSE

    - If token's claims["cognito:username"] == event["username"]
        Then, 
            create a profile for the user if there doesn't exist one.
            return all of dynamodb's knowledge of username and email
            
    - If token's claims["cognito:username"] != event["username"]
        Then, 
            return limited information about username and email

"""
def lambda_handler(event, context):

    """
    Validate the token
    """
    claims = authenticate_event(event)
    if not claims:
        return error_response(msg="Bad Token", code="401")
    
    """
    Perform the GET request for the username
    """
    querystring = event['params']['querystring']
    request_type = event['context']['http-method']
    if request_type == "GET":
        return GET_profile(querystring, claims)
    elif request_type == "POST":
        return POST_profile(querystring, claims)
    else:
        return error_response(msg=f"Got {request_type} but expected GET or POST", code="401")


"""
{
   "body-json":{
      
   },
   "params":{
      "path":{
         
      },
      "querystring":{
         "token":"eyJraWQiOiJZeGo5Y1BDcnVyYndnTU9iSkN0Uk5VOXNCY0RvWDRtUDB6NDhGY1FDSVk4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MWIxNWY4MS00MzY5LTRlOGYtYTVhYS02YTU2OTg2OGVmYTMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfTlpUMml0eWVKIiwiY29nbml0bzp1c2VybmFtZSI6ImJydWNlbGkiLCJvcmlnaW5fanRpIjoiZjUzNGUxYzktYzJiNC00ZTRmLThkMmMtZmJlODk5ODM4NTg2IiwiYXVkIjoiZG0wcmhxMGQxbWt1c2JtNHBxY3BvOXJvZyIsImV2ZW50X2lkIjoiMmM2MzYzMmEtNmU5NS00MGFjLWEyODEtZWRkNmQ4NTE1MDE4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzkwMzM2ODEsImV4cCI6MTY3OTAzNzI4MSwiaWF0IjoxNjc5MDMzNjgxLCJqdGkiOiI3MTBmNzNhYS00MmQ1LTRkYmMtYmZlYy0xYjFlZDQ5MzA2ZjEiLCJlbWFpbCI6Im1pbmR3aXBlMDA3QGdtYWlsLmNvbSJ9.S__1CVvhCk_0ZevJ0vyw13BDT5KDlnb6CJMatpAM2RODaVu3e69ta4ZhSgBgi2XmCrzV-DdKtPiSC4EDewaNsTx5LhHMjYpOh4Eqmui4ocPzIVcGGUBfnYOZbUsIEQKGH6wOpfgidE1D8Vrs6V8GQBx-NZPMP2MRVRu_ob_Ah8eS8HLjWJUU_Sl4vD-L6cH1LvBFcOQ6vjTBfWKZjHLsoPokg0glNJkx8YMH-uyKJFbxHHHMUD2Axh_uGPluQzDnJjP3KX1E_12pyl1UdWIUm5Qh5Gk5ZoAaiUehQb7IvRJh9vQYaujqzantv0JLLw8CF00nzOuPbyD-oi1rMNRqvg",
         "username":"bruceli"
      },
      "header":{
         "Accept":"*/*",
         "Accept-Encoding":"gzip, deflate, br",
         "Authorization":"eyJraWQiOiJZeGo5Y1BDcnVyYndnTU9iSkN0Uk5VOXNCY0RvWDRtUDB6NDhGY1FDSVk4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MWIxNWY4MS00MzY5LTRlOGYtYTVhYS02YTU2OTg2OGVmYTMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfTlpUMml0eWVKIiwiY29nbml0bzp1c2VybmFtZSI6ImJydWNlbGkiLCJvcmlnaW5fanRpIjoiZjUzNGUxYzktYzJiNC00ZTRmLThkMmMtZmJlODk5ODM4NTg2IiwiYXVkIjoiZG0wcmhxMGQxbWt1c2JtNHBxY3BvOXJvZyIsImV2ZW50X2lkIjoiMmM2MzYzMmEtNmU5NS00MGFjLWEyODEtZWRkNmQ4NTE1MDE4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzkwMzM2ODEsImV4cCI6MTY3OTAzNzI4MSwiaWF0IjoxNjc5MDMzNjgxLCJqdGkiOiI3MTBmNzNhYS00MmQ1LTRkYmMtYmZlYy0xYjFlZDQ5MzA2ZjEiLCJlbWFpbCI6Im1pbmR3aXBlMDA3QGdtYWlsLmNvbSJ9.S__1CVvhCk_0ZevJ0vyw13BDT5KDlnb6CJMatpAM2RODaVu3e69ta4ZhSgBgi2XmCrzV-DdKtPiSC4EDewaNsTx5LhHMjYpOh4Eqmui4ocPzIVcGGUBfnYOZbUsIEQKGH6wOpfgidE1D8Vrs6V8GQBx-NZPMP2MRVRu_ob_Ah8eS8HLjWJUU_Sl4vD-L6cH1LvBFcOQ6vjTBfWKZjHLsoPokg0glNJkx8YMH-uyKJFbxHHHMUD2Axh_uGPluQzDnJjP3KX1E_12pyl1UdWIUm5Qh5Gk5ZoAaiUehQb7IvRJh9vQYaujqzantv0JLLw8CF00nzOuPbyD-oi1rMNRqvg",
         "Cache-Control":"no-cache",
         "CloudFront-Forwarded-Proto":"https",
         "CloudFront-Is-Desktop-Viewer":"true",
         "CloudFront-Is-Mobile-Viewer":"false",
         "CloudFront-Is-SmartTV-Viewer":"false",
         "CloudFront-Is-Tablet-Viewer":"false",
         "CloudFront-Viewer-ASN":"14618",
         "CloudFront-Viewer-Country":"US",
         "Content-Type":"application/json",
         "Host":"3t4azy5e1i.execute-api.us-east-1.amazonaws.com",
         "Postman-Token":"2824da69-a25a-4740-87db-1675bcf989d3",
         "User-Agent":"PostmanRuntime/7.31.3",
         "Via":"1.1 6f067a3fd6e721a7db2a2901701a65d8.cloudfront.net (CloudFront)",
         "X-Amz-Cf-Id":"PB0pUD4LsxFzQLnmXka2NBYDpQgKcPI5lyC4YVIEEJ9kK4MB9uB7Ow==",
         "X-Amzn-Trace-Id":"Root=1-641406e9-66d060a022b9639923de4a83",
         "X-Forwarded-For":"54.86.50.139, 15.158.50.43",
         "X-Forwarded-Port":"443",
         "X-Forwarded-Proto":"https"
      }
   },
   "stage-variables":{
      
   },
   "context":{
      "account-id":"",
      "api-id":"3t4azy5e1i",
      "api-key":"",
      "authorizer-principal-id":"",
      "caller":"",
      "cognito-authentication-provider":"",
      "cognito-authentication-type":"",
      "cognito-identity-id":"",
      "cognito-identity-pool-id":"",
      "http-method":"GET",
      "stage":"test",
      "source-ip":"54.86.50.139",
      "user":"",
      "user-agent":"PostmanRuntime/7.31.3",
      "user-arn":"",
      "request-id":"ad4de25f-caac-4e2c-9bea-e3bc879ff76e",
      "resource-id":"a7rvkk",
      "resource-path":"/contact"
   }
}
"""
