import requests
import json
import queue
import threading
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import tqdm
header={
    "user-agent":"okhttp/3.12.0"
}

def get_id(url):
    id_list = []
    data = requests.get(url=url,headers=header)
    for i in json.loads(data.text)['rescont']['data']:
        id_list.append(i['id'])
    return id_list

def get_m3u8(id):
    url = "http://sg01.sg01.sg01.xyz/api/videoplay/{0}?uuid=3afe85b54b641683&device=0".format(id)
    data = json.loads(requests.get(url,headers=header).text)
    return data['rescont']

def make_url(url_list = [],ch=0):
    """
    1:new
    2:hot
    3:like
    """
    if(ch==1):
        url = "http://sg01.sg01.sg01.xyz/api/videosort/0?orderby={0}&uuid=3afe85b54b641683&device=0&page=".format("new")
    if ch==2:
        url = "http://sg01.sg01.sg01.xyz/api/videosort/0?orderby={0}&uuid=3afe85b54b641683&device=0&page=".format("hot")
    if ch==3:
        url = "http://sg01.sg01.sg01.xyz/api/videosort/0?orderby={0}&uuid=3afe85b54b641683&device=0&page=".format("like")
    num = json.loads(requests.get(url,headers = header).text)['rescont']['last_page']
    for i in range(1,num+1):
        url_list.append(url+str(i))
def save_data(data):
    with open("data.json",'w') as f:
        f.write(json.dumps(data))
def loads_data():
    data = []
    with open("data.json",'r') as f:
        data = json.loads(f.read())
    for i in data:
        print(i)
def Main():
    threadPool = ThreadPoolExecutor(max_workers = 20)
    url_list = []
    make_url(url_list,1)
    tasks = [threadPool.submit(get_id,(url)) for url in url_list]
    id_list = []
    print("正在获取id")
    for i in tqdm.tqdm(tasks):
        id_list+=i.result()
    print("正在获取m3u8")
    threadPool = ThreadPoolExecutor(max_workers = 20)
    tasks = [threadPool.submit(get_m3u8,(id)) for id in id_list]
    data = []
    for i in tqdm.tqdm(tasks):
        data.append(i.result())
    print("正在转储数据")
    save_data(data)
    print("OK")
Main()

