import requests
import base64
import re
import xlsxwriter
from io import BytesIO
import tqdm
import random
import os
from PIL import Image
import queue
import threading
import json
from colorama import init
import time
init(autoreset=True)

"""选项菜单"""
def Menu():
    F = """
|------------------------------------------------------------------|
|  选项 |         功能                                             |
|-------|----------------------------------------------------------|
|   0   |    获取所有nsp中文游戏                                   |
|-------|----------------------------------------------------------|
|   1   |    获取所有nsp游戏                                       |
|-------|----------------------------------------------------------|
|   2   |    获取所有xci中文游戏                                   |
|-------|----------------------------------------------------------|
|   3   |    获取所有xci游戏                                       |
|-------|----------------------------------------------------------|
|   4   |获取所有switch游戏(由于数据过大偶现异常，请关闭程序重试)  |
|-------|----------------------------------------------------------|
|   5   |        游戏搜索                                         |
|------------------------------------------------------------------|
|   6   |        退出程序                                        |
|------------------------------------------------------------------|
    """
    print("\033[1;36m     （便捷小站，switch游戏）功能菜单\033[0m")
    print('\033[1;34m{0}\033[0m'.format(F))

def clear():
    if(os.name=='nt'):
        os.system('cls')
    else:
        os.system('clear')

"""要求用户输入Min到Max区内的�?,返回这个�?,F(是否显示选项菜单，兼容性设�?)"""
def Get_number(Min,Max,F = False):
    while True:
        try:
            if(F):
                Menu()
            print("\033[1m请输入\033[1;31m{0:<10}\033[0m\033[1m到\033[1;31m{1:>10}\033[0m\033[1m范围内的整数�?:\033[0m".format(Min,Max),end='')
            number = eval(input())
            if(F):
                if (os.name == 'nt'):
                    os.system('cls')
                else:
                    os.system('clear')
            if(type(number)!=int):
                print("\033[1;31m警告，请输入整数\033[0m")
                continue
            if(number>Max and True):
               print("\033[1;31m输入的数值超限\033[0m")
            elif(number<Min):
               print("\033[1;31m输入的数值过小\033[0m")
            else:
                if (F):
                    if (os.name == 'nt'):
                        os.system('cls')
                    else:
                        os.system('clear')
                return int(number)
        except:
            if (F):
                if (os.name == 'nt'):
                    os.system('cls')
                else:
                    os.system('clear')
            print("\033[1;31m输入的数值包含非法字符\033[0m")

"""
数据储存结构�?
{
"game_name":[....."url","key"]
}
"""
"""加载proxy代理节点"""
def load_proxy():
    proxy = []
    try:
        with open("proxy.txt",'r',encoding='utf-8') as f:
            data = f.read()
        for i in data.split('\n'):
            if i==[]:
                continue
            t  = i.split('|')
            P = {}
            P[t[0]] = t[1]
            proxy.append(P)
    except:pass
    return proxy

"""获取随机代理节点"""
def rand_proxy(proxies=[]):
    return  random.choice(proxies)

"""随机User—Agent"""
def Get_User_Agent():
    user_agent=[
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)'
    ]
    return random.choice(user_agent)

def load_data():
    data = {}
    try:
        with open("便携小站.json",'r',encoding='utf-8') as f:
            data = json.loads(f.read())
    except:pass
    return data
def save_data(data):
    try:
        with open("便携小站.json",'w',encoding='utf-8') as f:
            f.write(json.dumps(data))
    except:
        print("\033[1;31m数据储存失败\033[0m")
