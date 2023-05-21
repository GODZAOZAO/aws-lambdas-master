from datetime import date, datetime, timedelta
from decimal import Decimal

"""
The maximum editable days that the user is able to edit.

IMPORTANT: "Days" really means the most recent entries.
"""
MAX_EDITABLE_DAYS = 7
LOGIN_STREAK_DAYS_UNTIL_REWARD = 15
LOGIN_STREAK_REWARD_POINTS = 15
LIKE_REWARD_POINTS = 1
PERSONAL_GOAL_REWARD_POINTS = 1
MAX_CHARACTER_LENGTH = 280
TIME_FORMAT = "%H:%M:%S"

"""
@author Luke Jordan (bruceli)
"""
def __empty_log(date: date):
    return {
        "date": str(date),
        "food_itemset": [],
        "fitness_itemset": [],
        "weight_itemset": [],
        "users_liked": {},
        "users_encouraged": {},
        "posts": [],
        "reward_flags": {
            "target_calories_burned": False,
            "target_calories_eaten": False,
            "target_weight": False,
        },
        "points": 0,
    }


"""
@author Luke Jordan (bruceli)

We need to create a new log for the user for todays date

@param user_profile is the entire user profile.
@return the updated logs with today's empty log.
"""
def __initialize_todays_log(user_profile):
    user_profile_logs = user_profile["logs"]

    # Todays date
    todays_date = date.today()  # YYYY-MM-DD

    # Initialize this profile's first ever log
    if len(user_profile_logs) == 0:
        user_profile_logs.append(__empty_log(todays_date))

    # The most recent time the user has had their log updated
    latest_log = user_profile_logs[-1]

    if "date" not in latest_log or latest_log["date"] != str(todays_date):
        user_profile_logs.append(__empty_log(todays_date))

    return user_profile_logs


"""
@author Luke Jordan (bruceli)

From todays date, go backwards in time until we reach the MAX_EDITABLE_DAYS
Once we reach a date that matches "date", then we return the index of it.
If it doesn't exist, then initialize it.
"""
def __get_index_of_log(
    user_profile: dict, target_date: date, abort_if_nonexistant: bool = False
) -> int:
    user_profile_logs: list = __initialize_todays_log(user_profile)

    todays_date = date.today()

    out_of_range = True
    # Determine if it is in range
    delta = timedelta(days=1)
    for day in range(0, MAX_EDITABLE_DAYS):
        delta_date = todays_date - (delta * day)
        if target_date == delta_date:
            out_of_range = False
            break
    if out_of_range:
        return -1

    index_of_day = len(user_profile_logs) - 1

    # We know it is in range, now get the index
    for day in reversed(user_profile_logs[:MAX_EDITABLE_DAYS]):
        delta_date = date.fromisoformat(day["date"])
        if delta_date == target_date:
            return index_of_day
        if delta_date < target_date:
            if abort_if_nonexistant:  # Does not create a new log
                return -1
            user_profile_logs.insert(index_of_day + 1, __empty_log(target_date))
            return index_of_day + 1
        index_of_day -= 1

    user_profile_logs.insert(0, __empty_log(target_date))
    return 0

"""
@author Luke Jordan (bruceli)

Get a set of logs to a specific target_date
"""
def __get_log_set(user_profile: dict, target_date: date):
    user_profile_logs: list = __initialize_todays_log(user_profile)

    all_logs = []

    todays_date = date.today()
    if target_date > todays_date:
        return all_logs

    for day in reversed(user_profile_logs):
        delta_date = date.fromisoformat(day["date"])
        if delta_date < target_date:
            break
        else:
            all_logs.append(day)

    return all_logs

"""
@author Luke Jordan (bruceli)

Delete an empty log
"""
def __del_empty_log(user_profile: dict, index_to_del: int):
    log = user_profile["logs"][index_to_del]
    if (
        not log["food_itemset"]
        and not log["fitness_itemset"]
        and not log["weight_itemset"]
        and log["date"] != str(date.today())
    ):
        del user_profile["logs"][index_to_del]


