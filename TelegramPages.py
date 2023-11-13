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


def show_x_stories(bot, client_id, x=None):
    favourite_users = favourite(client_id)
    folders = client_folders(client_id)
    markup = types.InlineKeyboardMarkup()

    reply_text = f'<b>{x}</b>\n'

    if favourite_users:
        for user in favourite_users:
            markup.add(types.InlineKeyboardButton(user + ' 💖', callback_data=f'{x.replace(" ", "")}?user?{user}'))
    if folders:
        for folder in folders:
            markup.add(types.InlineKeyboardButton(folder + ' 🗂', callback_data=f'{x.replace(" ", "")}?folder?{folder}'))

    if favourite_users and folders:
        reply_text += '\nSelect a user from favourites, select folder or enter username'
    elif favourite_users and not folders:
        reply_text += '\nSelect a user from favourites or enter username'
    elif favourite_users and folders:
        reply_text += 'Select folder or enter username'
    else:
        reply_text += 'Enter username'

    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, reply_text, reply_markup=markup, parse_mode='HTML')

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_x_stories_folder(bot, client_id, folder, x=None):
    users = users_in_folder(client_id, folder)

    markup = types.InlineKeyboardMarkup()
    reply_text = f'<b>{x} / "{folder}"</b>\n\n'
    if users:
        for user in users:
            markup.add(types.InlineKeyboardButton(user + ' ', callback_data=f'{x.replace(" ", "")}?user?{user}'))
        # reply_text += 'Select user'
    else:
        reply_text += f'No users in folder'
    if x == 'Save Stories':
        markup.add(types.InlineKeyboardButton('Save the whole Folder 👨‍👩‍👧‍👦', callback_data=f'SaveStories?whole_folder?{folder}'))
        markup.add(types.InlineKeyboardButton('Go back to Save Stories 💾', callback_data=f'SaveStories?open'))
    elif x == 'Monitor Stories':
        markup.add(types.InlineKeyboardButton('Monitor the whole Folder 👨‍👩‍👧‍👦', callback_data=f'MonitorStories?whole_folder?{folder}'))
        markup.add(types.InlineKeyboardButton('Go back to Monitor Stories 📺', callback_data=f'MonitorStories?open'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, reply_text, reply_markup=markup, parse_mode='HTML')

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_favourite_users(bot, client_id, launch_after='settings'):

    favourite_users = favourite(client_id)

    favourite_users_line = '<b>💖 Favourite users</b>\n\n'

    if favourite_users:
        for user in favourite_users:
            if user != favourite_users[-1]:
                favourite_users_line += f'{user},\n'
            else:
                favourite_users_line += f'{user}\n'
    else:
        favourite_users_line += 'No favourite users 💔'

    markup = types.InlineKeyboardMarkup()
    if launch_after == 'settings':
        markup.add(types.InlineKeyboardButton('Add favourite 💞', callback_data=f'favourite?add'))
        markup.add(types.InlineKeyboardButton('Delete favourite 💔', callback_data=f'favourite?delete'))
    elif launch_after == 'add favourite':
        markup.add(types.InlineKeyboardButton('Add more 💞', callback_data=f'favourite?add'))
        markup.add(types.InlineKeyboardButton('Delete favourite 💔', callback_data=f'favourite?delete'))
    elif launch_after == 'delete favourite':
        markup.add(types.InlineKeyboardButton('Add favourite 💞', callback_data=f'favourite?add'))
        markup.add(types.InlineKeyboardButton('Delete more 💔', callback_data=f'favourite?delete'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))

    msg = bot.send_message(client_id, favourite_users_line, reply_markup=markup, parse_mode='HTML')
    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_add_favourite(bot, client_id):

    bot.set_state(client_id, States.add_favourite)
    favourite_users = favourite(client_id)

    favourite_users_line = '<b>Add favourite</b>\n\n'

    if favourite_users:
        favourite_users_line += '💖 Favourite users:\n'
        for user in favourite_users:
            if user != favourite_users[-1]:
                favourite_users_line += f'{user},\n'
            else:
                favourite_users_line += f'{user}\n'
    else:
        favourite_users_line += 'No favourite users 💔'

    favourite_users_line += '\nEnter username:'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Favourite users 💖', callback_data=f'favourite?show'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))

    msg = bot.send_message(client_id, favourite_users_line, reply_markup=markup, parse_mode='HTML')
    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_delete_favourite(bot, client_id):

    bot.set_state(client_id, States.delete_favourite)
    favourite_users = favourite(client_id)
    markup = types.InlineKeyboardMarkup()

    text = '<b>Delete favourite</b>\n\n'

    if favourite_users:
        text += 'Select or write the username you want to remove from favourites'
        for user in favourite_users:
            markup.add(types.InlineKeyboardButton(user, callback_data=f'favourite?delete_user?{user}'))
    else:
        text += 'No favourite users 💔'

    markup.add(types.InlineKeyboardButton('Favourite users 💖', callback_data=f'favourite?show'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup, parse_mode='HTML')
    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_folders_page(bot, client_id):
    folders = client_folders(client_id)
    markup = types.InlineKeyboardMarkup()

    if folders:
        text = '🗂 Your folders\n'
        for folder in folders:
            markup.add(types.InlineKeyboardButton(f'{folder}', callback_data=f'folder?{folder}?open'))
    else:
        text = 'No folders 😕'

    markup.add(types.InlineKeyboardButton('Add folder ✍️', callback_data=f'folders?add_folder'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_add_folder_page(bot, client_id):

    folders = client_folders(client_id)
    markup = types.InlineKeyboardMarkup()

    if folders:
        text = '🗂 Your folders:\n'
        text += form_line(folders, sep='\n')
        text += '\n\nEnter folder name'
    else:
        text = 'Enter folder name'

    markup.add(types.InlineKeyboardButton('Go back to folders 🗂', callback_data=f'folders?page'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_open_folder(bot, client_id, folder):

    users = users_in_folder(client_id, folder)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Add user 👱🏻‍♀️', callback_data=f'folder?{folder}?add_user'))

    text = f'<b>{folder}</b>\n\n'
    if users:
        # text = f'👱🏻‍♀️ Users in folder "{folder}":\n'
        text += form_line(users, sep='\n')
        text += '\n'
        markup.add(types.InlineKeyboardButton('Delete user ☠️‍️', callback_data=f'folder?{folder}?delete_user'))
    else:
        text += 'No users 😕'

    markup.add(types.InlineKeyboardButton('Rename folder ✍️', callback_data=f'folder?{folder}?rename'))
    markup.add(types.InlineKeyboardButton('Delete folder 🔥️', callback_data=f'folder?{folder}?delete_folder'))
    markup.add(types.InlineKeyboardButton('Go back to folders 🗂', callback_data=f'folders?page'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup, parse_mode='HTML')

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_add_user_page(bot, client_id, folder):

    users = users_in_folder(client_id, folder)
    markup = types.InlineKeyboardMarkup()

    text = f'<b>{folder}</b>\n\n'
    if users:
        text += f'👱🏻‍♀️ Users in folder:\n'
        text += form_line(users, sep='\n')
        text += '\n\nEnter username'
    else:
        text += 'Enter username'

    markup.add(types.InlineKeyboardButton(f'Go back to "{folder}" 📘', callback_data=f'folder?{folder}?open'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup, parse_mode='HTML')

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_delete_user_page(bot, client_id, folder):

    users = users_in_folder(client_id, folder)
    markup = types.InlineKeyboardMarkup()
    text = f'<b>{folder}</b>\n\n'
    if users:
        text += f'Select the user you want to delete'
        for user in users:
            markup.add(types.InlineKeyboardButton(user, callback_data=f'folder?{folder}?delete_this_user?{user}'))
    else:
        text += f'No users in folder "{folder}"'

    markup.add(types.InlineKeyboardButton(f'Go back to "{folder}" 📘', callback_data=f'folder?{folder}?open'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup, parse_mode='HTML')

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_delete_folder_confirmation(bot, client_id, folder):

    markup = types.InlineKeyboardMarkup()
    text = f'Are you sure you want to delete the folder "{folder}"?'

    markup.add(types.InlineKeyboardButton(f'Yes 😎', callback_data=f'folder?{folder}?confirmed_delete'))
    markup.add(types.InlineKeyboardButton(f'No  🫡', callback_data=f'folder?{folder}?open'))
    markup.add(types.InlineKeyboardButton('Go back to folders 🗂', callback_data=f'folders?page'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_rename_folder_page(bot, client_id, folder):

    markup = types.InlineKeyboardMarkup()
    text = f'Enter a new name for the folder "{folder}"?'

    markup.add(types.InlineKeyboardButton(f'Go back to "{folder}" 📘', callback_data=f'folder?{folder}?open'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_stop_page(bot, client_id):

    active = [process for process in Processes if process.client_id == client_id]

    markup = types.InlineKeyboardMarkup()
    if active:
        active_ss = {'[SS] ' + process.target: process.id for process in active if process.type == 'Save Stories'}
        active_ms = {'[MS] ' + process.target: process.id for process in active if process.type == 'Monitor Stories'}
        for process in active_ss:
            markup.add(types.InlineKeyboardButton(process, callback_data=f'stop?process?{active_ss[process]}'))
        for process in active_ms:
            markup.add(types.InlineKeyboardButton(process, callback_data=f'stop?process?{active_ms[process]}'))
        reply_text = 'Active processes:'
    else:
        reply_text = 'No active processes'

    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    delete_messages(bot, client_id)
    msg = bot.send_message(client_id, reply_text, reply_markup=markup)
    add_message(msg, client_id)


def show_cloud_page(bot, client_id):

    markup = types.InlineKeyboardMarkup()
    state = cloud_state(client_id)
    if state:
        link = cloud_folder_link(client_id)
        text = f'Cloud storage enabled. Your link:\n{link}'
        markup.add(types.InlineKeyboardButton('Turn off', callback_data=f'cloud?turn_off'))
        markup.add(types.InlineKeyboardButton('Change your folder name', callback_data=f'cloud?change_name'))
    else:
        text = 'Cloud storage disabled'
        markup.add(types.InlineKeyboardButton('Turn on', callback_data=f'cloud?turn_on'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_change_cloud_name_page(bot, client_id):

    name = cloud_name(client_id)
    text = f'Your current cloud name: {name}\n Enter a new one:'

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Go back to cloud ☁️', callback_data=f'cloud?settings'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)


def show_name_was_changed_page(bot, client_id):
    name = cloud_name(client_id)
    text = f'The name has been changed\nNow your name is "{name}"'

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Go back to cloud ☁️', callback_data=f'cloud?settings'))
    markup.add(types.InlineKeyboardButton('Go back to settings ⚙️', callback_data=f'settings'))
    markup.add(types.InlineKeyboardButton('Go back to menu 🔙', callback_data=f'menu'))
    msg = bot.send_message(client_id, text, reply_markup=markup)

    delete_messages(bot, client_id)
    add_message(msg, client_id)