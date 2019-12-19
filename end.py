import requests
import json
import re
import queue
import os
import time
from tqdm import tqdm
from  selenium.webdriver import ChromeOptions
from  selenium.webdriver import Chrome
def convert_cookie(chrome_cookie):
    """从chrome.get_cookies()中获取必要cookie信息
    
    :param chrome_cookie: chrome_cookie:由selenium产生的cookie
    :return: 返回为string，cookie字符,供requests使用
    """
    cookie = ""
    for i in chrome_cookie:
        if ("BDUSS" == i['name']):
            cookie += "BDUSS=" + i['value'] + ";"
        if ("STOKEN" == i['name']):
            cookie += "STOKEN=" + i['value'] + ";"
        if ("BDCLND" == i['name']):
            cookie += "BDCLND" + i['value'] + ";"
    return cookie

def check_file(cookie,filename):
    """检查文件是否被被存储
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :param filename: 查询的文件名
    :return: True已被存储，False没有被存储
    
    """
    F = search_file(cookie,filename)
    if(len(F)!=0):
        return True
    else:
        return False

def save_share(cookie,url,password=None,path=""):
    """保存分享链接（注意：cookie必须包含BDCLND（当浏览器保存一次分享链接后会在cookie中出现））
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :param url: 分享链接的完整地址
    :param password: 链接提取码
    :param path: 保存路径（绝对路径）
    :return: 0 储存成功， 1 分享链接错误，12 文件保存失败（储存空间不足），-21 链接失效，-9 pwd错误。
    """
    R = r'pan.baidu.com/s/1(\S+)'
    try:
        surl = re.findall(R,url)[0]
    except:
        return 1
    """外链验证"""
    url = "https://pan.baidu.com/share/verify?surl=" + surl
    data = {
            "pwd": password,
        }
    params = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer':'pan.baidu.com'
        }
    r=requests.post(url,data=data,headers=params)
    JS = json.loads(r.content)
    """外链验证结果"""
    if(JS['errno']!=0):
        return JS['errno']
    sekey=JS['randsk']
    """获取链接信息"""
    url="https://pan.baidu.com/share/list?shareid={0}&shorturl={1}&sekey={2}&root=1".format('',surl,sekey)
    r=requests.get(url,headers=params)
    file = json.loads(r.content)
    """提取fsid列表"""
    fsid=[]
    if(file['errno']!=0):
        return file['errno']
    for i in file['list']:
        fsid.append(eval(i['fs_id']))
    """转储必要信息为字典"""
    url = "https://pan.baidu.com/share/transfer?shareid={0}&from={1}&sekey={2}".format(file['share_id'],file['uk'],JS['randsk'])
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie'] = cookie
    post = {
        'fsidlist': json.dumps(fsid),
        'path':path
    }
    try:
        Z = requests.post(url, headers=header, data=post).text
        r = json.loads(Z)
    except:
        red(Z)
        return -100
    if(r['errno']==12):
        for i in file['list']:
            if(check_file(cookie,i['server_filename'])==False):
                M = check_free(cookie)
                M = (M['total'] - M['used'])/1024/1024/1024
                if(M>20):
                    return -100
                else:
                    return 12
        return 0
    return r['errno']

def load_cookie():
    """加载本地cookie

    :return: 返回为储存在本地的chrome cookie
    """
    Cookie = []
    try:
        with open('Cookie.json', 'r', encoding='utf-8') as f:
            for i in json.loads(f.read()):
                try:
                    del i['expiry']
                except:
                    pass
                Cookie.append(i)
    except:
        print('加载Cookie失败！')
    return Cookie

def get_file_name(file_name="", Char=""):
    """去除文件夹的名称中的不合法字符为Char，默认为空

    :param Char:替换成的字符
    :param file_name: 
    :return: 
    """
    for i in '<>|*?,/:':
        file_name = file_name.replace(i, Char)
    return file_name

def build_chrome(cookie=None):
    """构建浏览器

    :param cookie: selenium list类型的cookie
    :return: 返回构建完成的chrome浏览器
    """
    chrome_options = ChromeOptions()
    chrome = Chrome(chrome_options=chrome_options)
    chrome.get('http://pan.baidu.com')
    if (cookie != None or cookie != []):
        for i in cookie:
            try:
                del i['expiry']
            except:
                pass
            chrome.add_cookie(i)
    chrome.refresh()
    return chrome

