import telebot
from telebot.storage import StateMemoryStorage
from telebot import custom_filters

import threading
from time import sleep
import pdb

from ConsoleOutput import console

from ConfigGet import token, bot_password, authorized_users, cloud_name, users_in_folder
from ConfigUserSetup import add_favourite, add_folder, add_user_to_folder, rename_folder
from ConfigUserSetup import delete_favourite, delete_folder, delete_user_from_folder
from ConfigUserSetup import add_client_to_config, change_cloud_uploading_state, change_cloud_name


from MessageHandler import messages, add_message, delete_messages
from TelegramInnerFuncs import States

from TelegramPages import show_menu, show_settings
from TelegramPages import show_favourite_users, show_add_favourite, show_delete_favourite
from TelegramPages import show_cloud_page, show_change_cloud_name_page, show_name_was_changed_page
from TelegramPages import show_folders_page, show_open_folder, show_add_folder_page
from TelegramPages import show_add_user_page, show_delete_user_page
from TelegramPages import show_rename_folder_page
from TelegramPages import show_delete_folder_confirmation
from TelegramPages import show_x_stories, show_x_stories_folder
from TelegramPages import show_stop_page


from TelegramControlFuncs import save_stories, monitor_stories
from TestFunc import test_save_stories, test_monitor_stories

from CloudStorage import MegaLogin, mega_mkdir, mega_listdir, mega_rename

from HandlerProcess import Processes, create_process, add_process, close_process
from HandlerDrivers import authorize

from ActiveStateGet import get_processes

from TelegramLogBot import log


state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token(), state_storage=state_storage)


# modes : 'test' / 'real'
BOT_MODE = 'real'


authorize(mode=BOT_MODE)


# MegaLogin()


def process_save_stories(client_id, user, process=None):

    global BOT_MODE

    mode = BOT_MODE.lower()
    if user in ['shrek', 'donkey', 'dragon']:
        mode = 'test'

    if process is None:
        process = create_process(client_id, 'Save Stories', user)

    if process is not None:
        if mode == 'test':
            threading.Thread(target=test_save_stories, args=(bot, process)).start()

        elif mode == 'real':
            # threading.Thread(target=save_stories, args=([bot, client_id, user, process_id],)).start()
            threading.Thread(target=save_stories, args=(bot, process)).start()

        # sleep(0.3)
        console('', level='basic')


def process_monitor_stories(client_id, user, process=None):

    delete_messages(bot, client_id)

    global BOT_MODE

    mode = BOT_MODE.lower()
    if user in ['shrek', 'donkey', 'dragon']:
        mode = 'test'

    if process is None:
        process = create_process(client_id, 'Monitor Stories', user)

    if process is not None:
        if mode == 'test':
            threading.Thread(target=test_monitor_stories, args=(bot, process)).start()

        elif mode == 'real':
            threading.Thread(target=monitor_stories, args=(bot, process)).start()

        # bot.send_message(client_id, f'Запуск функции monitor_stories от {user}')

        # sleep(0.3)


def checkpoint_loading():

    processes = get_processes()

    if len(processes) == 0:
        console('Checkpoint Processes (0)', level='basic', end='\n\n')
    else:
        console(f'Checkpoint Processes ({len(processes)}):', level='basic')
    i = 1
    for process in processes:
        line = '{}. client_id: {}, type: {}, target: {},'.format(i, process['client_id'], process['type'], process['target'])
        for tag in process:
            if tag not in ['client_id', 'type', 'target']:
                if tag != 'database':
                    line += ' {}: {},'.format(tag, process[tag])
                else:
                    line += ' {}: {} images,'.format(tag, len(process[tag]))
        line = line[:-1]
        console(line, level='basic')
        i += 1
    console('', level='basic')

    for process in processes:
        if 'client_id' in process and 'type' in process and 'target' in process:
            client_id, process_type, target = process['client_id'], process['type'], process['target']
            p = add_process(client_id, process_type, target, process)
            if process_type == 'Save Stories':
                process_save_stories(client_id, target, process=p)
            if process_type == 'Monitor Stories':
                process_monitor_stories(client_id, target, process=p)

    for client_id in [process.client_id for process in Processes]:
        show_menu(bot, client_id)


