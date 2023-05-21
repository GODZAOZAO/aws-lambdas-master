"""
@author Luke Jordan (bruceli)
"""

import urllib.request
import decimal
import json

CALORIESBURNED_API_KEY = "QDDni6dBzY6m/6++XVr9Fg==lV3WcD1fCBEb22H3"
api_url = "https://api.api-ninjas.com/v1/caloriesburned"

"""
Gets the calories burned of given a query String.

EXAMPLE: "water skiing"
[
  {
    "name": "Skiing, water skiing",
    "calories_per_hour": 435,
    "duration_minutes": 60,
    "total_calories": 435
  }
]

"""
def get_automatic_exercise_info(activity: str, weight_kg: str, duration_min: str = None):
    activity = activity.replace(" ", "%20")
    request = urllib.request.Request(url=f"{api_url}?activity={activity}&weight={weight_kg}&duration={duration_min}", headers={'X-Api-Key': CALORIESBURNED_API_KEY}, method="GET")
    with urllib.request.urlopen(request) as response:
        response_data = json.loads(response.read().decode("utf-8"), parse_float=decimal.Decimal)
        return response_data

def get_manual_exercise_info(querystring):
    activity = {}
    for key in querystring:
        if (
            key == "activity" or key == "calories_burned" or key == "duration_min"
        ):
            activity[key] = querystring[key]
        else:
            return False
    if "activity" not in activity or "calories_burned" not in activity:
        return False
    return activity