def load_url_list():
    """加载本地分享链接数据(百度分享链接.txt)

    :return: 返回list类型的链接列表
    """
    data = []
    try:
        with open("百度分享链接.txt", 'r', encoding='utf-8') as f:
            for i in f.read().split('\n'):
                i=i.replace('?','')
                F = i.split('|')
                F[0]=get_file_name(F[0])
                data.append(F)
        print("加载数据成功！\n共计 {0}条".format(len(data)))
    except:
        print("加载数据失败！")
    return data

def create_folder(cookie, path, isdir=1):
    """创建文件/文件夹

            :param path:文件绝对路径（含需要创建文件/目录）

            :param isdir: 0 文件、1 目录
            
            :return 返回创建好的文件的绝对路径
            """
    data = {
        "path": '/' + path,
        "isdir": isdir,
        "size": "",
        "block_list": "[]",
        "method": "post"
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
        # 'cookie':'BDUSS=lyS3lOWVg4VjIxbmNOeWFUTnhqd3Z2NX5meE1nc0VoWVgyOEx6dXNkY2NySnhkRVFBQUFBJCQAAAAAAAAAAAEAAAA1bYmSaWhiNTQyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwfdV0cH3VdR3; STOKEN=9a1a4c2ca3a9711e77da92afd089f69a1732ef786a77488c38f12397e21c4103; '
    }
    header['cookie'] = cookie
    url = "https://pan.baidu.com/api/create?a=commit&channel=chunlei&app_id=250528"
    r = requests.post(url=url, headers=header, data=data).text
    return json.loads(r)['path']

def delete_files(cookie,path):
    """删除文件
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :param path: 这个为要删除的文件的绝对路径（可以传递路径列表，也可以传递单一 string绝对路径）
    :return: 返回errno，目前没有意义
    """
    url = 'https://pan.baidu.com/api/filemanager?opera=delete&async=2&onnest=fail&channel=chunlei&web=1&app_id=250528&clienttype=0'
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer':'pan.baidu.com'
    }
    header['cookie'] = cookie
    if(type(path)!=list):
        filelist = [path]
    else:
        filelist = path
    data={
    'filelist': json.dumps(filelist)
    }
    r = requests.post(url=url,data=data,headers = header).text
    return  json.loads(r)['errno']

def share_files(cookie,fid_list, pwd, days=7):
    """创建分享
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :param fid_list: 文件id列表
    :param pwd:  分享密码（4位不同的数字或字母）
    :param days: 外链有效期，0 永久、1 1天、7 7天，默认0
    :return: 响应
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie']=cookie
    url = "https://pan.baidu.com/share/set?channel=chunlei&clienttype=0&web=1&channel=chunlei&web=1&app_id=250528&clienttype=0"
    data = {
        'schannel': '4',
        'channel_list': json.dumps([]),
        'period': days,
        'pwd': pwd,
        'fid_list': json.dumps(fid_list)
    }
    r = requests.post(url=url, headers=header, data=data).text
    return json.loads(r)

def convert_size(number):
    """转换网盘容量

            :param number: 整数

            :return: 返回string
            """
    if (number < 1024):
        return '{0:.2f} Byte'.format(number)
    number /= 1024
    if (number < 1024):
        return '{0:.3f} KB'.format(number)
    number /= 1024
    if (number < 1024):
        return '{0:.3f} MB'.format(number)
    number /= 1024
    if (number < 1024):
        return '{0:.3f} GB'.format(number)
    number /= 1024
    return '{0:.3f} TB'.format(number)

def user_name(cookie):
    """获取用户信息（测试cookie有效性）
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :return: 用户名
    """
    url = 'https://passport.baidu.com/center'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie'] = cookie
    r = requests.get(url=url, headers=header).content.decode('utf-8')
    f = re.findall(r'"displayUsername"\s+title="(.*?)">', r)
    return f[0]

def check_free(cookie):
    """获取网盘容量
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
    :return: 结果例子：{"errno":0,"total":2204391964672,"request_id":5929092093134126170,"expire":null,"used":2203832252091}
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie'] = cookie
    page = requests.get('https://pan.baidu.com/api/quota?chckfree=1&checkexpire=1', headers=header).text
    return json.loads(page)

def get_file_list(cookie, path="/"):
    """获取用户文件列表
    
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到       
    :param path: 获取文件路径   
    :return: 返回None为失败
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie'] = cookie
    header['dir'] = path
    url = 'https://pan.baidu.com/api/list?'
    r = requests.get(url=url, headers=header).content.decode('utf-8')
    F = None
    try:
        F = json.loads(r)
    except:
        pass
    return F['list']

def search_file(cookie,file_name):
    """文件搜索

    :param file_name: 搜索的关键字
    :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到  
    :return: 返回：file_list
    结果:[{'category': 6, 'unlist': 0, 'isdir': 1, 'oper_id': 1066838869, 'server_ctime': 1568999679, 'local_mtime': 1568999679, 'size': 0, 'server_filename': '\ufeff《死在文兰DeadInVinland》中文版nsp下载', 'share': 0, 'path': '/\ufeff《死在文兰DeadInVinland》中文版nsp下载', 'local_ctime': 1568999679, 'server_mtime': 1568999679, 'fs_id': 99524860442047}]
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'pan.baidu.com'
    }
    header['cookie'] = cookie
    url = 'https://pan.baidu.com/api/search?key={0}'.format(file_name)
    r = requests.get(url=url, headers=header).content.decode('utf-8')
    return json.loads(r)['list']

