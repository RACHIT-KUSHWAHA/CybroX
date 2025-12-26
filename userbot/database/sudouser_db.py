from .all_db import legend_db

def sudousers_list():
    """Returns the list of sudo users from the database."""
    sudousers = legend_db.get("SUDOUSERS")
    if sudousers is None:
        return []
    return sudousers

def add_sudouser(user_id):
    """Adds a user ID to the sudo users list in the database."""
    sudousers = sudousers_list()
    if user_id not in sudousers:
        sudousers.append(user_id)
        legend_db.set_key("SUDOUSERS", sudousers)

def remove_sudouser(user_id):
    """Removes a user ID from the sudo users list in the database."""
    sudousers = sudousers_list()
    if user_id in sudousers:
        sudousers.remove(user_id)
        legend_db.set_key("SUDOUSERS", sudousers)

def is_sudouser(user_id):
    """Checks if a user ID is in the sudo users list."""
    sudousers = sudousers_list()
    return user_id in sudousers