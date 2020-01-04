import xlsxwriter
import json
from tqdm import tqdm
from PIL import Image
import queue
import threading
from io import BytesIO
import requests
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import re
import os
header={
    "user-agent":"okhttp/3.12.0"
}
def get_id(url):
    id_list = []
    data = None;
    status_code=404;
    time = 0;
    while status_code!=200:
        try:
            data = requests.get(url=url,headers=header,timeout=1)
            status_code = data.status_code
        except:
            time+=1
            # print("id获取地址:"+url+"\n失败:{0}次".format(time))
            continue
    for i in json.loads(data.text)['rescont']['data']:
        id_list.append(i['id'])
    return id_list

def get_m3u8(id):
    url = "http://sg01.sg01.sg01.xyz/api/videoplay/{0}?uuid=3afe85b54b641683&device=0".format(id)
    data = None
    status_code=404;
    time = 0;
    while status_code!=200:
        try:
            data = requests.get(url=url,headers=header,timeout=1)
            status_code = data.status_code
        except:
            time+=1
            # print("m3u8获取地址:"+url+"\n失败:{0}次".format(time))
            continue
    data = json.loads(data.text)
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
def Data(max_workers = 20):
    threadPool = ThreadPoolExecutor(max_workers = max_workers)
    url_list = []
    make_url(url_list,1)
    tasks = [threadPool.submit(get_id,(url)) for url in url_list]
    id_list = []
    print("正在获取id")
    for i in tqdm(tasks):
        id_list+=i.result()
    print("正在获取m3u8")
    threadPool = ThreadPoolExecutor(max_workers = max_workers)
    tasks = [threadPool.submit(get_m3u8,(id)) for id in id_list]
    data = []
    for i in tqdm(tasks):
        data.append(i.result())
    print("正在转储数据")
    save_data(data)
    print("OK")

def clear():
    if(os.name=='nt'):
        os.system('cls')
    else:
        os.system('clear')
"""进度显示（给定任务队列，根据队列剩余长度显示进度）（阻塞态）"""
def Show_tqdm(Q):
    num1 = Q.qsize()
    with tqdm(total=num1) as T:
        size = Q.qsize()
        while Q.empty()==False:
            q = Q.qsize()
            if(size!=q):
                T.update(-q+size)
                size = q
        T.update(size)
"""多线程下载图片(返回队列，包含以url为key的字)"""
def Get_Image(url_queue,imgdirct,threade_count,max_fail,timeout=(2, 2),error=False):
    clear()
    print("\033[1;36m开始缓存图片数据！\033[0m")
    threading_list = []
    image_queue = queue.Queue()
    for i in range(threade_count):
        t = threading.Thread(target=GI,args=(url_queue,image_queue,max_fail,error,timeout))
        t.start()
        threading_list.append(t)
    Show_tqdm(url_queue)
    for i in threading_list:
        i.join()
    while image_queue.empty()==False:
        data = image_queue.get()
        for i in data.keys():
            imgdirct[i] = data[i]
    print("\033[1;36m图片数据缓存完成！\033[0m")
def GI(url_queue,image_queue,max_fail,error, timeout):
    while url_queue.empty() == False:
        image_url = url_queue.get()
        URL = image_url
        data = None
        fail_count = 0
        isGif = False
        changeName = re.compile(r'\.gif')
        while True:
            try:
                if (isGif==False and len(changeName.findall(image_url)) > 0):
                    #print('\033[1;31m{0}\n发现不受支持的图片！\033[0m'.format(image_url))
                    isGif=True
                else:
                    respones = requests.get(image_url, headers=header, timeout=timeout)
                    if (respones.status_code == 200):
                        data = respones.content
                        break
                    else:
                        fail_count += 1
            except Exception as e:
                fail_count += 1
                if(error):
                    print(e)
            if (fail_count > max_fail):
                image_url='http://5b0988e595225.cdn.sohucs.com/images/20180914/8641e9dec4a945b9855fac1615b5ff38.jpeg'
        image_data = {}
        BIO = BytesIO(data)
        if(isGif):
            file_name = re.findall(r"/(\w+\.\w+)",URL)[0]
            file_name = changeName.sub('png',file_name)
            im = Image.open(BIO)
            im = im.copy()
            im.save(file_name)
            with open(file_name,'rb') as f:
                BIO = BytesIO(f.read())
            os.remove(file_name)
        image_data[URL]=BIO
        image_queue.put(image_data)