def save_chrome_cookie(cookie):
    """保存Cookie到本地

    :param cookie: selenium产生的cookie 
    :return: 返回bool类型值，true成功，false失败
    """
    try:
        with open('Cookie.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(cookie))
        return True
    except:
        return False

def Blue(text,T=False):
    """背景蓝
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if(T):
        print("\033[1;46m{0}\033[0m".format(text),end="")
    else:
        print("\033[1;46m{0}\033[0m".format(text))

def blue(text,T=False):
    """蓝字
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if(T):
        print("\033[1;36m{0}\033[0m".format(text),end="")
    else:
        print("\033[1;36m{0}\033[0m".format(text))

def Green (text,T=False):
    """背景绿
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if (T):
        print("\033[1;42m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;42m{0}\033[0m".format(text))

def green (text,T=False):
    """绿字
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if (T):
        print("\033[1;32m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;32m{0}\033[0m".format(text))

def yellow(text,T=False):
    """黄字
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if (T):
        print("\033[1;33m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;33m{0}\033[0m".format(text))

def red(text,T=False):
    """红字
    
    :param text: 
    :param T: 是否换行
    :return: 
    """
    if (T):
        print("\033[1;31m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;31m{0}\033[0m".format(text))

def code(code):
    if(code==-21):
        return "分享的文件已经被取消"
    if (code ==12):
        return "储存已满"
    if (code ==105):
        return "外链地址错误"
    if (code ==-12):
        return "参数错误"
    if (code ==-9):
        return "pwd错误"
    if (code ==110):
        return "文件命中频控策略"
    if (code ==-7):
        return "shareid不存在"
    if (code ==115):
        return "文件命中黑名单禁止分享"
    if (code ==-70):
        return "分享文件存在病毒"
    if (code ==0):
        return "成功"
    if(code==-100):
        return "文件过大"
    if(code==1):
        return "错误链接"
    return str(code)
def safe_writer(f,i):
    if(i==[]):
        return 
    if(len(i)==1):
        f.write(i[0]+"||\n")
    elif(len(i)==2):
        f.write(i[0]+"|"+i[1]+"|\n")
    else:
        f.write(i[0]+"|"+i[1]+"|"+i[2]+"\n")

url = load_url_list()
C = load_cookie()
chrome = build_chrome(cookie=C)
input("继续:")
cookie = convert_cookie(chrome.get_cookies())
save_chrome_cookie(chrome.get_cookies())
FF = True
count =1
size = len(url)
for i in url:
    G = None
    if(len(i)!=1):
        try:
            print("链接：{0}\n进度：{1}/{2} = {3:.2f}%".format(i[1],count,size,count*100/size))
        except:
            print("ERROR_Mage:{0}".format(i))
    else:
        continue
    count+=1
    if(FF):
        if(len(i)==3):
            G = create_folder(cookie=cookie,path=i[0])
            C = save_share(cookie=cookie, url=i[1], password=i[2], path=G)
        else:
            print("错误链接！")
            with open('BAD_URL.txt', 'a', encoding='utf-8') as f:
                safe_writer(f, i)
            print('')
            continue
        print("文件", end='    ')
        print(i[0], end='    ')
        print("存储在", end='    ')
        print(G)
        print("状态：",end='  ')
        print(code(C))
        print("")
        if (C == 0):
            continue
        if (C == -100):
            with open('BIG_FILE.txt', 'a', encoding='utf-8') as f:
                safe_writer(f,i)
        elif (C == -9):
            with open('pwd错误.txt', 'a', encoding='utf-8') as f:
                safe_writer(f, i)
        else:
            with open('BAD_URL.txt', 'a', encoding='utf-8') as f:
                safe_writer(f, i)
        delete_files(cookie, G)
    else:
        with open('NO_SAVE.txt','a',encoding='utf-8') as f:
            safe_writer(f, i)
        continue
    if(C == 12 and FF==True):
        FF = False
        print("写入NO_SAVE.txt")
input("退出：")
chrome.quit()