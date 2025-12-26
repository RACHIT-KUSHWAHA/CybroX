from .all_db import legend_db

def afk_data():
    """Returns the AFK data from the database."""
    afk_info = legend_db.get_key("AFK_DATA")
    if afk_info is None:
        return {}
    return afk_info

def set_afk_data(afk_dict):
    """Sets the AFK data in the database."""
    legend_db.set_key("AFK_DATA", afk_dict)

def update_afk_data(key, value):
    """Updates a specific key in the AFK data."""
    afk_info = afk_data()
    afk_info[key] = value
    set_afk_data(afk_info)

def clear_afk_data():
    """Clears the AFK data from the database."""
    legend_db.delete_key("AFK_DATA")
    