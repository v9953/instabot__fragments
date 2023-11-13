from telebot.types import InputMediaPhoto, InputMediaVideo

from ConsoleOutput import console

def upload_to_telegram(bot, client_id, img_folder, order, user):
    console(f'[{user}] Start uploading stories to Telegram')

    num_of_stories = len(order)
    tens = num_of_stories // 10
    for i in range(tens + 1):
        media = []
        if (i + 1) * 10 < num_of_stories:
            for j in range(i * 10, (i + 1) * 10):
                story = order[str(j)]
                if story.type == 'pic':
                    media.append(InputMediaPhoto(open(f'{img_folder}/{story.file_name}', "rb")))
                elif story.type == 'video':
                    media.append(InputMediaVideo(open(f'{img_folder}/{story.file_name}', "rb")))

        else:
            for j in range(i * 10, num_of_stories):
                story = order[str(j)]
                if story.type == 'pic':
                    media.append(InputMediaPhoto(open(f'{img_folder}/{story.file_name}', "rb")))
                elif story.type == 'video':
                    media.append(InputMediaVideo(open(f'{img_folder}/{story.file_name}', "rb")))
        if media:
            try:
                bot.send_media_group(client_id, media, timeout=30)
            except Exception as ex1:
                console(ex1)
                console('[Upload to Telegram] Error1: files were not uploaded', level='error')
                console('                     client_id: {}, target: {}'.format(client_id, user), level='error')
                try:
                    bot.send_media_group(client_id, media, timeout=60)
                except Exception as ex2:
                    console(ex2)
                    console('[Upload to Telegram] Error2: files were not uploaded', level='error')
                    console('                     client_id: {}, target: {}'.format(client_id, user), level='error')