"""给定游戏名获取下载链接，返回类型[(url),(key)]"""
def get_download_link(game_name,M_queue,proxy=None):
    data={}
    KEY = "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|预览图片,游戏标题,下载网址,提取码|*|游戏标题 like '%{0}%'".format(game_name)
    data['captcha'] = base64.b64encode(KEY.encode('utf-8'))
    header = {
        'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
        'Cookie': 'ZDEDebuggerPresent=php; phtml=; php3=',
        'Cookie2': '$Version=1'
    }
    if(proxy==None):
        message = requests.post(data=data,headers=header,url='http://120.25.225.69/openapi_unsafe.php').content.decode('utf-8')
    else:
        message = requests.post(data=data, headers=header,
                                url='http://120.25.225.69/openapi_unsafe.php',proxies = proxy).content.decode('utf-8')
    data={}
    try:
        data[game_name]  =list(re.findall(r'.*?\|\.\+\.\|.*?\|\.\+\.\|(.*?)\|\.\+\.\|(.*?)\|\.\+\.\|',message)[0])
    except:
        data[game_name] = [message,""]
        print("ERROR INFO:\t",message)
    M_queue.put(data)
    time.sleep(1)

"""向服务器获取数据（返回分割完成的列表,F==True：开启调试缓存数据到本地message.txt�?"""
def Get_data(KEY,timeout=None,Search = False,F=False):
    data={}
    data['captcha'] = base64.b64encode(KEY.encode('utf-8'))
    print('\033[1;32m正在向服务器请求数据！\033[0m')
    header = {
        'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
        'Cookie': 'ZDEDebuggerPresent=php; phtml=; php3=',
        'Cookie2': '$Version=1'
    }
    message = ""
    while True:
        try:
            message = requests.post('http://120.25.225.69/openapi_unsafe.php', data=data, headers=header,timeout=timeout).content.decode('utf-8')
            break
        except:
            print('\033[1;31m请求失败，重试中。。。。\033[0m')
            continue
    Re = r'QrData'
    message = re.sub(Re, '', message)
    message = message.replace('\r','')
    message = message.replace('\n','')
    """             游戏类型        图片链接        游戏�?         """
    Re = r'\|\.\+\.\|(.*?)\|\.\+\.\|(.*?)\|\.\+\.\|(.*?)\|\.\+\.\|'
    m = re.findall(Re, message)
    if(F):
        f = open('message.txt','w+',encoding='utf-8')
        f.write(message)
        f.close()
    Thread_queue = queue.Queue()
    count=0
    if Search:
        data={}
    else:
        data=load_data()
    for i in m:
        if(i[2] in data):
            continue
        count+=1
    print('\033[1m共计\033[1;31m{0:^10}\033[0m\033[1m条数据需要下载\033[0m'.format(count))
    print("\033[1m请设置链接获取线程\033[0m")
    Thread_count=Get_number(1,os.cpu_count())
    proxies = load_proxy()
    T = tqdm.tqdm(total=len(m))
    M_queue = queue.Queue()
    for i in m:
        if(i[2] in data):
            pass
        else:
            if(proxies==[]):
                t = threading.Thread(target=get_download_link,args=(i[2],M_queue))
            else:
                t = threading.Thread(target=get_download_link,args=(i[2],M_queue,rand_proxy(proxies)))
            data[i[2]] = list(i)
            t.start()
            Thread_queue.put(t)
            if(Thread_queue.qsize()==Thread_count):
                t = Thread_queue.get()
                t.join()
                T.update(1)
    while Thread_queue.empty()==False:
        t = Thread_queue.get()
        t.join()
        T.update(1)
    T.close()
    while M_queue.empty()==False:
        t = M_queue.get()
        try:
            i = list(t.keys())[0]
            data[i]+=t[i]
        except:
            print("ERROR:",t)
    input('\033[1;32m数据获取成功！回车继续！\033[0m')
    clear()
    return data

def pare_data(data={}):
    Data=[]
    for i in data.keys():
        Data.append(data[i])
    return Data


