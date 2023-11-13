import random
from time import sleep
from configparser import ConfigParser
from pprint import pprint

from ConsoleOutput import console
from InnerFuncs import form_line


class InstProfile:
    def __init__(self, name, email, password, level, usage):
        self.name = name
        self.email = email
        self.password = password
        self.level = level
        self.usage = usage


def get_account(name):
    config = ConfigParser()
    config.read("InstagramAccounts.ini", encoding="utf-8")
    if name in config.sections():
        return InstProfile(name=config[name]['nickname'],
                           email=config[name]['login'],
                           password=config[name]['password'],
                           level=config[name]['level'],
                           usage=config[name]['usage'])
    else:
        return None


def get_accounts(mode='allowed'):
    config = ConfigParser()
    config.read("InstagramAccounts.ini", encoding="utf-8")
    accounts = []
    for account in config.sections():
        profile = get_account(account)
        if profile is not None:
            accounts.append(profile)
    if mode == 'all':
        return accounts

    elif mode == 'allowed':
        allowed_profiles = []
        for profile in accounts:
            if hasattr(profile, 'email') and hasattr(profile, 'password') and profile.usage == 'on':
                allowed_profiles.append(profile)
        return allowed_profiles




