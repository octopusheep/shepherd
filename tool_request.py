import requests
import time
import os
import json
from bs4 import BeautifulSoup

# requests config
requests.adapters.DEFAULT_RETRIES = 5
time_out=3
time_sleep=0
max_count=600

# basic information
reference = {
    "剧情": "58",
    "喜剧": "66",
    "动作": "67",
    "惊悚": "69",
    "爱情": "60",
    "犯罪": "74",
    "冒险": "68",
    "恐怖": "76",
    "科幻": "59",
    "动画": "71",
    "奇幻": "77",
    "家庭": "72",
    "悬疑": "99",
    "战争": "83",
    "纪录片": "88",
    "传记": "102",
    "历史": "113",
    "神秘": "62",
    "音乐": "94",
    "幻想": "81",
    "古装": "175",
    "情色": "1401",
    "R级": "1583",
    "运动": "82",
    "歌舞": "170",
    "同性": "1271",
    "武侠": "174",
    "西部": "93",
    "儿童": "397",
    "灾难": "70",
}
categoty_list = ["剧情", "喜剧", "动作", "惊悚", "爱情", "犯罪", "冒险", "恐怖", "科幻", "动画", "奇幻", "家庭", "悬疑", "战争", "纪录片", "传记", "历史",
                 "神秘", "音乐", "幻想", "古装", "情色", "R级", "运动", "歌舞", "同性", "武侠", "西部", "儿童", "灾难"]


function = [
    '同步电影资源(爬取过程可能耗时20min,请耐心等候吼)',
    '搜索电影分类',
    '搜索电影名称',
    '退出',
]


# model
class Video(object):

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def information(self):
        SPLIT_LINE = '----------------------------------'
        print('%s\nvideo title: %s\nvideo link: %s\n%s'
              % (SPLIT_LINE, self.title, self.link, SPLIT_LINE))


# IO
def read_json(dir, filename):
    with open('./data/' + dir + '/category/' + filename + '.txt', 'r') as f:
        for line in f.readlines():
            print(line.strip())


def read(url):
    with open(url, 'r') as f:
        for line in f.readlines():
            print(line.strip())


def write_demo_video():
    with open('./demo/demo.json', 'a') as f:
        for dict in get_list_demo_video():
            f.write(json.dumps(dict, default=video2dict) + '\n')
    read_json()


def print_movie_list_local():
    for movie in get_list_movie_list_local_without_advertise():
        print(movie)


def print_demo_video_information():
    for video in get_list_demo_video():
        video.information()


def print_information_local(dir, filename):
    for video in get_list_from_json(dir, filename):
        video.information()


def get_list_movie_list_local():
    return [os.path.splitext(movie)[0] for movie in os.listdir('/Users/zhangyuyang/Movies') if
            os.path.splitext(movie)[1] == '.mp4' or os.path.splitext(movie)[1] == '.mkv']


def get_list_movie_list_local_without_advertise():
    return list(map(filter_advertise, get_list_movie_list_local()))


def get_list_demo_video():
    return list(map(str2video, get_list_movie_list_local_without_advertise()))


def get_list_from_json(dir, filename):
    with open('./data/' + dir + '/' + filename + '.txt', 'r') as f:
        return list(map(json2dict, f.readlines()))


def get_list(url):
    try:
        with open(url, 'r') as f:
            return list(map(json2dict, f.readlines()))
    except FileNotFoundError:
        print('妹有找到文件吼!')


def str2video(text):
    return Video(text, 'http://google.com')


def video2dict(video):
    return {'title': video.title, 'link': video.link}


def dict2video(dict):
    return Video(dict['title'], dict['link'])


def json2dict(text):
    return json.loads(text.strip(), object_hook=dict2video)


def filter_advertise(text):
    advertise = '[BD影视分享bd-film.cc]'
    if text[:len(advertise)] == advertise:
        return text[len(advertise):]
    return text


# get function
def get_request_by_category(category, page):
    code = reference[category]
    url = 'https://www.bd-film.cc/tag/' + code + '_' + str(page) + '.jspx'
    try:
        request_category = requests.get(url, timeout=time_out)
        text = request_category.text
    except requests.exceptions.ConnectionError:
        print('ConnectionError -- please wait 3 seconds')
        text = ''
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError -- please wait 3 seconds')
        text = ''
    except:
        print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        text = ''
    print(
        'category: ' + category + '\ncatecode: ' + code + '\nurl_link: ' + url + '\n-----------------------------------------------')
    return text


def get_soup_by_category(category, page):
    return BeautifulSoup(get_request_by_category(category, page), 'lxml')


def get_list_selected_by_category(category, page, selector):
    return get_soup_by_category(category, page).select(selector)


def get_list_dict_by_category(category, page, selector):
    return list(map(soup2dict, get_list_selected_by_category(category, page, selector)))


def get_all_list_dict_by_category(category):
    list = []
    selector = '#content_list > li > div > a'
    last_page_list = []
    index = 0
    while index < max_count:

        index += 1
        current_page_list = get_list_dict_by_category(category, index, selector)
        print('index:', index, '\ncurrent_page_list:', current_page_list, '\nlast_page_list:', last_page_list,
              '\n-----------------------------------------------')
        if current_page_list == last_page_list and not current_page_list == []:
            break
        last_page_list = current_page_list
        list += current_page_list
        time.sleep(time_sleep)

    return list


