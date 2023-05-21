"""
@author Luke Jordan (bruceli)
"""

import urllib.request
import decimal
import json 

NINJA_API_KEY = "c8JdmNkL6+/bM6X6lxL/rg==QpNnqxHkTeqLLMR2"
api_url = "https://api.calorieninjas.com/v1/nutrition?query="


"""
Gets the Calorie Information given a query String.

EXAMPLE: "beef hamburger"
{
    'items': [
        {'name': 'beef', 'calories': 291.9, 'serving_size_g': 100.0, 'fat_total_g': 19.7, 'fat_saturated_g': 7.8, 'protein_g': 26.6, 'sodium_mg': 63, 'potassium_mg': 206, 'cholesterol_mg': 87, 'carbohydrates_total_g': 0.0, 'fiber_g': 0.0, 'sugar_g': 0.0},
        {'name': 'hamburger', 'calories': 242.5, 'serving_size_g': 100.0, 'fat_total_g': 11.8, 'fat_saturated_g': 4.7, 'protein_g': 15.2, 'sodium_mg': 349, 'potassium_mg': 138, 'cholesterol_mg': 54, 'carbohydrates_total_g': 17.9, 'fiber_g': 0.0, 'sugar_g': 0.0}
    ]
}

"""
def get_automatic_calorie_info(query):
    query = query.replace(" ", "%20")
    request = urllib.request.Request(url=api_url+query, headers={'X-Api-Key': NINJA_API_KEY}, method="GET")
    with urllib.request.urlopen(request) as response:
        response_data = json.loads(response.read().decode("utf-8"), parse_float=decimal.Decimal)
        return response_data



"""
Manually inputting calorie ninja information
"""
def get_manual_calorie_info(querystring):
    nutrition = {}
    for key in querystring:
        if (
            key == "name" or key == "calories" or key == "sodium_mg" or key == "sugar_g" or 
            key == "fat_total_g" or key == "cholesterol_mg" or key == "protein_g" or
            key == "fiber_g" or key == "serving_size_g" or key == "fat_saturated_g" or
            key == "carbohydrates_total_g" or key == "potassium_mg"
        ):
            nutrition[key] = querystring[key]

        else:
            return False
    
    # We will require name and calorie for food items.
    if "name" not in nutrition or "calories" not in nutrition:
        return False
    
    return {"items": [nutrition]}