"""要求用户输入一个路径（返回这个路径, T 自动添加的扩展名�?"""
def Get_path(T=""):
    path=''
    while True:
        try:
            path = input(
                '\033[1m输入文件导出路径（不含扩展名）或文件名（不含扩展名）\n(例如：name，C:\\Users\\Shinelon\\Desktop\\name)：\033[0m') + T
            f = open(path, 'w')
            f.close()
            break
        except:
            print("路径无效")
    return path

"""写入TXT文件（需要提供路径data,path�?"""
def Save_to_TXT(data,path):
    print('\033[1;32m正在写入数据TXT文档！\033[0m')
    f=open(path,'a+',encoding='utf-8')
    count = 1
    TQ = tqdm.tqdm(total=len(data))
    f.write('{0:*^50}\r\n'.format('共计'+str(len(data)),'条数�?'))
    for i in data:
        f.write('第{0}个\n'.format(str(count)))
        f.write('游戏类型：{0}游戏名：{1}\n图片链接：{2}\n下载地址：{3}\n提取码：{4}\r\n'.format(i[0],i[2],i[1],i[3],i[4]))
        count+=1
        TQ.update(1)
    TQ.close()
    print('\033[1;32m写入数据TXT文档成功！\033[0m')
"""使用菜单"""
def Using_Menu(n):
    if(os.name=='nt'):
        os.system('cls')
    else:
        os.system('clear')
    data = {}
    header = {
        'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
        'Cookie': 'ZDEDebuggerPresent=php; phtml=; php3=',
        'Cookie2': '$Version=1'
    }
    if(n!=5):
        Optiona_List = [
            "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏类型 = 'nsp中文游戏'",
            "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏类型 like '%nsp%'",
            "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏类型  = 'xci中文游戏'",
            "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏类型 like '%xci%'",
            "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏类型  like '%%'"
        ]
        return Get_data(Optiona_List[n])
    else:
        while True:
            print('\033[1m游戏�?(直接回车退�?)：\033[0m',end='')
            name = input()
            if (os.name == 'nt'):
                os.system('cls')
            else:
                os.system('clear')
            if(name==''):
                return  None
                break
            else:
                name = name.replace(' ','')
                KEY = "MSDATA120.25.225.69:3306|*||*||*|ziyuanku|*|utf8|*|QrData|*|ns便捷|*|id,游戏类型,预览图片,游戏标题|*|游戏标题 like '%"+name+"%'"
                Game_data = pare_data(Get_data(KEY,Search=True))
                size = len(Game_data)
                count=1
                if(size==0):
                    print('\033[1;31m没有查询到任何游戏！\033[0m')
                    continue
                print('\033[1m关键字：\033[1;31m{0}\033[0m \033[1m共有\033[1;32m{1}\033[0m\033[1m个游戏\033[0m'.format(name,size))
                print('\033[1m是否显示数据�?1：是   2：否）\033[0m')
                num = Get_number(1,2)
                if(num==1):
                    for i in Game_data:
                        print('\033[1m第\033[1;31m{0:^10}\033[0m\033[1m个游�?'.format(count))
                        print(
                            '\033[1m游戏类型：\033[1;42m{0}\r\n\033[0m\033[1m游戏名：\033[1;43m{1}\r\n\033[0m\033[1m图片链接：\033[1;47m{2}\r\n\033[0m\033[1m下载地址：\033[1;44m{3}\r\n\033[0m\033[1m提取码：\033[1;41m{4}\r\n\r\n\033[0m'.format(
                                i[0], i[2], i[1], i[3], i[4]))
                        count+=1
                else:
                    print('\033[1;31m跳过显示\033[0m')
                print('\033[1m是否写入文件\r\n(1:�?    2:�?)\033[0m')
                num = Get_number(1,2)
                if(num==1):
                    print('\033[1m写入文件类型( 1：xlsx（有图片�?   2：TXT(无图)    3:全部 )')
                    W_n = Get_number(1,3)
                    if(W_n==2 or W_n==3):
                        print('\033[1m请输入需要\033[1;43mTXT文件\033[0m\033[1m保存\033[0m')
                        path = Get_path('.txt')
                        Save_to_TXT(data=Game_data,path=path)
                    if(W_n==1 or W_n==3):
                        return Game_data
                    else:
                        continue
                else:
                    continue
                return None

