import json

def load_config():
    with open("config.json") as config_file:
        config_data = json.load(config_file)
    return config_data

