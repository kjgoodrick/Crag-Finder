import configparser
import os

SETTINGS_FILE = 'settings.ini'


def gen_settings(key='your_key_here'):
    config = configparser.ConfigParser()

    config['MP API'] = {'key': key}

    # Check if settings already exists and read in old values to prevent overwriting old settings
    if os.path.isfile(SETTINGS_FILE):
        config.read(SETTINGS_FILE)

    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    gen_settings()