# Органичение доступа к боту по ID
@bot.message_handler(func=lambda message: message.chat.id not in authorized_users())
def warning(message):
    line = f'Заблокирована попытка входа\n' \
           f'  ID: {message.from_user.id}\n' \
           f'  Name: {message.from_user.first_name} {message.from_user.last_name}\n' \
           f'  Nickname: {message.from_user.username}\n'
    console(line, level='basic')

    password = bot_password()
    client_id = message.from_user.id

    if password is not None and message.text == password:
        add_message(message, client_id)
        show_menu(bot, client_id)
        # delete_messages(bot, client_id)
        add_client_to_config(message.from_user)
    else:
        add_message(message, client_id)
        msg = bot.send_photo(client_id, open('warning_pic.png', 'rb'), caption='Access denied')
        add_message(msg, client_id)
        if len(messages[client_id]) > 4:
            delete_messages(bot, client_id)


@bot.message_handler(commands=['setup'])
def setup(message):

    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)
    show_settings(bot, client_id)


@bot.message_handler(commands=['save_stories'])
def save_stories_bot(message):

    client_id = message.from_user.id
    add_message(message, client_id)
    bot.set_state(client_id, States.save_stories)
    show_x_stories(bot, client_id, x='Save Stories')


@bot.message_handler(commands=['monitor_stories'])
def monitor_stories_bot(message):
    client_id = message.from_user.id
    add_message(message, client_id)
    bot.set_state(client_id, States.save_stories)
    show_x_stories(bot, client_id, x='Monitor Stories')


@bot.message_handler(commands=['stop'])
def stop_monitoring_bot(message):
    client_id = message.from_user.id
    add_message(message, client_id)
    show_stop_page(bot, client_id)


@bot.message_handler(commands=['menu'])
def stop_monitoring_bot(message):
    client_id = message.from_user.id
    add_message(message, client_id)
    show_menu(bot, client_id)


@bot.message_handler(state=States.add_favourite)
def input_add_favourite(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)

    user = message.text
    add_favourite(client_id, user)
    show_favourite_users(bot, client_id, launch_after='add favourite')


@bot.message_handler(state=States.delete_favourite)
def input_delete_favourite(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)

    user = message.text
    delete_favourite(client_id, user)
    show_favourite_users(bot, client_id, launch_after='delete favourite')


@bot.message_handler(state=States.add_folder)
def input_folder_name(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)

    folder = message.text
    add_folder(client_id, folder)
    # show_add_more_folders(bot, client_id, folder)
    show_open_folder(bot, client_id, folder)


@bot.message_handler(state=States.rename_folder)
def input_folder_name_rename(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)

    new_name = message.text
    with bot.retrieve_data(client_id) as data:
        folder = data['folder']
        rename_folder(client_id, folder, new_name)
        show_open_folder(bot, client_id, new_name)
        data.pop('folder')


@bot.message_handler(state=States.add_user_to_folder)
def input_username_name(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)

    username = message.text
    with bot.retrieve_data(client_id) as data:
        folder = data['folder']
        data.pop('folder')
        add_user_to_folder(client_id, folder, username)
        show_open_folder(bot, client_id, folder)


@bot.message_handler(state=States.change_cloud_name)
def input_change_cloud_name(message):
    client_id = message.from_user.id
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)
    new_name = message.text
    mega_rename(cloud_name(client_id), new_name)
    change_cloud_name(client_id, new_name)
    show_name_was_changed_page(bot, client_id)


@bot.message_handler(state=States.save_stories)
def input_save_stories(message):
    client_id, user = message.from_user.id, message.text
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)
    process_save_stories(client_id, user)
    sleep(0.3)
    show_menu(bot, client_id)


