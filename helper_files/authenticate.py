import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

region = 'us-east-1'
userpool_id = 'us-east-1_NZT2ityeJ'
app_client_id = 'dm0rhq0d1mkusbm4pqcpo9rog'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

"""
Validate the token in the event
"""
def authenticate_event(event):
    token = event['params']['header']['Authorization']
    claims = authenticate_token(token)
    if not claims:
        return False
    return claims
    


def authenticate_token(token):
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # Now we know that the claims is valid, return it.
    return claims


if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': 'eyJraWQiOiJZeGo5Y1BDcnVyYndnTU9iSkN0Uk5VOXNCY0RvWDRtUDB6NDhGY1FDSVk4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MWIxNWY4MS00MzY5LTRlOGYtYTVhYS02YTU2OTg2OGVmYTMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfTlpUMml0eWVKIiwiY29nbml0bzp1c2VybmFtZSI6ImJydWNlbGkiLCJvcmlnaW5fanRpIjoiNzVlZTllYmItYzczZS00OWY5LTkzZjItNzhmODk4N2I4MmZlIiwiYXVkIjoiZG0wcmhxMGQxbWt1c2JtNHBxY3BvOXJvZyIsImV2ZW50X2lkIjoiYjMzZDgzZTUtYmRkNy00MGExLWFiZDktOGNkMTRkYWUzY2QwIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzYzMzUxMjUsImV4cCI6MTY3NjMzODcyNSwiaWF0IjoxNjc2MzM1MTI1LCJqdGkiOiJhOGNkZDk1ZS1lMGY1LTQ2YWQtOTk0Ny1jMzE5ZmMzZGFjOTYiLCJlbWFpbCI6Im1pbmR3aXBlMDA3QGdtYWlsLmNvbSJ9.q6JB9Pyd2Dsobh--Frje1I8Ht5DioyBK7ycwap82231-IrqSe62MpBu3bspcBtbRcOPdjbzfibht-jPA-AVNvxjebGmCuuXn8WTACbR8HlQ43sO1nHCVKvtdP9sLhhuaa2Fn10ocHOdwWII0mkAP_3g7HNpFvccR0URZX2WWJQk0dKI-DnPMQAFpnoY1qsx5SpMEoFxWWM69NuYlSYY1_Ch7H_7_hcMZ5FBcT6jVnOtOeI6-k-qTbKbH3e18Cg8k5uCTmBze_kQ0rYrSl1_TfVVbX-rbRu55RnpEl6CadgSRelfYwQYhfCZK7ojf88zU2QqKK9ITHnr7TWKO4TLVmg'}
    print(authenticate_token(event))