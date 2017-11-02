import json
from configparser import ConfigParser


def config(filename="config/database.ini", section="postgresql"):
    parser = ConfigParser()

    parser.read(filename)

    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Section {0} not found in the {1} file".format(
            section,
            filename
        ))

    return db


def config_accounts(filename="config/accounts.json"):
    with open(filename) as data_file:
        data = list(map(lambda x: (x["user"], x["password"]), json.load(data_file)["accounts"]))
    return data
