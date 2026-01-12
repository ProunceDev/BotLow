# Example custom format file (event.whitelist)
# [Discord ID               |Discord Username         |Minecraft UUID           |Minecraft Username       ]
# [-------------------------|-------------------------|-------------------------|-------------------------]
# |123456789                |ExampleUser              |abcdef123456             |Steve                    |
# |987654321                |AnotherUser              |654321abcdef             |Alex                     |

# Python parser for the custom format

import requests, os

def load_users(filename="event.whitelist"):
    users = []

    if not os.path.exists(filename):
        save_users([], filename)

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("[") or "|" not in line:
                continue
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) == 4:
                users.append(parts)
    return users

def save_users(users, filename="event.whitelist"):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write(f'[{"Discord ID":<40}|{"Discord Username":<40}|{"Minecraft UUID":<40}|{"Minecraft Username":<40}]\n')
            file.write('[----------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------]\n')

    with open(filename, 'w') as file:
        file.write(f'[{"Discord ID":<40}|{"Discord Username":<40}|{"Minecraft UUID":<40}|{"Minecraft Username":<40}]\n')
        file.write('[----------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------]\n')
        for user in users:
            file.write(f'|{user[0]:<40}|{user[1]:<40}|{user[2]:<40}|{user[3]:<40}|\n')

def add_user(new_user, filename="event.whitelist"):
    users = load_users(filename)
    for user in users:
        if user[2] == new_user[2]:
            return False  # UUID already exists
    users.append(new_user)
    save_users(users, filename)
    return True

def remove_user(minecraft_uuid, filename="event.whitelist"):
    users = load_users(filename)
    users = [user for user in users if user[2].replace("-", "") != minecraft_uuid]
    save_users(users, filename)
    return True
	
def get_number_of_whitelisted_users(discord_id, filename="event.whitelist"):
	total = 0
	users = load_users(filename)
	for user in users:
		if str(user[0]) == str(discord_id):
			total+=1
	return total

def check_if_whitelisted(minecraft_uuid, filename="event.whitelist"):
    users = load_users(filename)
    for user in users:
        if user[2] == minecraft_uuid:
            return True
    return False

def create_user(discord_id, discord_username, minecraft_uuid, minecraft_username):
	return [str(discord_id), str(discord_username), str(minecraft_uuid), str(minecraft_username)]

def get_minecraft_account(username):
	url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
	response = requests.get(url)

	if response.status_code == 200:
		data = response.json()
		return data.get("id"), data.get("name")
	else:
		return None, None
	
def get_minecraft_username_by_uuid(uuid):
    url = f"https://playerdb.co/api/player/minecraft/{uuid}"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            return data.get("data").get("player").get("username")
    return None