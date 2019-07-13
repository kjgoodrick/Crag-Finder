import configparser
import os

settings_file = 'settings.ini'

config = configparser.ConfigParser()

config['MP API'] = {'key': 'your_key_here'}

# Check if settings already exists and read in old values to prevent overwriting old settings
if os.path.isfile(settings_file):
    config.read(settings_file)

with open(settings_file, 'w') as configfile:
    config.write(configfile)
