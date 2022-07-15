from bs4 import BeautifulSoup
from myfunc_html_response_codes import response_code_meaning
import requests


def printout_primary_parse_result(search_string):     # this is to be shown in telegram

    primary_parse_result_as_textblock = "<meta charset=utf-8>"

    test_mode = "off"  # "on" (service messages will be displayed) OR "off" (service messages will not be displayed)
    if (test_mode != "on"): test_mode = "off"  # for sure

    goal_URI = 'https://wooordhunt.ru/word/' + search_string

    response = requests.get(goal_URI)
    response_code = response.status_code
    response_encoding = response.encoding
    response_text = response.text

    if (test_mode == "on"):
        print(f"test mode {test_mode}")
        print()
        print(f"Goal URI is {goal_URI}")
        print()
        print(f"Html response (status) code is {response_code}")
        print(response_code_meaning(response_code))
        print()
        print(f"Html page charset is {response_encoding}")    # by the way
    #====================

    the_whole_page = BeautifulSoup(response_text, 'html.parser')


    # 0) we don't need any hrefs or images in Telegram version:
    for i in the_whole_page.find_all(href=True):
        del i['href']

    for tag in the_whole_page("img"):
        tag.decompose()

    # 1) from  <div id="wd_title"> we will  take the word itself and its pronunciation
    block_wd_title = the_whole_page.find(id='wd_title')

    unwanted_id_list_in_wd_title = ['ppt', 'word_rank_box', 'block_action_icons', 'audio_us', 'audio_uk']  # we will dismiss these
    unwanted_class_list_in_wd_title = ['sound_pic']

    for i in unwanted_id_list_in_wd_title:
        for k in block_wd_title.find_all(id=i):
            result_found = block_wd_title.find(id=i)
            if str(result_found) != "None":
                block_wd_title.find(id=i).decompose()

    for i in unwanted_class_list_in_wd_title:
        for k in block_wd_title.find_all(class_=i):
            result_found = block_wd_title.find(class_=i)
            if str(result_found) != "None":
                block_wd_title.find(class_=i).decompose()

    pretty_block_wd_title = block_wd_title.prettify()   # _prettify_ should come last!
    primary_parse_result_as_textblock += pretty_block_wd_title
    # print(pretty_block_wd_title)
    #==========================================================

    # 2) from  <div id="wd_content"> we will  take the word meanings
    block_wd_content = the_whole_page.find(id='wd_content')

    unwanted_id_list_in_wd_content = ['personal_ex_block']  # we will dismiss these
    unwanted_class_list_in_wd_content = ['more_up', 'more_down', 'snoska no_mobile', 'snoska']

    for i in unwanted_id_list_in_wd_content:
        for k in block_wd_content.find_all(id=i):
            result_found = block_wd_content.find(id=i)
            if str(result_found) != "None":
                block_wd_content.find(id=i).decompose()

    for i in unwanted_class_list_in_wd_content:
        for k in block_wd_content.find_all(class_=i):
            result_found = block_wd_content.find(class_=i)
            if str(result_found) != "None":
                block_wd_content.find(class_=i).decompose()

    pretty_block_wd_content = block_wd_content.prettify()
    primary_parse_result_as_textblock += pretty_block_wd_content

    # print(pretty_block_wd_content)

    # print(primary_parse_result_as_textblock)

    return primary_parse_result_as_textblock


#==========================================================

# print(printout_primary_parse_result("weather"))