"""
@author Luke Jordan (bruceli)

Because the items in logs continues to grow, and we need to exclude unnecessary
data, place keys we want to keep into a "keep_list" and return just those
keys from the list of valid log.
"""
def __extract_from_logs(valid_logs: list, keep_list: list):
    if "date" not in keep_list:
        keep_list.append("date")
    keep_logs = []
    for log in reversed(valid_logs):
        modded_log = {}
        for key in log:
            if key in keep_list:
                modded_log[key] = log[key]
        keep_logs.append(modded_log)
    return keep_logs


"""
@author Luke Jordan (bruceli)
@author Shao-chun Wang

When getting one's own profile, we can't just return the entire thing.
"""
def get_own_profile(user_profile: dict) -> dict:
    if len(user_profile["logs"]) != 0:
        __del_empty_log(user_profile, -1)  # Remove the most recent empty log if it isn't today
    __initialize_todays_log(user_profile)  # Create today's log
    prev_login: date = date.fromisoformat(user_profile["login"]["last_login"])
    if (user_profile["login"]["login_streak"] + 1) % LOGIN_STREAK_DAYS_UNTIL_REWARD == 0 and user_profile["login"]["last_login"] != str(date.today()):
        user_profile["logs"]["points"] += LOGIN_STREAK_REWARD_POINTS
        user_profile["total_points"] += LOGIN_STREAK_REWARD_POINTS
    user_profile["login"]["last_login"] = str(date.today())
    if prev_login == date.today() - timedelta(days=1):
        user_profile["login"]["login_streak"] += 1
    elif prev_login == date.today():
        return user_profile
    else:
        user_profile["login"]["login_streak"] = 1
    return user_profile

"""
@author Luke Jordan (bruceli)

Gets another user's profile
"""
def get_other_profile(other_profile: dict) -> dict:
    other_settings = other_profile["settings"]
    if not other_settings["is_profile_public"]:
        return False
    if not other_settings["is_email_public"]:
        other_settings["email"] = None
    if not other_settings["is_logs_public"]:
        other_profile["logs"] = []
    if not other_settings["is_following_public"]:
        other_profile["following"] = []
    if not other_settings["is_login_public"]:
        other_profile["login"] = {}
    if not other_settings["is_sex_public"]:
        other_profile["personal"]["sex"] = None
    if not other_settings["is_first_public"]:
        other_profile["personal"]["first"] = None
    if not other_settings["is_last_public"]:
        other_profile["personal"]["last"] = None
    if not other_settings["is_height_public"]:
        other_profile["personal"]["height_cm"] = None
    if not other_settings["is_target_weight_public"]:
        other_profile["personal"]["target_weight_kg"] = None
    if not other_settings["is_target_calorie_consumed_public"]:
        other_profile["personal"]["target_calorie_consumed"] = None
    if not other_settings["is_target_calorie_exercised_public"]:
        other_profile["personal"]["target_calorie_exercise"] = None
    return other_profile

"""
@author Luke Jordan (bruceli)

Initialize a user's personal profile
"""
def initialize_personal_profile(user_profile: dict, querystring: dict) -> dict:
    str_valid_keys = {
        "sex",
        "first",
        "last"
    }
    int_valid_keys = {
        "height_cm",
        "target_weight_kg",
        "target_calorie_consumed",
        "target_calorie_exercise",
    }
    for key in querystring:
        if key in str_valid_keys:
            user_profile["personal"][key] = str(querystring[key]).strip()
        elif key in int_valid_keys:
            user_profile["personal"][key] = Decimal(querystring[key])
    return user_profile


