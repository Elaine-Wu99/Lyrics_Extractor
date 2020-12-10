import requests
from bs4 import BeautifulSoup
import json
import re
import xlrd


def get_html(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us",
        "Connection": "keep-alive",
        "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
    }
    try:
        response = requests.get(url, headers=header)
        html = response.text
        return html
    except:
        print("Request error")
        pass


def get_singer_info(html):
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('ul', class_='f-hide').find_all('a')
    song_IDs = []
    song_names = []
    for link in links:
        song_ID = link.get('href').split('=')[-1]
        song_name = link.get_text()
        song_IDs.append(song_ID)
        song_names.append(song_name)
    return zip(song_names, song_IDs)


def get_lyric(song_id):
    url = 'http://music.163.com/api/song/lyric?id=' + \
        str(song_id) + '&lv=1&kv=1&tv=-1'
    html = get_html(url)
    json_obj = json.loads(html)
    initial_lyric = json_obj['lrc']['lyric']
    regex = re.compile(r'\[.*\]')
    final_lyric = re.sub(regex, '', initial_lyric).strip()
    return final_lyric


def write_text(song_name, lyric):
    print("writing now: {}".format("歌词"))
    with open('{}.txt'.format("歌词"), 'a', encoding='utf-8') as fp:
        fp.write(song_name+'\n')
        fp.write(lyric)
        fp.write('\n\n\n')


def read_xlsx_file(filename):
    f = xlrd.open_workbook(filename)
    sh = f.sheet_by_name("Sheet1")
    singer_names = sh.col_values(0)[1:]
    singer_ids = sh.col_values(1)[1:]
    songs_number = sh.col_values(3)[1:]
    return zip(singer_names, singer_ids, songs_number)


# if __name__ == '__main__':
 #   singer_id = input("请输入歌手ID：")
 #   start_url = 'http://music.163.com/artist?id={}'.format(singer_id)
 #   html = get_html(start_url)
 #   singer_infos = get_singer_info(html)
 #   for singer_info in singer_infos:
 #       lyric = get_lyric(singer_info[1])
 #       write_text(singer_info[0], lyric)


infos = read_xlsx_file("/Users/wuqiaowen/Desktop/网易云lyrics/Book1.xlsx")
# print(type(infos))
for inf in infos:
    # print(round(inf[1]))
    singer_name = inf[0]
    with open('{}.txt'.format("歌词"), 'a', encoding='utf-8') as fp:
        fp.write("歌手姓名：" + singer_name + '\n\n\n')
        fp.close()
    singer_id = round(inf[1])
    start_url = 'http://music.163.com/artist?id={}'.format(singer_id)
    html = get_html(start_url)
    singer_infos = get_singer_info(html)
    for singer_info in singer_infos:
        lyric = get_lyric(singer_info[1])
        write_text(singer_info[0], lyric)
        fp.close()
