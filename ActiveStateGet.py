from configparser import ConfigParser
from time import sleep

from ConsoleOutput import console
from ConfigGet import authorized_users
from ConfigInnerFuncs import make_sure


class Message:
    def __init__(self, message_id):
        self.message_id = message_id
        self.text = '*** The text of the message was lost when the bot was restarted ***'


def get_messages():
    config = ConfigParser()
    config.read('messages.ini', encoding='utf-8')
    messages = {}
    for client_id in config.sections():
        client_id = int(client_id)
        messages[client_id] = {}
        client_messages = config.get(str(client_id), 'messages').split(', ')
        if client_messages == ['']:
            messages[client_id] = {}
        else:
            for message_id in client_messages:
                message_id = int(message_id)
                messages[client_id][message_id] = Message(message_id)

    return messages


def get_processes():
    config = ConfigParser()
    config.read('processes.ini', encoding='utf-8')

    processes = []
    for client_id in config.sections():
        client_processes = config.get(client_id, 'processes').split(', ')
        for process_id in client_processes:
            if process_id in config.options(client_id):

                process_info = config.get(client_id, process_id)
                tags = {key: value for key, value in [tag.split(': ') for tag in process_info.split(', ')]}

                if 'target' in tags and 'type' in tags and 'queue' in tags:
                    tags['id'] = int(process_id)
                    tags['client_id'] = int(client_id)
                    tags['queue'] = int(tags['queue'])

                    if 'launch_number' in tags:
                        tags['launch_number'] = int(tags['launch_number'])

                    if f'{process_id} db' in config.options(client_id):
                        tags['database'] = config.get(client_id, f'{process_id} db').split(', ')

                    processes.append(tags)

    return sorted(processes, key=lambda x: x['queue'])


def get_process_db(client_id, process_id):
    client_id = str(client_id)
    config = ConfigParser()
    config.read('processes.ini', encoding='utf-8')

    option_name = f'{process_id} db'
    outer_func = 'GET PROCESS DB'

    response = make_sure([config, client_id], mode='client', outer_func=outer_func,
                         file='processes.ini', correction=True)
    if response == 'correction required':
        return None

    response = make_sure([config, client_id, option_name], mode='option', outer_func=outer_func,
                         file='processes.ini', correction=True)
    if response == 'correction required':
        return None

    # "{'DkAAAgDxTOA-960.jpg', '595_0959024_s.jpg'}" -->  ["DkAAAgDxTOA-960.jpg", "595_0959024_s.jpg"]
    return {img: None for img in config.get(client_id, option_name).replace('\'', '')[1:-1].split(', ')}