def get_all_list_video_by_category(category):
    return list(map(dict2video, get_all_list_dict_by_category(category)))

def get_list_video(url):
    return list(map(dict2video, get_list(url)))

def get_list_all_category(url_2, url_1='data', url_3='category'):
    list = []
    for file in os.listdir('./' + url_1 + '/' + url_2 + '/' + url_3):
        for video in get_list('./' + url_1 + '/' + url_2 + '/' + url_3 + '/' + file):
            count = 0
            for index in list:
                if video.title == index.title:
                    count += 1
            if count == 0:
                list.append(video)
    return list


# write function


def save_by_category(dir, category):
    with open('./data/' + dir + '/category/' + category + '.txt', 'a') as f:
        for dict in get_all_list_video_by_category(category):
            f.write(json.dumps(dict, default=video2dict, ensure_ascii=False) + '\n')
    read_json(dir, category)


def save_as_category(website='bd-film.cc'):
    delete_all_file_from_category(website)
    for category in reference:
        save_by_category(website, category)
    save_as_unit()
    print('同步完成，各位爸爸久等辣!')
    entrance()


def save_as_unit(url_2='bd-film.cc', url_1='data'):
    with open('./' + url_1 + '/' + url_2 + '/index_by_all_category.txt', 'a') as f:
        for dict in get_list_all_category(url_2):
            f.write(json.dumps(dict, default=video2dict, ensure_ascii=False) + '\n')
    read('./' + url_1 + '/' + url_2 + '/index_by_all_category.txt')


# print function


def print_list(list):
    for dict in list:
        print(dict)


# command line
def entrance():
    print(
        split + '\nFilm Search Tools 电影搜索神器\n' + split + '\nAuthor : Octopusheep\nWebsite: Octopusheep.com\nGithub : https://github.com/octopusheep\n' + split)
    index = 1
    for func in function:
        print(str(index) + '. ' + func)
        index += 1
    print(split)
    text = input('请输入操作编号(1-' + str(len(function)) + '):\n')

    if text == '1':
        save_as_category()
    elif text == '2':
        category()
    elif text == '3':
        search()
    elif text == '4':
        pass
    else:
        print('请输入正确的操作编号哦～')
        entrance()


# search function
def search(website='bd-film.cc'):
    text = input(split + '\n请输入关键字:\n')
    list = get_list('./data/' + website + '/index_by_all_category.txt')
    try:
        for video in list:
            if not video.title.find(text) == -1:
                video.information()
    except TypeError:
        print('请先同步电影资源，同步完成后方可进行搜索吼!')

    text = input(split + '\n是否继续按关键字查询电影(y/n):\n')
    if text == 'y' or text == 'Y':
        search()
    elif text == 'n' or text == 'N':
        entrance()
    else:
        print('您的操作有误，请输入正确的操作编号哦～')
        entrance()

def category():
    try:
        print(split)
        count = 1
        for index in reference:
            print(str(count) + '. ' + index)
            count += 1
        print(split)
        text = input('请输入电影分类编号:\n')
        index=int(text)-1
        if index > len(categoty_list)-1 :
            print('您的操作有误，请输入正确的操作编号哦～')
            category()
        param=categoty_list[index]
        url='./data/bd-film.cc/category/' +param+'.txt'
        try:
            list = get_list(url)
            for video in list:
                video.information()
        except TypeError:
            print('请先同步电影资源，同步完成后方可进行搜索吼!\n'+split)
        text=input('是否继续按分类查询电影(y/n)：\n')

        if  text=='y' or text=='Y':
            category()
        elif text=='n' or text=='N':
            entrance()
        else:
            print('您的操作有误，请输入正确的操作编号哦～')
    except ValueError:
        print('您的操作有误，请输入正确的操作编号哦～')
        category()


# essential function
split = '---------------------------------------------'


def dict2video(dict):
    video = Video(dict['title'], dict['link'])
    return video


def soup2dict(element):
    element_soup = BeautifulSoup(str(element), 'lxml')
    tag = element_soup.a
    dict = {'title': tag['title'], 'link': tag['href'], 'href': tag['href']}
    return dict


def delete_all_file_from_category(url_2, url_1='data', url_3='category'):
    if os.path.exists('./' + url_1 + '/' + url_2 + '/' + url_3):
        for file in os.listdir('./' + url_1 + '/' + url_2 + '/' + url_3):
            os.remove('./' + url_1 + '/' + url_2 + '/' + url_3 + '/' + file)
    else:
        os.mkdir('./' + url_1 + '/' + url_2 + '/' + url_3)

    if os.path.exists('./' + url_1 + '/' + url_2 + '/index_by_all_category.txt'):
        os.remove('./' + url_1 + '/' + url_2 + '/index_by_all_category.txt')


# write_vedio_to_local('bd-film.cc','top-100')
# print_information_local('bd-film.cc','top-100')
# print_list(get_all_list_dict_by_category('love'))
# save_as_unit()

entrance()
