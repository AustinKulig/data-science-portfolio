from configparser import ConfigParser

config_object = ConfigParser()

config_object["linkedin"] = {
    "email": 'Linkedin email',
    "password": 'Linkedin password',
    "search_term": 'Data Scientist',
    "location": 'Boston, MA',
}

# Write the above sections to config.ini file
with open('config.ini', 'w') as conf:
    config_object.write(conf)