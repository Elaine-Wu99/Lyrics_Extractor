import requests
from bs4 import BeautifulSoup
import json
import re
import xlrd
from lxml import etree
from functools import reduce
ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
headers = {
    'User-agent': ua
}


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


def get_url_html(url):
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        text = response.text
        html = etree.HTML(text)
    return html


def get_all_info(singer_id):
    # get all album ids
    # html = "https://music.163.com/artist/album?id=" + \
    #    str(singer_id)+"&limit=150&offset=0"
    html = "https://music.163.com/artist/album?id=" + \
        str(singer_id)+"&limit=150&offset=0"
    html = get_html(html)
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all('a', class_='tit s-fc0')
    album_ids = []
    for link in links:
        album_id = link.get('href').split('=')[-1]
        album_ids.append(album_id)
    all_song_ids, all_song_names = [], []
    for album_id in album_ids:
        one_album_url = "https://music.163.com/album?id="+str(album_id)
        html = get_html(one_album_url)
        soup2 = BeautifulSoup(html, 'lxml')
        links2 = soup2.find('ul', class_='f-hide').find_all('a')
        for link in links2:
            song_ID = link.get('href').split('=')[-1]
            song_name = link.get_text()
            all_song_ids.append(song_ID)
            all_song_names.append(song_name)
    return zip(all_song_names, all_song_ids)


def get_singer_info(html, song_numbers):
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('ul', class_='f-hide').find_all('a')
    song_IDs = []
    song_names = []
    cnt = 0
    for link in links:
        song_ID = link.get('href').split('=')[-1]
        song_name = link.get_text()
        song_IDs.append(song_ID)
        song_names.append(song_name)
        cnt += 1
        if(cnt == song_numbers):
            break

    return zip(song_names, song_IDs)


def get_lyric(song_id):
    url = 'http://music.163.com/api/song/lyric?id=' + \
        str(song_id) + '&lv=1&kv=1&tv=-1'
    html = get_html(url)
    json_obj = json.loads(html)
    # print(contains_lyric(song_id))
    initial_lyric = json_obj['lrc']['lyric']
    regex = re.compile(r'\[.*\]')
    final_lyric = re.sub(regex, '', initial_lyric).strip()
    return final_lyric


def contains_lyric(song_id):
    url = 'http://music.163.com/api/song/lyric?id=' + \
        str(song_id) + '&lv=1&kv=1&tv=-1'
    html = get_html(url)
    json_obj = json.loads(html)
    if 'lrc' in json_obj.keys():
        return True
    return False


def write_text(singer, song_name, lyric):
    print("writing now: {}".format(song_name)+"singer: {}".format(singer))
    with open('{}.docx'.format(singer), 'a', encoding='utf-8') as fp:
        fp.write(song_name+'\n')
        fp.write(lyric)
        fp.write('\n\n\n')


def read_xlsx_file(filename):
    f = xlrd.open_workbook(filename)
    sh = f.sheet_by_name("Sheet1")
    singer_names = sh.col_values(0)[1:]
    singer_ids = sh.col_values(1)[1:]
    songs_numbers = sh.col_values(3)[1:]
    return zip(singer_names, singer_ids, songs_numbers)


# excel address in your computer
infos = read_xlsx_file(
    "/Users/wuqiaowen/Desktop/网易云lyrics/project/artist list.xlsx")
for inf in infos:
    if type(inf[1]) != float or type(inf[2]) != float:
        continue
    singer_name = (str)(inf[0])
    with open('{}.docx'.format(singer_name), 'a', encoding='utf-8') as fp:
        fp.write("歌手姓名：" + singer_name + '\n\n\n')
        fp.close()
    singer_id = round(inf[1])
    song_numbers = round(inf[2])
    start_url = 'http://music.163.com/artist?id={}'.format(singer_id)
    html = get_html(start_url)
    singer_infos = []
    if song_numbers == 50:
        album_url = "https://music.163.com/artist/album?id=" + \
            str(singer_id)+"&limit=150&offset=0"
        html_album = get_url_html(album_url)
        singer_infos = get_all_info(singer_id)
    else:
        singer_infos = get_singer_info(html, song_numbers)

    for singer_info in singer_infos:
        print(singer_info[0])
        print(singer_info[1])
        if contains_lyric(singer_info[1]) == False:
            print("invalid" + (str)(singer_info[0]))
            continue
        lyric = get_lyric(singer_info[1])
        write_text(singer_name, singer_info[0], lyric)
        fp.close()