@bot.message_handler(state=States.start_monitoring)
def input_monitor_stories(message):
    client_id, user = message.from_user.id, message.text
    bot.set_state(client_id, States.normal)
    add_message(message, client_id)
    process_monitor_stories(client_id, user)
    sleep(0.3)
    show_menu(bot, client_id)



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):

    callback_sublines = callback.data.split('?')
    client_id = callback.message.chat.id

    if callback.data.startswith('settings'):
        bot.set_state(client_id, States.normal)
        show_settings(bot, client_id)

    elif callback.data.startswith('menu'):

        bot.set_state(client_id, States.normal)
        show_menu(bot, client_id)

    elif callback.data.startswith('favourite'):

        command = callback_sublines[1]

        if command == 'show':
            bot.set_state(client_id, States.normal)
            show_favourite_users(bot, client_id)

        if command == 'add':
            bot.set_state(client_id, States.add_favourite)
            show_add_favourite(bot, client_id)

        elif command == 'delete':
            bot.set_state(client_id, States.delete_favourite)
            show_delete_favourite(bot, client_id)

        elif command == 'delete_user':
            user = callback_sublines[2]
            delete_favourite(client_id, user)
            show_favourite_users(bot, client_id, launch_after='delete favourite')

    elif callback.data.startswith('folders'):

        if callback_sublines[1] == 'page':
            bot.set_state(client_id, States.normal)
            show_folders_page(bot, client_id)

        elif callback_sublines[1] == 'add_folder':
            bot.set_state(client_id, States.add_folder)
            show_add_folder_page(bot, client_id)

    elif callback.data.startswith('folder'):

        folder = callback_sublines[1]
        command = callback_sublines[2]

        if command == 'open':
            bot.set_state(client_id, States.normal)
            show_open_folder(bot, client_id, folder)

        elif command == 'add_user':
            bot.set_state(client_id, States.add_user_to_folder)
            with bot.retrieve_data(client_id) as data:
                data['folder'] = folder
            show_add_user_page(bot, client_id, folder)

        elif command == 'delete_user':
            bot.set_state(client_id, States.normal)
            show_delete_user_page(bot, client_id, folder)

        elif command == 'delete_this_user':
            bot.set_state(client_id, States.normal)
            user = callback_sublines[3]
            delete_user_from_folder(client_id, folder, user)
            show_open_folder(bot, client_id, folder)

        elif command == 'rename':
            bot.set_state(client_id, States.rename_folder)
            with bot.retrieve_data(client_id) as data:
                data['folder'] = folder
            show_rename_folder_page(bot, client_id, folder)

        elif command == 'delete_folder':
            bot.set_state(client_id, States.normal)
            show_delete_folder_confirmation(bot, client_id, folder)

        elif command == 'confirmed_delete':
            bot.set_state(client_id, States.normal)
            delete_folder(client_id, folder)
            show_folders_page(bot, client_id)

    elif callback.data.startswith('cloud'):

        bot.set_state(client_id, States.normal)

        # if callback_sublines[1] == 'settings':
        #     bot.set_state(client_id, States.normal)
        #     show_cloud_page(bot, client_id)
        #
        # elif callback_sublines[1] == 'turn_on':
        #     change_cloud_uploading_state(client_id, 'on')
        #     name = cloud_name(client_id)
        #     if name not in mega_listdir():
        #         mega_mkdir(name)
        #     show_cloud_page(bot, client_id)
        #
        # elif callback_sublines[1] == 'turn_off':
        #     change_cloud_uploading_state(client_id, 'off')
        #     show_cloud_page(bot, client_id)
        #
        # elif callback_sublines[1] == 'change_name':
        #     bot.set_state(client_id, States.change_cloud_name)
        #     show_change_cloud_name_page(bot, client_id)

    elif callback.data.startswith('SaveStories'):

        command = callback_sublines[1]

        if command == 'open':
            show_x_stories(bot, client_id, x='Save Stories')
            bot.set_state(client_id, States.save_stories)

        elif command == 'folder':
            folder = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            show_x_stories_folder(bot, client_id, folder, x='Save Stories')

        elif command == 'whole_folder':
            folder = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            for user in users_in_folder(client_id, folder):
                delete_messages(bot, client_id)
                process_save_stories(client_id, user)
            show_menu(bot, client_id)

        elif command == 'user':
            username = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            delete_messages(bot, client_id)
            process_save_stories(client_id, username)
            show_menu(bot, client_id)

    elif callback.data.startswith('MonitorStories'):

        command = callback_sublines[1]

        if command == 'open':
            show_x_stories(bot, client_id, x='Monitor Stories')
            bot.set_state(client_id, States.save_stories)

        elif command == 'folder':
            folder = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            show_x_stories_folder(bot, client_id, folder, x='Monitor Stories')

        elif command == 'whole_folder':
            folder = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            for user in users_in_folder(client_id, folder):
                delete_messages(bot, client_id)
                process_monitor_stories(client_id, user)
                # sleep(0.3)
            show_menu(bot, client_id)

        elif command == 'user':
            username = callback_sublines[2]
            bot.set_state(client_id, States.normal)
            delete_messages(bot, client_id)
            process_monitor_stories(client_id, username)
            show_menu(bot, client_id)

    elif callback.data.startswith('stop'):

        command = callback_sublines[1]

        if command == 'open':
            bot.set_state(client_id, States.normal)
            delete_messages(bot, client_id)
            show_stop_page(bot, client_id)

        elif command == 'process':
            bot.set_state(client_id, States.normal)
            process_id = int(callback_sublines[2])
            process = [p for p in Processes if p.id == process_id]
            if process:
                close_process(process[0])
            delete_messages(bot, client_id)
            # show_stop_page(bot, client_id)
            sleep(0.3)
            show_menu(bot, client_id)


@bot.message_handler()
def handle_text(message):

    add_message(message, message.from_user.id)











checkpoint_loading()



bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.infinity_polling(skip_pending=True)
