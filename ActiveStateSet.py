from configparser import ConfigParser
from time import sleep

from ConfigGet import authorized_users
from InnerFuncs import form_line



def add_all_authorized_clients():
    config = ConfigParser()
    client_ids = [str(client_id) for client_id in authorized_users()]
    for client_id in client_ids:
        config.add_section(client_id)
        config.set(client_id, 'messages', '')
        config.set(client_id, 'processes', '')

    with open('active_state.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def update_messages(messages):
    config = ConfigParser()
    config.read('messages.ini', encoding='utf-8')
    for client_id in messages:
        client_id = str(client_id)
        if client_id not in config.sections():
            config.add_section(client_id)
            config.set(client_id, 'messages', '')

        messages_line = form_line([str(msg) for msg in messages[int(client_id)]])
        config.set(client_id, 'messages', messages_line)
    with open('messages.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def update_processes(processes):
    # console('UPDATE PROCESSES', level='error')

    # queues = [process.queue for process in processes]

    config = ConfigParser()
    for process in processes:
        client_id = str(process.client_id)

        if client_id not in config.sections():
            config.add_section(client_id)
            config.set(client_id, 'processes', '')

        process_list = config.get(client_id, 'processes').split(', ') + [str(process.id)]
        if '' in process_list:
            process_list.remove('')
        config.set(client_id, 'processes', ', '.join(process_list))

        process_info = f'target: {process.target}, '
        process_info += f'type: {process.type}, '
        process_info += f'queue: {process.queue}'

        if hasattr(process, 'launch_number'):
            process_info += f', launch_number: {process.launch_number}'

        config.set(client_id, str(process.id), process_info)

        if hasattr(process, 'database'):
            if process.database is not None:
                config.set(client_id, f'{process.id} db', ', '.join(process.database))

    with open('processes.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)
    sleep(0.1)




# processes = {373995981: {},
#              6269953373: {},
#              185132977: {},
#              123: {228: {'process_type': 'Save Stories',
#                          'process_target': 'VovaSidor',
#                          'state': 'waiting',
#                          'queue': 100,
#                          'waiting_time': '50 hours'},
#                    666: {'process_type': 'Monitor Stories',
#                          'process_target': 'kiberbuller',
#                          'state': 'waiting',
#                          'queue': 15,
#                          'waiting_time': '6 hours'}
#                    }
#              }
# update_processes(processes)

# {USER_ID: {PROCESS_ID: {'process_type': 'Save Stories',
#                         'process_target': 'VovaSidor',
#                         'state': 'waiting',
#                         'queue': 100,
#                         'waiting_time': '50 hours'}}}
