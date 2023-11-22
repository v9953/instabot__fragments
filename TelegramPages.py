from telebot import types

from TelegramInnerFuncs import States
from MessageHandler import add_message, delete_messages

from ConfigGet import favourite, client_folders, users_in_folder
from ConfigGet import cloud_name, cloud_state, cloud_folder_link

from HandlerProcess import Processes

from InnerFuncs import form_line


def show_menu(bot, client_id):

    active = [process for process in Processes if process.client_id == client_id]

    if active:
        active_ss = ['[SS] ' + process.target for process in active if process.type == 'Save Stories']
        active_ms = ['[MS] ' + process.target for process in active if process.type == 'Monitor Stories']

        active_line = '🖥 Active processes:\n\n'
        if active_ss:
            active_line += '\n'.join(active_ss) + '\n'
        if active_ms:
            active_line += '\n'.join(active_ms)

    else:
        active_line = '🖥 No active processes'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Save Stories 💾️', callback_data=f'SaveStories?open'))
    markup.add(types.InlineKeyboardButton('Monitor Stories 📺', callback_data=f'MonitorStories?open'))
    markup.add(types.InlineKeyboardButton('Stop the Process ❤️‍🔥', callback_data=f'stop?open'))
    markup.add(types.InlineKeyboardButton('Settings ⚙️', callback_data=f'settings'))

    msg = bot.send_message(client_id, active_line, reply_markup=markup)
    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_settings(bot, client_id):

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Favourite users 💖', callback_data=f'favourite?show'))
    markup.add(types.InlineKeyboardButton('Folders 🗂', callback_data=f'folders?page'))
    markup.add(types.InlineKeyboardButton('Cloud storage ☁️', callback_data=f'cloud?settings'))
    markup.add(types.InlineKeyboardButton('Archives and reports 📜', callback_data=f'reports'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, '⚙️ Settings', reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


# Другие функции удалены
