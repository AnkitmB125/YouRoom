import requests
from urllib.parse import urlparse, parse_qs
from xml.etree import ElementTree
from requests.auth import HTTPProxyAuth
import re
import json
import sys

proxies = {"http":"172.31.100.29:3128"}
auth = HTTPProxyAuth("edcguest", "edcguest")
OK = 200

def get_video_id(url):

    if not url:
        return ""

    if "embed" in url:
        return url.split("/")[-1]

    parse_result = urlparse(url)
    query = parse_qs(parse_result.query)
    return query["v"][0]


def transcribe_video(youtube_url, ghost=True):
    id = get_video_id(youtube_url)
    url = "http://video.google.com/timedtext?lang=en&v={}".format(id)
    print(url)
    response = requests.get(url, proxies=proxies, auth=auth)
    return response.status_code, response.content

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return round(int(h) * 3600 + int(m) * 60 + float(s),3)

def search_keywords(youtube_url, keyword, srt):
    timestamps = list()
    if not keyword or not youtube_url:
        return timestamps
    # status_code, content = transcribe_video(youtube_url)
    with open(srt, 'r') as myfile:
        content = myfile.read()
    status_code = 200
    # print(content)
    if not content:
        print("NO CONTENT")
        return timestamps

    if status_code == OK:
        content = str(content);
        a=[];
        x = [m.start() for m in re.finditer(keyword,content)];
        extracted_date = "[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]"
        for iterator in x:
            y = [(m.start(0), m.end(0)) for m in re.finditer(extracted_date,content[0:iterator])];
            timestamps.append(get_sec(content[y[len(y)-1][0]:y[len(y)-1][0]+12].replace(',', '.')));

    # if status_code == OK:
    #     tree = ElementTree.fromstring(content)
    #     # print(keyword)
    #     for node in tree:
    #         # print(node.text)
    #         if keyword in node.text:
    #             # print(node.text)
    #             # print(node.attrib)
    #             timestamps.append(float(node.attrib["start"]))

    return timestamps


if __name__ == '__main__':
    # url = "https://www.youtube.com/watch?v=-6OFqkemd4c"
    url = sys.argv[1]
    srt = sys.argv[2]
    keyword = sys.argv[3]
    # url = "/home/ankitb/Downloads/stranger_things.mp4";
    # xml = '/home/ankitb/Downloads/stranger_things_sub.xml';
    # srt = '/home/ankitb/Downloads/stranger_things_sub.srt';
    # keyword = "grandma"
    timestamps = search_keywords(url, keyword, srt)
    print((timestamps), end='')