#将gif图片转成PNG图片
def gif_to_png(im):
    for i, frame in enumerate(iter_frames(im)):
        frame.save('image.png',**frame.info)
def iter_frames(im):
    try:
        i= 0
        while 1:
            im.seek(i)
            imframe = im.copy()
            if i == 0:
                palette = imframe.getpalette()
            else:
                imframe.putpalette(palette)
            yield imframe
            i += 1
    except EOFError:
        pass

def saveToXlsx():
    path = 'm3u8.xlsx'
    workbook = xlsxwriter.Workbook(path)
    sheet = workbook.add_worksheet()
    row = 0;
    bold = workbook.add_format({'bold':True})
    info = ['coverpath','id','title','authername','created_at','updated_at','pageviews','introduction','sort_id','videopath'];
    fy =   ['图片','ID','标题','演员','创建时间','更新时间','浏览量','介绍','sort id','视频地址']
    for i in range(len(info)):
        sheet.write(row,i,info[i],bold)
    data = None;
    with open('data.json','r') as f:
        data = json.loads(f.read())
    url_queue = queue.Queue()
    for i in range(len(data)):
        url_queue.put(data[i][info[0]])
    image_data = {}
    Get_Image(url_queue,image_data,20,30)
    image_width=22
    image_higth=75
    sheet.set_column('A:A', 30)
    sheet.set_column('C:C', 70)
    sheet.set_column('D:D', 20)
    sheet.set_column('E:E', 20)
    sheet.set_column('F:F', 20)
    sheet.set_column('H:H', 60)
    sheet.set_column('J:J', 60)
    clear()
    print("\033[1;36m开始写入表格！\033[0m")
    for I in tqdm(range(len(data))):
        for i in range(len(info)):
            if(i==0):
                sheet.set_row(I+1, image_higth)
                im = None
                image_url = data[I][info[i]]
                try:
                   im = Image.open(image_data[image_url])
                except:
                   im = Image.open(BytesIO(requests.get('http://5b0988e595225.cdn.sohucs.com/images/20180914/8641e9dec4a945b9855fac1615b5ff38.jpeg').content))
                """图像尺寸"""
                x_size = im.size[0]
                y_size = im.size[1]
                """获取缩放"""
                if( x_size<=314 and y_size<=196):
                    pass
                else:
                    try:
                       im = im.resize((314, 196), Image.ANTIALIAS)
                       file_name = '1.jpg'
                       try:
                           im.save(file_name)
                       except:
                           file_name='1.png'
                           im.save(file_name)
                       f = open(file_name, 'rb')
                       image_data[image_url] = BytesIO(f.read())
                       f.close()
                       x_size = im.size[0]
                       y_size = im.size[1]
                    except:pass
                x = (image_width * 9 + 7) / x_size
                y = image_higth / 3 * 5 / y_size
                sheet.set_row(I+1, image_higth + 18)
                sheet.insert_image(I+1, i, image_url, {'url':data[I][info[9]],'image_data': image_data[image_url], 'x_scale': x, 'y_scale': y})
                pass
            else:
                sheet.write(I+1,i,data[I][info[i]])
    try:
        os.remove('1.png')
    except:
        try:
            os.remove('1.jpg')
        except:
            pass
    workbook.close()
    print("\033[1;36m所有操作已完成!\033[0m")
Data()
saveToXlsx()