"""
@author Luke Jordan (bruceli)

Adds weight data to the weight_itemset

@param user_profile: dict = the userprofile of the user
@param weight_kg: float = the weight of the user 
@param target_date: str = the date of the target log in string format
"""
def log_weight_data(user_profile: dict, weight_kg: float, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    user_profile["logs"][index_of_day]["weight_itemset"].append(
        {"time": datetime.now().strftime(TIME_FORMAT), "weight_kg": weight_kg}
    )
    return user_profile

"""
@author Luke Jordan (bruceli)

Logs a post to the posts list

@param user_profile: dict = the userprofile of the user
@param post: str = the post of the user
@param target_date: str = the date of the target in string format
"""
def log_post_data(user_profile: dict, post: str, target_date: str):
    if len(post) > MAX_CHARACTER_LENGTH:
        return False
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    user_profile["logs"][index_of_day]["posts"].append(
        {"time": datetime.now().strftime(TIME_FORMAT), "post": str(post)}
    )
    return user_profile


"""
@author Luke Jordan (bruceli)

Adds the calorie_ninja_output to the user_profile and then places that
data back into the table.

@param user_profile: dict = the userprofile of the user
@param calorie_ninja_output: dict = the calorie ninja dict
@param target_date: str = the date of the target in string format
"""
def log_nutritional_data(user_profile: dict, calorie_ninja_output: dict, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    for food_item in calorie_ninja_output["items"]:
        user_profile["logs"][index_of_day]["food_itemset"].append(food_item)
    return user_profile


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of nutritional data
"""
def get_nutritional_data(user_profile: dict, target_date: str) -> list:
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["food_itemset"])


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of weight data
"""
def get_weight_data(user_profile: dict, target_date: str) -> list:
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["weight_itemset"])


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of posts data 
"""
def get_post_data(user_profile: dict, target_date: str) -> list:
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["posts"])


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of fitness data
"""
def get_exercise_data(user_profile: dict, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["fitness_itemset"])


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of userliked data
"""
def get_like_data(user_profile: dict, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["users_liked", "points"])


"""
@author Luke Jordan (bruceli)

Given the user_profile and the target_date, return an array of user_encourage data
"""
def get_encourage_data(user_profile: dict, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    valid_logs = __get_log_set(user_profile, target_date)
    return __extract_from_logs(valid_logs, ["users_encouraged"])


"""
@author Luke Jordan (bruceli)

Logs the exercise data into the appropriate log

@param user_profile: dict = the userprofile of the user
@param activity_output: dict = the activity dict
@param target_date: str = the date of the target in string format
"""
def log_exercise_data(user_profile: dict, activity_output: dict, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    user_profile["logs"][index_of_day]["fitness_itemset"].append(activity_output)
    return user_profile


"""
@author Luke Jordan (bruceli)

Logs a like for the user, and increases the point by one.

@param user_profile: dict = the userprofile of the user
@param param_username: str = The username who liked
@param target_date: str = the date of the target in string format
"""
def log_like_data(user_profile: dict, param_username: str, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(
        user_profile, target_date, abort_if_nonexistant=True
    )
    if index_of_day == -1:
        return False
    user_profile["logs"][index_of_day]["users_liked"][param_username] = 1
    user_profile["logs"][index_of_day]["points"] += LIKE_REWARD_POINTS
    user_profile["total_points"] += LIKE_REWARD_POINTS
    return user_profile


"""
@author Luke Jordan (bruceli)

Logs an encouragement for the user

@param user_profile: dict = the userprofile of the user
@param param_username: str = the username who encouraged
@param encourage_enum: int = the type of encoruagement
@param target_date: str = the target date
"""
def log_encourage_data(user_profile: dict, param_username: str, encourage_enum: int, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(
        user_profile, target_date, abort_if_nonexistant=True
    )
    if index_of_day == -1:
        return False
    user_profile["logs"][index_of_day]["users_encouraged"][
        param_username
    ] = encourage_enum
    return user_profile


"""
@author Luke Jordan (bruceli)

Logs the follower into the user profile

@param user_profile: dict = the userprofile of the user
@param follower_to_add: str = the username who this user is following
"""
def log_following_data(user_profile: dict, follower_to_add: str):
    user_profile["following"][follower_to_add] = 1
    return user_profile


"""
@author Luke Jordan (bruceli)
@author Shao-chun Wang [Point system]

Deletes the like from the user, and decreases the point by one.
"""
def delete_like_data(user_profile: dict, param_username: str, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(
        user_profile, target_date, abort_if_nonexistant=True
    )
    if index_of_day == -1:
        return False
    if param_username in user_profile["logs"][index_of_day]["users_liked"]:
        del user_profile["logs"][index_of_day]["users_liked"][param_username]
        user_profile["logs"][index_of_day]["points"] -= LIKE_REWARD_POINTS
        user_profile["total_points"] -= LIKE_REWARD_POINTS
        return user_profile
    return False


"""
@author Luke Jordan (bruceli)

Deletes the follower from the user profile
"""
def delete_following_data(user_profile: dict, follower_to_delete: str):
    if follower_to_delete in user_profile["following"]:
        del user_profile["following"][follower_to_delete]
        return user_profile
    return False


"""
@author Luke Jordan (bruceli)

Deletes the specific food item from today
"""
def delete_nutritional_data(user_profile: dict, name: str, target_date: str):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    index_to_del = -1
    for idx, food_item in reversed(
        list(enumerate(user_profile["logs"][index_of_day]["food_itemset"]))
    ):
        if food_item["name"] == name:
            index_to_del = idx
            break
    if index_to_del == -1:
        return False
    del user_profile["logs"][index_of_day]["food_itemset"][index_to_del]
    __del_empty_log(user_profile, index_of_day)
    return user_profile


"""
@author Luke Jordan (bruceli)

Deletes the weight data
"""
def delete_weight_data(user_profile: dict, weight_kg: float, target_date: str, time: str = None):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    index_to_del = -1
    for idx, weight_item in reversed(list(enumerate(user_profile["logs"][index_of_day]["weight_itemset"]))):
        if weight_item["weight_kg"] == weight_kg:
            if time is None or (time and weight_item["time"] == time):
                index_to_del = idx
                break
    if index_to_del == -1:
        return False

    user_profile = __delete_weight_points(user_profile, index_of_day, index_to_del)

    del user_profile["logs"][index_of_day]["weight_itemset"][index_to_del]
    __del_empty_log(user_profile, index_of_day)
    return user_profile

"""
@author Luke Jordan (bruceli)
"""
def delete_post_data(user_profile: dict, post: str, target_date: str, time: str = None):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    index_to_del = -1
    for idx, weight_item in reversed(list(enumerate(user_profile["logs"][index_of_day]["posts"]))):
        if weight_item["post"] == post:
            if time is None or (time and weight_item["time"] == time):
                index_to_del = idx
                break
    if index_to_del == -1:
        return False
    del user_profile["logs"][index_of_day]["posts"][index_to_del]
    __del_empty_log(user_profile, index_of_day)
    return user_profile

"""
@author Luke Jordan (bruceli)
"""
def delete_exercise_data(user_profile: dict, activity: str, target_date: str, calories_burned: str = None, duration_min: str = None):
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return False
    index_to_del = -1
    for idx, fitness_item in reversed(list(enumerate(user_profile["logs"][index_of_day]["fitness_itemset"]))):
        if (
            fitness_item["activity"] == activity and 
            (calories_burned is None or (fitness_item["calories_burned"] == calories_burned)) and
            (duration_min is None or ("duration_min" in fitness_item and fitness_item["duration_min"] == duration_min))
        ):
            index_to_del = idx
            break
    if index_to_del == -1:
        return False
    del user_profile["logs"][index_of_day]["fitness_itemset"][index_to_del]
    __del_empty_log(user_profile, index_of_day)
    return user_profile

"""
@author Shao-chun Wang and Luke Jordan (bruceli)
"""
def log_exercise_points(user_profile: dict, target_date: str) -> int:
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return user_profile
    if (user_profile["logs"][index_of_day]["reward_flags"]["target_calories_burned"] == True):
        return user_profile
    total_calories_burned = 0
    fitness_items = user_profile["logs"][index_of_day]["fitness_itemset"]
    for item in fitness_items:
        total_calories_burned += int(item["calories_burned"])
    if total_calories_burned > int(user_profile["personal"]["target_calorie_exercise"]):
        user_profile["logs"][index_of_day]["points"] += PERSONAL_GOAL_REWARD_POINTS
        user_profile["total_points"] += PERSONAL_GOAL_REWARD_POINTS
        user_profile["logs"][index_of_day]["reward_flags"]["target_calories_burned"] = True
        return user_profile
    return user_profile

"""
@author Shao-chun Wang [Point System]
"""
def delete_exercise_points(user_profile: dict, target_date: str) -> dict:
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return user_profile
    if (user_profile["logs"][index_of_day]["reward_flags"]["target_calories_burned"] == False):
        return user_profile
    total_calories_burned = 0
    fitness_items = user_profile["logs"][index_of_day]["fitness_itemset"]
    for item in fitness_items:
        total_calories_burned += int(item["calories_burned"])
    if (total_calories_burned <= int(user_profile["personal"]["target_calorie_exercise"]) 
        and int(user_profile["logs"][index_of_day]["points"] > 0)):
        user_profile["logs"][index_of_day]["points"] -= PERSONAL_GOAL_REWARD_POINTS
        user_profile["total_points"] -= PERSONAL_GOAL_REWARD_POINTS
        user_profile["logs"][index_of_day]["reward_flags"]["target_calories_burned"] = False
        return user_profile
    return user_profile

"""
@author Shao-chun Wang [Point System]
"""
def log_nutritional_points(user_profile: dict, target_date: str) -> int:
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return user_profile
    if (user_profile["logs"][index_of_day]["reward_flags"]["target_calories_eaten"] == True):
        return user_profile
    total_calories_eaten = 0
    fitness_items = user_profile["logs"][index_of_day]["food_itemset"]
    for item in fitness_items:
        total_calories_eaten += int(item["calories"])
    if total_calories_eaten > int(user_profile["personal"]["target_calorie_consumed"]):
        user_profile["logs"][index_of_day]["points"] += PERSONAL_GOAL_REWARD_POINTS
        user_profile["total_points"] += PERSONAL_GOAL_REWARD_POINTS
        user_profile["logs"][index_of_day]["reward_flags"]["target_calories_eaten"] = True
        return user_profile
    return user_profile

"""
@author Shao-chun Wang [point system]
"""
def delete_nutritional_points(user_profile: dict, target_date: str) -> int:
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return user_profile
    if (user_profile["logs"][index_of_day]["reward_flags"]["target_calories_eaten"] == False):
        return user_profile
    total_calories_eaten = 0
    fitness_items = user_profile["logs"][index_of_day]["food_itemset"]
    for item in fitness_items:
        total_calories_eaten += int(item["calories"])
    if (total_calories_eaten <= int(user_profile["personal"]["target_calorie_consumed"]) 
        and int(user_profile["logs"][index_of_day]["points"] > 0)):
        user_profile["logs"][index_of_day]["points"] -= PERSONAL_GOAL_REWARD_POINTS
        user_profile["total_points"] -= PERSONAL_GOAL_REWARD_POINTS
        user_profile["logs"][index_of_day]["reward_flags"]["target_calories_eaten"] = False
        return user_profile
    return user_profile

"""
@author Shao-chun Wang [point system]
"""
def log_weight_points(user_profile: dict, target_date: str) -> int:
    target_date: date = date.fromisoformat(target_date)
    index_of_day = __get_index_of_log(user_profile, target_date)
    if index_of_day == -1:
        return user_profile
    if user_profile["logs"][index_of_day]["reward_flags"]["target_weight"] == True:
        return user_profile
    weight_items = user_profile["logs"][index_of_day]["weight_itemset"]
    if len(weight_items) > 0:
        if int(weight_items[-1]["weight_kg"]) > int(user_profile["personal"]["target_weight_kg"]):
            user_profile["logs"][index_of_day]["points"] += PERSONAL_GOAL_REWARD_POINTS
            user_profile["total_points"] += PERSONAL_GOAL_REWARD_POINTS
            user_profile["logs"][index_of_day]["reward_flags"]["target_weight"] = True
            return user_profile
    return user_profile

"""
@author Shao-chun Wang
"""
def __delete_weight_points(user_profile: dict, index_of_day: int, index_to_del: int):
    # Check whether should deduct points when deleting weight
    if user_profile["logs"][index_of_day]["reward_flags"]["target_weight"] == True:
        if (
            int(user_profile["logs"][index_of_day]["weight_itemset"][index_to_del]["weight_kg"]) > int(user_profile["personal"]["target_weight_kg"])
            and int(user_profile["logs"][index_of_day]["points"] > 0)
        ):
            user_profile["logs"][index_of_day]["points"] -= PERSONAL_GOAL_REWARD_POINTS
            user_profile["total_points"] -= PERSONAL_GOAL_REWARD_POINTS
            user_profile["logs"][index_of_day]["reward_flags"]["target_weight"] = False
    return user_profile