"""
@author Luke Jordan (bruceli)
"""
def error_response(msg="Resource Not Found", code="404"):
    return {
        "message": "ERROR: " + msg,
        "code": code
    }

def success_response(msg="Success!", code="200"):
    return {
        "message": "SUCCESS: " + msg,
        "code": code
    }