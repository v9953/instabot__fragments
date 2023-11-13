import threading
from copy import copy
from time import sleep

from ConsoleOutput import console
from ConfigGet import user_info
from ActiveStateGet import get_messages
from ActiveStateSet import update_messages


messages = get_messages()


def add_message(message, client_id):

    global messages
    if message.chat.id not in messages:
        messages[message.from_user.id] = {}
    messages[client_id][message.message_id] = message
    messages_output = {}
    for client in messages:
        messages_output[client] = {}
        for msg in messages[client]:
            # if messages[client][msg] is None:
            #     messages_output[client][msg] = '*** The text of the message was lost when the bot was restarted ***'
            # else:
            messages_output[client][msg] = messages[client][msg].text

    client_info = user_info(client_id)
    idx = client_info.find(', @')
    if idx == -1:
        username = client_info
    else:
        username = client_info[:idx]

    message_text = message.text.replace('\n\n', '\n').replace("\n", "\n"+(12+len(username))*" ")
    console(f'[MESSAGE] {username}: {message_text}', level='message', end='\n\n')

    # locker = threading.RLock()
    # locker.acquire()
    # update_messages(messages)
    # locker.release()


def delete_messages(bot, client_id):
    global messages
    if client_id in messages:
        try:
            for message_id in messages[client_id]:
                try:
                    bot.delete_message(client_id, message_id)
                except Exception as ex:
                    console('Message to delete not found. Какой-то еблан удалил сообщение руками')
        except Exception as ex:
            console(ex)
            console('[DELETE MESSAGES] Error: probably it\'s synchronization problem', level='error')
            delete_messages(bot, client_id)
        messages[client_id] = {}

    # locker = threading.RLock()
    # locker.acquire()
    # update_messages(messages)
    # locker.release()


def check_message_updates():
    global messages
    ref_messages = copy(messages)
    while True:
        if ref_messages != messages:
            ref_messages = copy(messages)
            update_messages(messages)
        sleep(0.1)


threading.Thread(target=check_message_updates).start()