"""进度显示（给定任务队列，根据队列剩余长度显示进度）（阻塞态）"""
def Show_tqdm(Q):
    num1 = Q.qsize()
    with tqdm.tqdm(total=num1) as T:
        size = Q.qsize()
        while Q.empty()==False:
            q = Q.qsize()
            if(size!=q):
                T.update(-q+size)
                size = q
        T.update(size)

"""多线程下载图�?(返回队列，包含以url为key的字�?)"""
def Get_Image(url_queue,image_queue,error_image_path,threade_count):
    if(os.name=='nt'):
        os.system('cls')
    else:
        os.system('clear')
    print("\033[1;36m开始缓存图片数据！\033[0m")
    threading_list = []
    for i in range(threade_count):
        t = threading.Thread(target=GI,args=(url_queue,image_queue,error_image_path))
        t.start()
        threading_list.append(t)
    Show_tqdm(Q=url_queue)
    print("\033[1;36m等待剩余线程完成！\033[0m")
    for i in threading_list:
        i.join()
    print("\033[1;36m图片数据缓存完成！\033[0m")
def GI(url_queue,image_queue,error_image):
    while url_queue.empty() == False:
        image_url = url_queue.get()
        URL = image_url
        data = None
        fail_count = 0
        while True:
            try:
                header = {}
                header['User-Agent'] = Get_User_Agent()
                if (len(re.findall(r'\.gif', image_url)) > 0):
                    print('\033[1;31m{0}\n发现不受支持的图片！\033[0m'.format(image_url))
                    fail_count = 20
                else:
                    respones = requests.get(image_url, headers=header, timeout=(3, 3))
                    if (respones.status_code == 200):
                        data = respones.content
                        break
                    else:
                        fail_count += 1
            except:
                fail_count += 1
            if (fail_count > 3):
                image_url='https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=137921156,3197104189&fm=26&gp=0.jpg'
        image_data = {}
        image_data[URL]=BytesIO(data)
        image_queue.put(image_data)
    return

