'''
Created on Sun Sep 22 13:59:00 2019
@author: 
'''
import re
import requests
import threading
import queue
from tqdm import tqdm
import os
from colorama import init
import json
import xlrd
init(autoreset=True)
def verify_key(url,password=None):
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
    return JS['errno']

def Get_number(Min,Max,F = False):
    while True:
        try:
            if(F):
                pass
            print("\033[1m请输入\033[1;31m{0:<10}\033[0m\033[1m到\033[1;31m{1:>10}\033[0m\033[1m范围内的整数值:\033[0m".format(Min,Max),end='')
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
def load_url_from_xls():
    U = re.compile('http')
    data=[]
    try:
        table = xlrd.open_workbook('百度分享链接.xls').sheet_by_name('Sheet1')
    except:
        print("\033[1;31m数据加载失败\n请检查表格是否与程序在同一个目录下（百度分享链接.xls）\n且表单名称为：Sheet1")
        print("\033[1;32m回车退出\033[0m")
        input()
        return data
    for i in range(table.nrows):
        cell=[]
        for t in range(table.ncols):
            url = table.cell(i,t).value
            try:
                url = int(url)
                url = str(url)
            except:
                pass
            url = url.replace(' ','')
            url = url.replace('?','')
            if t==0:
                if len(U.findall(url))==0:
                    url = 'https://'+url
            cell.append(url)
        data.append(cell)
    print('成功加载\033[1;32m{0}\033[0m条链接'.format(len(data)))
    return data

def load_url():
    data=[]
    U = re.compile('http')
    try:
        with open('百度分享链接.txt','r',encoding='utf-8') as f:
            H = f.read()[1:]
            for i in H.split('\n'):
                try:
                    F = i.split('|')
                    G = []
                    F[1]=F[1].replace(' ','')
                    F[1]=F[1].replace('?','')
                    F[2]=F[2].replace(' ','')
                    if len(U.findall(F[1]))==0:
                        F[1]='https://'+F[1]
                    G.append(F[1])
                    G.append(F[2])
                    G.append(F[0])
                    data.append(G)
                except:
                    print("此行数据存在问题，无法加载：\033[1;31m{0}\033[1m".format(i))
    except:
        pass
    if(len(data)==0):
        print("\033[1;31m加载测试链接失败\033[1m")
        print('\033[1;31m没有找到测试文件\n请将测试文件(\033[1;32m百度分享链接.txt\033[1;31m)与本程序放在同一目录\033[0m')
        help()
        input("回车退出")
        exit()
    else:
        print('成功加载\033[1;32m{0}\033[0m条链接'.format(len(data)))
    return data
def Test(Panurl,OK_Panurl,i,T=False):
    header={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    if len(Panurl.findall(i[0]))==0:
        with open("其他分享链接.txt",'a',encoding='utf-8') as f:
            f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
        return
    if i[1]=='':
        with open("无提取码的分享链接.txt",'a',encoding='utf-8') as f:
            f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
        return
    fail_count=0
    while True:
        try:
            page = requests.get(url = i[0],headers = header).content.decode('utf-8')
            break
        except:
            if(fail_count>=10):
                print("\033[31m链接：{0} 失败次数过多！\033[0m".format(i[0]))
                with open("失效的分享链接.txt", 'a', encoding='utf-8') as f:
                    f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
                return
            print("\033[31m服务器异常，正在重试第{0}次\033[0m".format(fail_count+1))
            fail_count+=1
    if  len(OK_Panurl.findall(page))==0 :
        with open("失效的分享链接.txt",'a',encoding='utf-8') as f:
            f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
        return
    E = True
    if(T):
        fail_count=0
        while True:
            try:
                K = verify_key(i[0],i[1])
                break
            except:
                if(fail_count>=10):
                    print("\033[31m链接：{0} 失败次数过多！\033[0m".format(i[0]))
                    with open("失效的分享链接.txt", 'a', encoding='utf-8') as f:
                        f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
                    return
                print("\033[31m服务器异常，正在重试第{0}次\033[0m".format(fail_count+1))
            fail_count+=1
        if(K!=0):
            with open("提取码有误.txt",'a',encoding='utf-8') as f:
                f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
            E = False
    if(E):
        with open("有效分享链接.txt",'a',encoding='utf-8') as f:
            f.write("{0}    链接:{1} {2:>20}\n".format(i[2],i[0],"提取码："+i[1]))
    return
def help():
    print('格式(无论有没有提取码都需要加\033[1;36m|\033[0m)：\033[1;32m链接\033[1;36m|\033[1;32m提取码\033[0m')
    print("\033[1;32m一个测试链接为一行\033[0m")
def Main():
    Help = """
    使用说明：
    1.支持txt文本数据和xls表格数据
    
    2.针对表格数据：
    表格与程序在同一目录
    文件名为：百度分享链接.xls
    表格A列:为链接，表格B列:为提取码，表单名称：Sheet1
    
    3.针对txt文本数据：
    文件与程序在同一目录
    文件名：百度分享链接.txt
    储存格式：分享链接|提取码（一行为一个测试数据，无论数据是否需要提取码都要加|分割）
    
    4.关于速度：
    线程可以提高速度（服务器响应需要时间，线程并发提高时间利用率）
    但是长时间的大量链接访问，服务器会增加对每一个链接得响应时间，
    或者直接不响应，这个导致程序假死（可适当减少线程数目），程序会重复尝试失败链接来解决这样
    的问题(单链接最大尝试次数10次，超过，将链接作为：失效的分享链接处理)，目前20线程下，未发现
    这样的情况。
    
    5.结果以txt文档储存，每次测试完成后请清理这写文件，否则会产生数据堆叠
    
    6.关于验证提取码正确性:
    这个使用了百度api进行验证，但是频繁验证可能会有难以预料的问题（20线程下有小概率问题，解决方法如上）。
    
    """
    print("\033[1;33m{0}\033[0m".format(Help))
    print('\033[1;31m    本软件完全免费，仅供学习交流使用，禁止倒卖！\033[0m')
    input("回车继续")
    os.system('cls')
    print('\033[1;32m选择数据加载方式(1:从\033[1;33m百度分享链接.txt加载数据\033[0m  \033[1;32m2：从 \033[1;33m百度分享链接.xls \033[1;32m加载数据)')
    Data=None
    if 2 == Get_number(1,2):
        os.system('cls')
        Data = load_url_from_xls()
    else:
        os.system('cls')
        Data=load_url()
    input("回车继续")
    os.system('cls')
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    Panurl = re.compile("pan.baidu.com/s/")
    OK_Panurl = re.compile("请输入提取码")
    size = len(Data)
    if(size==0):
        exit()
    print("\033[1;32m是否验证提取码有效性（会增加耗时）,1:使用  2：放弃")
    T = False
    if 1 == Get_number(1,2):
        T = True
    os.system('cls')
    print("请设置线程数目（过大程序会卡死，百度服务器不响应，推荐：20）")
    count = Get_number(1,500)
    os.system('cls')
    print("\033[1;32m开始测试\033[0m")
    thread_queue = queue.Queue()
    T = tqdm(total=size)
    for i in Data:
        t = threading.Thread(target=Test,args=(Panurl,OK_Panurl,i,T))
        t.start()
        thread_queue.put(t)
        if thread_queue.qsize()== count:
            i = thread_queue.get()
            i.join()
            T.update(1)
    while thread_queue.empty()==False:
        i = thread_queue.get()
        i.join()
        T.update(1)
    T.close()
    os.system('cls')
    input("测试完毕，回车退出")
if __name__ == '__main__':
    Main()