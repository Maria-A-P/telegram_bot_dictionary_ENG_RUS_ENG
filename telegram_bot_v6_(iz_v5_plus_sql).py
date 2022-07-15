# based on https://www.codementor.io/@garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay


TOKEN = ""
full_filename_of_an_aux_html_file = r''
mssql_driver_name = r''
mssql_server_name = r''
mssql_database_name = r''
mssql_user = r''
mssql_pwd = r''


dir_path = r''
filename_of_an_aux_png_file_itself = 'response.png'
full_filename_of_an_aux_png_file = dir_path + "\\" + filename_of_an_aux_png_file_itself

write_to_database_flag = "on"  # "on" (save requests history to database) OR "off" (do not)
if (write_to_database_flag != "off"): write_to_database_flag = "on"  # on is preferred

from primary_parsing_of_vocab_site import printout_primary_parse_result

import json             # (to parse the JSON responses from Telegram into Python dictionaries so that we can extract the pieces of data that we need)
import requests
import time
import urllib.parse
from html2image import Html2Image
import pyodbc



URL_beginning = "https://api.telegram.org/bot{}/".format(TOKEN)        #  basic URL

def get_content_of_user_message(url):
    response = requests.get(url)
    user_mes_content = response.content.decode("utf8")      # for extra compatibility
    return user_mes_content

def transform_json_to_py_dict(url):
    content = get_content_of_user_message(url)        # in Telegram this is always in JSON
    user_mes_content_as_py_dict = json.loads(content)    # transform a JSON string to a python dictionary
    return user_mes_content_as_py_dict

def get_updates(offset=None):
    url = URL_beginning + "getUpdates?timeout=10"
    if offset:
        url += "&offset={}".format(offset)
    user_mes_content_as_py_dict = transform_json_to_py_dict(url)
    return user_mes_content_as_py_dict

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

# if there was a connectivity issue and a user managed to send many messages - we will reply to each
def respond_to_all_new_user_messages(all_updates, request_term_column_allowed_size):
    for each_update in all_updates["result"]:    # все равно обрабатывает по одному, но пока оставлю так
        try:
            input_text = each_update["message"]["text"]
            chat = each_update["message"]["chat"]["id"]
            telegram_user_id_value = each_update["message"]["from"]["id"]   # telegram_user_id_value is to be written to database
            request_term_value = input_text                       # request_term_value is to be written to database
            respond_to_one_user_message(input_text, chat)
            if write_to_database_flag == 'on':
                my_connection = pyodbc.connect('DRIVER='+mssql_driver_name+';SERVER='+mssql_server_name+';DATABASE='+mssql_database_name+';UID='+mssql_user+';PWD='+mssql_pwd+'')
                my_cursor = my_connection.cursor()
                length_of_request_term = len(request_term_value)
                if length_of_request_term > int(request_term_column_allowed_size):
                    error_message_for_request_term_value = 'only first {} symbols of request term were saved'.format(
                        request_term_column_allowed_size)
                    request_term_value = request_term_value[:request_term_column_allowed_size]
                else:
                    error_message_for_request_term_value = ''
                unix_time_sec_of_request_value = int(time.time())   # seconds  For Unix, the epoch is January 1, 1970, 00:00:00 (UTC)
                my_cursor.execute(
                    "INSERT INTO Table_Journal(request_term, telegram_user_id, unix_time_sec_of_request, error_message_for_request_term) VALUES (?, ?, ?, ?)",
                    request_term_value, telegram_user_id_value, unix_time_sec_of_request_value,
                    error_message_for_request_term_value)
                    # при этом в столбец request_id ничего не пишу, у него автозаполнение
                my_connection.commit()
                my_cursor.close()
                my_connection.close()
        except Exception as e:
            print(e)

def respond_to_one_user_message(input_text, chat_id):
    nice_input_text = urllib.parse.quote(input_text)      # что лучше - .quote или .quote_plus ? вообще это чтобы любые знаки ок были
    search_string = nice_input_text
    output_text = printout_primary_parse_result(search_string)
    with open(full_filename_of_an_aux_html_file, "w", encoding="utf-8") as file:
        file.write(output_text)
    # nice_output_text = urllib.parse.quote_plus(output_text)

    time.sleep(0.05)   # на всякий случай - чтобы точно не захватить более ранний файл
    hti = Html2Image(output_path=dir_path)           # тут путь к директории, куда сохраняем скриншот
    hti.screenshot(
        html_file=full_filename_of_an_aux_html_file,
        save_as=filename_of_an_aux_png_file_itself,      # а это имя файла со скриншотом без пути
        size=(500, 1000))                     # нет смысла делать высоту больше 1000 (Телеграм сожмет)

    # url = URL_beginning + "sendMessage?text={}&chat_id={}".format(output_text, chat_id)

    url_sendphoto = URL_beginning + "sendPhoto?caption={}".format("Предпросмотр начала статьи. Статья полностью - в html файле ниже")
    with open(full_filename_of_an_aux_png_file, 'rb') as file:
        post_data = {'chat_id': chat_id}
        post_file = {'photo': file}
        requests.post(url_sendphoto, data=post_data, files=post_file)

    url_senddoc = URL_beginning + "sendDocument"
    with open(full_filename_of_an_aux_html_file, 'r', encoding="utf-8") as file:
        post_data = {'chat_id': chat_id}
        post_file = {'document': file}
        requests.post(url_senddoc, data=post_data, files=post_file)


# infinite cycle: get updates, find the last update id
def main():
    last_update_id = None
    if write_to_database_flag == 'on':
        my_connection_0 = pyodbc.connect('DRIVER='+mssql_driver_name+';SERVER='+mssql_server_name+';DATABASE='+mssql_database_name+';UID='+mssql_user+';PWD='+mssql_pwd+'')
        my_cursor_0 = my_connection_0.cursor()
        for rr in my_cursor_0.columns(table='Table_Journal', column='request_term'):  # просто rr = не работает
            request_term_column_allowed_size = rr.column_size
        my_cursor_0.close()
        my_connection_0.close()
    while True:
        all_updates = get_updates(last_update_id)    # all updates since last_update_id
        number_of_new_msgs = len(all_updates["result"])
        if number_of_new_msgs > 0:           # if there WERE updates
            respond_to_all_new_user_messages(all_updates, request_term_column_allowed_size)
            last_update_id = get_last_update_id(all_updates) + 1    # for future waiting
                              # если вместо 1 написать number_of_new_msgs, то не на все отвечает
                              # видимо, тут хитрое согласование между временем отсылки запроса и временем ожидания
                              # но тогда нет смысла писать цикл в respond_to_all_new_user_messages,
                              # достаточно по одному. Но пока оставлю.
        time.sleep(0.5)


if __name__ == '__main__':
    main()