"""将获取到的数据写入xlse表格"""
def Save_to_excel(data,path,image_width=22,image_higth=75):
     # x_dpi = None
     # y_dpi = None
     if (os.name == 'nt'):
         os.system('cls')
     else:
         os.system('clear')
     DU = re.compile('http')
     url_queue = queue.Queue()
     image_queue = queue.Queue()
     for i in data:
         if(data[0]=="重要公告"):
             continue
         url_queue.put(i[1])
     Get_Image(url_queue,image_queue,'ERROR.jpg',threade_count=20)
     image_data = {}
     while image_queue.empty()==False:
         image_data = dict(image_data,**image_queue.get())
     if (os.name == 'nt'):
         os.system('cls')
     else:
         os.system('clear')
     print("\033[1;36m开始写入表格！\033[0m")
     workbook = xlsxwriter.Workbook(path)
     sheet = workbook.add_worksheet()
     row = 0
     # 定义粗体�?
     bold = workbook.add_format({'bold': True})
     sheet.write(row, 0, '游戏类型', bold)
     sheet.write(row, 1, '游戏图片', bold)
     sheet.write(row, 2, '游戏名称', bold)
     sheet.write(row, 3, '下载地址', bold)
     sheet.write(row, 4, '提取�?', bold)
     sheet.set_column('A:A', 12)
     sheet.set_column('B:B', image_width + 6.4)
     sheet.set_column('C:C', 80)
     sheet.set_column('D:D', 50)
     sheet.set_column('E:E', 10)
     for i in tqdm.tqdm(data):
         if(i[0]=="公告"):
             continue
         row += 1
         game_type = i[0]
         image_url = i[1]
         game_name = i[2]
         try:
            download_url = i[3]
            download_key = i[4]
         except:
            print(i)
            download_key=""
            download_url=""
         print(image_url)
         sheet.write(row, 0, game_type)
         im = None
         try:
            im = Image.open(image_data[image_url])
         except:
            with open('1.jpg','wb') as f:
                f.write(image_data[image_url])
            im = Image.open(BytesIO(requests.get('https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=137921156,3197104189&fm=26&gp=0.jpg').content))
         # """图像DPI"""
         # try:
         #     x_dpi = im.info['dpi'][0]
         #     y_dpi = im.info['dpi'][1]
         # except:
         #     x_dpi = None
         #     y_dpi = None
         #     print("\033[1;31m{0}\n获取DPI失败！\033[0m".format(image_url))
         #     pass
         """图像尺寸"""
         x_size = im.size[0]
         y_size = im.size[1]
         # """获取图像物理尺寸"""
         # if(x_dpi==None):
         #     x_real = x_size / 72 * 2.54 * 30 / 72
         #     y_real = y_size / 72 * 2.54 * 30 / 72
         # else:
         #     x_real = x_size / x_dpi * 2.54 * 30 / x_dpi
         #     y_real = y_size / y_dpi * 2.54 * 30 / y_dpi
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
         sheet.set_row(row, image_higth + 18)
         sheet.insert_image(row, 1, image_url, {'url':image_url,'image_data': image_data[image_url], 'x_scale': x, 'y_scale': y})
         sheet.write(row, 2, game_name)
         if (len(DU.findall(download_url)) == 0):
             download_url = 'https://' + download_url
         sheet.write(row, 3, download_url)
         sheet.write(row, 4, download_key)
     try:
        os.remove("1.jpg")
     except:pass
     try:
        os.remove("1.png")
     except:pass
     workbook.close()
     if (os.name == 'nt'):
         os.system('cls')
     else:
         os.system('clear')
     print("\033[1;36m表格写入完成！\033[0m")

"""主函�?"""
def BMain():
    while True:
        num = Get_number(0, 6, True)
        if(num==6):
            break
        data = Using_Menu(num)
        if (data != None):
            U=re.compile("http")
            print('\033[1m共计\033[1;31m{0:^10}\033[0m\033[1m条数据\033[0m'.format(len(data)))
            print("\033[1;42m是否转储到本地：百度网盘分享链接.txt�?1：是   2：否）\033[0m:")
            if(Get_number(1,2)==1):
                print("\033[1;42m是否使用日志模板过滤链接�?1:�?     2：否）\033[0m")
                GL = {}
                if(Get_number(1,2)==1):
                    try:
                        with open('便携小站.json','r',encoding='utf-8') as f:
                            GL = json.loads(f.read())
                            print("加载本地日志成功�?")
                    except:
                        print("加载本地日志失败�?")
                with open('百度分享链接.txt',"w",encoding='UTF-8') as f:
                    for i in data.keys():
                        if(i in GL.keys()):
                            continue
                        if data[i][2]=="公告":
                            continue
                        if(len(U.findall(data[i][-2]))==0):
                            f.write('{0}|{1}|{2}\n'.format(data[i][2],"https://"+data[i][-2],data[i][-1]))
                        else:
                            f.write('{0}|{1}|{2}\n'.format(data[i][2],data[i][-2], data[i][-1]))
            print("\033[1;42m是否转储日志到：便携小站.json�?1：是   2：否）\033[0m")
            if(Get_number(1,2)==1):
                with open('便携小站.json','w',encoding='utf-8') as f:
                    f.write(json.dumps(data))
            path = ""
            print('\033[1m请输入需要\033[1;42mXlsx文件\033[0m\033[1m保存\033[0m')
            path = Get_path('.xlsx')
            Save_to_excel(pare_data(data), path)
BMain()