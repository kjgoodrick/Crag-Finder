"""Settings Generation
"""
import configparser
import os

SETTINGS_FILE = 'settings.ini'
"""The file name of the settings file
"""


def gen_settings(key='your_key_here'):
    """
    Generate Default settings file without overwriting existing settings

    Parameters
    ----------
    key : str
        MP API Key

    Returns
    -------
    nothing
    """
    # Create Configuration parser
    config = configparser.ConfigParser()

    # Add Key to configuration
    config['MP API'] = {'key': key}

    # Check if settings already exists and read in old values to prevent overwriting old settings
    if os.path.isfile(SETTINGS_FILE):
        config.read(SETTINGS_FILE)

    # Write new settings file
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)


# Allow module standalone run
if __name__ == '__main__':
    gen_settings()
