import requests
import json
import time
from tqdm import  tqdm
import re
from urllib.parse import urlencode
import random
import queue
from  selenium.webdriver import ChromeOptions
from  selenium.webdriver import Chrome
from concurrent.futures import ThreadPoolExecutor,as_completed
from hashlib import md5
import  os
class BaiDuPan:
    """
    百度网盘api
    删除文件： delete_files
    创建文件夹： create_folder
    文件上传： upload_file
    解析分享链接(获取文件结构，大小，需要将返回值调用show_file,不推荐暴力解析会导致链接被取消)：get_share_file_list
    保存分享文件（破解文件数量转存限制）： save_share
    上传文件（只支持文件，不支持文件夹）：upload_file
    """
    def __init__(self,cookie,log=False,path='/',bulid_chrome=True):
        self.log = log
        self.use_time = queue.Queue()
        self.short_url = None
        self.cookie = cookie
        self.path = path
        self.split_size = 400
        if(bulid_chrome):
            self.chrome = self.build_chrome()
            self.green("请确认登录后继续，确保完成创建！",True)
            input()
            self.updata_cookie()

    def close(self):
        """
        关闭浏览器
        :return:
        """
        self.chrome.quit()

    def updata_cookie(self):
        """
        升级cookie
        :return:
        """
        try:
            self.green("升级cookie成功！")
            self.cookie = self.convert_cookie(self.chrome.get_cookies())
        except Exception as e:
            self.red("升级cookie失败{0}".format(e))

    def Get_User_Agent(self):
        """
        获取随机User_Agent
        :return:
        """
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
    def green(self,text, T=False):
        """绿字
        :param text:
        :param T: 是否换行
        :return:
        """
        if (T):
            print("\033[1;32m{0}\033[0m".format(text), end="")
        else:
            print("\033[1;32m{0}\033[0m".format(text))

    def red(self,text, T=False):
        """红字

        :param text:
        :param T: 是否换行
        :return:
        """
        if (T):
            print("\033[1;31m{0}\033[0m".format(text), end="")
        else:
            print("\033[1;31m{0}\033[0m".format(text))


    def blue(self,text, T=False):
        """蓝字

        :param text:
        :param T: 是否换行
        :return:
        """
        if (T):
            print("\033[1;36m{0}\033[0m".format(text), end="")
        else:
            print("\033[1;36m{0}\033[0m".format(text))

    def yellow(self,text, T=False):
        """黄字

        :param text:
        :param T: 是否换行
        :return:
        """
        if (T):
            print("\033[1;33m{0}\033[0m".format(text), end="")
        else:
            print("\033[1;33m{0}\033[0m".format(text))

    def verify_share(self,url, password=None):
        """
        验证并解析链接
        :param url: 分享链接的完整地址
        :param password: 链接提取码
        :return: 返回分享链接根目录下的文件列表
        """
        time.sleep(1)
        R = r'pan.baidu.com/s/1(\S+)'
        try:
            surl = re.findall(R, url)[0]
            self.short_url = 'https://pan.baidu.com/share/init?surl='+surl
        except:
            return 1
        """外链验证"""
        url = "https://pan.baidu.com/share/verify?surl=" + surl
        data = {
            "pwd": password,
        }
        params = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': 'pan.baidu.com'
        }
        self.blue("正在获取链接验证密匙")
        r = requests.post(url, data=data, headers=params)
        JS = json.loads(r.content)
        """外链验证结果"""
        if (JS['errno'] != 0):
            return JS
        sekey = JS['randsk']
        """获取链接信息"""
        url = "https://pan.baidu.com/share/list?shareid={0}&shorturl={1}&sekey={2}&root=1".format('', surl, sekey)
        r = None
        self.blue("正在验证密匙")
        time.sleep(1)
        while True:
            try:
                r = requests.get(url, headers=params)
                if(r.status_code!=200):
                    continue
            except Exception as e:
                self.red("请求验证密匙失败")
                continue
            break
        file = json.loads(r.content.decode('utf-8'))
        file['sekey'] = sekey
        self.sekey = sekey
        self.share_id = file['share_id']
        self.uk = file['uk']
        if(self.log):
            print(file)
        return file


    def convert_cookie(self,chrome_cookie):
        """从chrome.get_cookies()中获取必要cookie信息

        :param chrome_cookie: chrome_cookie:由selenium产生的cookie
        :return: 返回为string，cookie字符,供requests使用
        """
        cookie = ""
        try:
            for i in chrome_cookie:
                if ("BDUSS" == i['name']):
                    cookie += "BDUSS=" + i['value'] + ";"
                if ("STOKEN" == i['name']):
                    cookie += "STOKEN=" + i['value'] + ";"
                if ("BDCLND" == i['name']):
                    cookie += "BDCLND=" + i['value'] + ";"
        except:pass
        return cookie

    def build_chrome(self):
        """构建浏览器

        :param cookie: selenium list类型的cookie
        :return: 返回构建完成的chrome浏览器
        """
        chrome_options = ChromeOptions()
        chrome = Chrome(chrome_options=chrome_options)
        chrome.get('http://pan.baidu.com')
        if(type(self.cookie)==str):
            for i in cookie.split(';'):
                I = i.split('=')
                if(len(I)>=2):
                    chrome.add_cookie({'name':I[0],'value':I[1]})
                else:
                    pass
        else:
            if (self.cookie != None):
                for i in self.cookie:
                    try:
                        del i['expiry']
                    except:
                        pass
                    chrome.add_cookie(i)
        chrome.refresh()
        return chrome
    def get_file_name(self,file_name="", Char=None,REPLACE = ""):
        """
        去除文件夹的名称中的不合法字符为Char，默认为空
        :param Char:替换成的字符，空值使用默认值
        :param file_name:文件名
        :return:
        """
        if not Char:
            Char = '<>|*?,/:'
        for i in Char:
            file_name = file_name.replace(i, REPLACE)
        return file_name

    def load_cookie(self,):
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
        self.cookie =  self.convert_cookie(Cookie)
        return Cookie

    def load_url_list(self,):
        """加载本地分享链接数据(百度分享链接.txt)

        :return: 返回list类型的链接列表
        """
        data = []
        try:
            with open("百度分享链接.txt", 'r', encoding='utf-8') as f:
                for i in f.read().split('\n'):
                    i=i.replace('?','')
                    F = i.split('|')
                    F[0]=self.get_file_name(F[0])
                    data.append(F)
            print("加载数据成功！\n共计 {0}条".format(len(data)))
        except:
            print("加载数据失败！")
        return data


    def delete_files(self, path):
        """删除文件
        :param path: 这个为要删除的文件的绝对路径（可以传递路径列表，也可以传递单一 string绝对路径）
        :return: 返回errno，目前没有意义
        """
        url = 'https://pan.baidu.com/api/filemanager?opera=delete&async=2&onnest=fail&channel=chunlei&web=1&app_id=250528&clienttype=0'
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] = self.cookie
        if (type(path) != list):
            filelist = [path]
        else:
            filelist = path
        data = {
            'filelist': json.dumps(filelist)
        }
        r = requests.post(url=url, data=data, headers=header).text
        return json.loads(r)['errno']

    def convert_size(self,number):
        """转换网盘容量

        :param number: 整数
        :return: 返回string
        """
        min_size = 1024
        if (number < min_size):
            return '{0:.2f} Byte'.format(number)
        number /= min_size
        if (number < min_size):
            return '{0:.3f} KB'.format(number)
        number /= min_size
        if (number < min_size):
            return '{0:.3f} MB'.format(number)
        number /= min_size
        if (number < min_size):
            return '{0:.3f} GB'.format(number)
        number /= min_size
        return '{0:.3f} TB'.format(number)

    def create_folder(self, path, isdir=1):
        """创建文件/文件夹

        :param path:文件绝对路径（含需要创建文件/目录
        :param isdir: 0 文件、1 目
        :return 返回创建好的文件的绝对路径
        """
        if(path==''):
            self.blue("创建完成:{0}".format(path))
            return '/'
        data = {
            "path":  path,
            "isdir": isdir,
            "size": "",
            "block_list": "[]",
            "method": "post"
        }
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] = self.cookie
        url = "https://pan.baidu.com/api/create?a=commit&channel=chunlei&app_id=250528"
        r = None
        self.blue("正在创建文件夹：" + path)
        while True:
            try:
                r = requests.post(url=url, headers=header, data=data, timeout=2).text
            except Exception as e:
                self.red("创建文件夹失败")
                continue
            break
        if(self.log):
            print(json.loads(r))
        self.blue("创建完成:{0}".format(json.loads(r)['path']))
        return json.loads(r)['path']

    def get_share_file_list(self,url,password=None,max_workers=5,verify_data=None,fast_mode = False,Create_folder=False):
        """
        获取文件列表/储存大文件

        :param url:分享链接
        :param password: 密码
        :param max_workers: 爬取线程(递归式创建)
        :param verify_data:验证数据
        :param fast_mode:是否储存文件（加速文件存储）
        :return:
        """
        file_data = verify_data
        if(file_data==None):
            file_data = self.verify_share(url=url,password=password)
        params = {
            'order': 'name',
            'shareid': file_data['share_id'],
            'desc': 1,
            'uk': file_data['uk'],
            'web': 1,
            'showempty': 0,
            'page': 1,
            'num': 100000,
            'bdstoken': '23f12119806c1d8a60c509572af64c5e',
            'logid': 'MTU4MDU4MDk3NzY2ODAuNDc1NTA4NDY4NzA5MTQ3Mw==',
            'app_id': 250528,
            'dir':self.path
        }
        header = {
            'cookie':"BDCLND={0};".format(file_data['sekey'])
        }
        return self.GSFL(file_data,params,header,{},max_workers,fast_mode=fast_mode,Create_folder=Create_folder)

    def GSFL(self,file_data,params,header,file_list={},max_workers = 5,fast_mode = False,Create_folder=False):
        file_list_url = 'https://pan.baidu.com/share/list?'
        dir = params['dir']
        self.green("开始解析：{0}".format(dir))
        file_list[dir] = []
        if(Create_folder or fast_mode):
            if(dir!=self.path):
                root_path = self.create_folder(self.path+dir)
            else:
                root_path = self.path
        Pool=None
        if(max_workers!=0):
            Pool = ThreadPoolExecutor(max_workers = max_workers)
        if(fast_mode):
            fast_mode_pool = ThreadPoolExecutor(max_workers = max_workers)
            fast_mode_tasks = []
        tasks=[]
        try:
            for i in file_data['list']:
                if(i['isdir']=='1' or i['isdir']==1):
                    if (fast_mode):
                        args = [root_path, [int(i['fs_id'])], file_data]
                        Args = [args,i['path']]
                        fast_mode_tasks.append(fast_mode_pool.submit(self.fast_mode_process,Args))
                    else:
                        params['dir'] = i['path']
                        arguments = [file_list_url, header, params.copy(), 0]
                        if (max_workers == 0):
                            data = self.POST(arguments)
                            params['dir'] = data[0]
                            self.GSFL(data[1], params.copy(), header, file_list, max_workers)
                        else:
                            tasks.append(Pool.submit(self.POST, (arguments)))
                else:
                    file_list[dir].append(i)
            if fast_mode :
                # 储存模块start
                Args = [root_path, file_list[dir]]
                fast_mode_tasks.append(fast_mode_pool.submit(self.save_mode,(Args)))
                # 储存模块end
                for i in as_completed(fast_mode_tasks):
                    if(i.result()==None):
                        continue
                    respones = i.result()[0]
                    if respones['errno'] == 0:
                        self.green("储存文件夹：{0}\t成功！".format(i.result()[-1]))
                        continue
                    if self.log:
                        self.red("返回信息：{0}".format(respones))
                    self.blue("尝试储存文件：{0}\t失败！\t启用递归方式解析文件并存储".format(i.result()[-1]))
                    params['dir'] = i.result()[-1]
                    arguments = [file_list_url, header, params.copy(), 0]
                    if (max_workers == 0):
                        data = self.POST(arguments)
                        params['dir'] = data[0]
                        self.GSFL(data[1], params.copy(), header, file_list, max_workers)
                    else:
                        tasks.append(Pool.submit(self.POST, (arguments)))
            if (max_workers != 0):
                for i in as_completed(tasks):
                    file_data = i.result()
                    params['dir'] = file_data[0]
                    self.GSFL(file_data[1],params.copy(),header,file_list,max_workers,fast_mode)
        except Exception as e:
            self.red("发生异常！\n"+str(file_data))
        return file_list
    def fast_mode_process(self,Args):
        """
        辅助创建线程池
        :param Args:
        :return:
        """
        return [self.save_share_file(Args[0]),Args[-1]]

    def save_mode(self,Args):
        """
        share储存模块（加速线程）
        :param Args[]: [root_path,file_list[dir]]
        :return:
        """
        start = 0
        for i in range(start, len(Args[1]), self.split_size):
            fsid = Args[1][i:i + self.split_size]
            args = [Args[0], None, {'list': fsid}]
            respones = self.save_share_file(args)
            if (respones['errno'] != 0):
                self.red("储存\t{0}\t下文件失败\t{1}".format(Args[0], respones))
                self.fail_save_file.put([Args[0], fsid])
            else:
                self.yellow("储存\t{0}\t下文件成功".format(Args[0]))
                if (self.log):
                    self.red(str(respones))
        return None
    def POST(self,arguments):
        respones = None
        do_post = True
        if self.log:
            self.green("{0}请求开始".format(self.use_time.qsize()))
            time.sleep(random.randint(1,3))
            self.use_time.put(1)
            print("arguments:",arguments)
        while do_post:
            try:
                arguments[1]['user-agent']=self.Get_User_Agent()
                respones = requests.post(arguments[0], headers=arguments[1], data=arguments[2])
                if(respones.status_code==200):
                    do_post = False
                else:
                    self.red("请求失败:服务器异常\t{0}".format(respones.status_code))
            except Exception as e:
                if(self.log):
                    self.red("请求发生异常：{0}".format(str(e)))
        if self.log:
            self.red("响应：")
            print(json.loads(respones.content.decode('utf-8')))
        if(arguments[-1]==0):
            return  [arguments[2]['dir'],json.loads(respones.content.decode('utf-8'))]
        else:
            return json.loads(respones.content.decode('utf-8'))

    def share_file_size(self,file_list):
        """
        :param file_list:获取文件总大小
        :return:
        """
        """
        :param file_list: 
        :return: 
        """
        Size = 0
        for i in file_list:
            for I in file_list[i]:
                Size+=int(I['size'])
        return Size

    def show_file(self,file_list):
        count_size = 0
        for i in file_list:
            self.red("路径：{0}".format(i))
            self.blue("文件数：{0}".format(len(file_list[i])))
            for I in file_list[i]:
                print(I['server_filename'],end='')
                self.red( '\t', self.convert_size(I['size']))
                count_size+=I['size']
            print()
        self.green("文件总大小：{0}".format(self.convert_size(count_size)))

    def check_free(self):
        """获取网盘容量
        :return: 结果例子：{"errno":0,"total":2204391964672,"request_id":5929092093134126170,"expire":null,"used":2203832252091}
        """
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] =  self.cookie
        page = requests.get('https://pan.baidu.com/api/quota?chckfree=1&checkexpire=1', headers=header).text
        return json.loads(page)

    def code(self,code):
        if(code==-21):
            return "分享的文件已经被取消"
        if (code ==12):
            return "文件存储失败"
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

    def search_file(self,file_name):
        """文件搜索

        :param file_name: 搜索的关键字
        :param cookie: 由get_cookie()函数转换chrome得到，或者通过浏览器抓包得到
        :return: 返回：file_list
        结果:[{'category': 6, 'unlist': 0, 'isdir': 1, 'oper_id': 1066838869, 'server_ctime': 1568999679, 'local_mtime': 1568999679, 'size': 0, 'server_filename': '\ufeff《死在文兰DeadInVinland》中文版nsp下载', 'share': 0, 'path': '/\ufeff《死在文兰DeadInVinland》中文版nsp下载', 'local_ctime': 1568999679, 'server_mtime': 1568999679, 'fs_id': 99524860442047}]
        """
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] = self.cookie
        url = 'https://pan.baidu.com/api/search?key={0}'.format(file_name)
        r = requests.get(url=url, headers=header).content.decode('utf-8')
        return json.loads(r)['list']


    def get_file_list(self, path="/"):
        """获取用户文件列表

        :param path: 获取文件路径
        :return: 返回None为失败
        """
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] = self.cookie
        params = {
            'dir':path
        }
        url = 'https://pan.baidu.com/api/list?'
        r = requests.get(url=url, headers=header,params=params).content.decode('utf-8')
        F = None
        try:
            F = json.loads(r)
        except:
            pass
        return F['list']

    def save_chrome_cookie(self,chrome_cookie):
        """保存Cookie到本地

        :param chrome_cookie: selenium产生的cookie
        :return: 返回bool类型值，true成功，false失败
        """
        try:
            with open('Cookie.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(chrome_cookie))
            return True
        except:
            return False


    def share_files(self, fid_list, pwd, days=7):
        """创建分享

        :param fid_list: 文件id列表
        :param pwd:  分享密码（4位不同的数字或字母）
        :param days: 外链有效期，0 永久、1 1天、7 7天，默认0
        :return: 响应
        """
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com'
        }
        header['cookie'] = self.cookie
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
    def save_share_file(self,args):
        """
        保存分享文件
        :param args: [path,fsid,file] 当fsid为None时会尝试从file中解析fs_id
        :return:
        """
        path = args[0]
        fsid = args[1]
        if(fsid==None):
            fsid = []
            for i in args[2]['list']:
                fsid.append(int(i['fs_id']))
        url = "https://pan.baidu.com/share/transfer?shareid={0}&from={1}&sekey={2}".format(self.share_id, self.uk,
                                                                                           self.sekey)
        header = {
            'User-Agent': self.Get_User_Agent(),
            'Referer': 'pan.baidu.com',
            'cookie': self.cookie
        }
        data = {
            'path': path,
            'fsidlist':json.dumps(fsid)
        }
        args = [url, header, data, 1]
        respones = self.POST(args)
        time.sleep(random.randint(1,3))
        return respones

    def save_share_normal(self,file_list,Create_folder = False):
        """
        分享文件的储存子程序
        :param file_list:
        :param Create_folder: 是否创建文件夹
        :return:
        """
        for i in tqdm(file_list,desc="正在转储文件"):
            if(Create_folder):
                path = self.create_folder(self.path+i)
            else:
                path = self.path+i
            fsid = []
            for I in file_list[i]['lsit']:
                fsid.append(I['fs_id'])
            for I in range(0,len(fsid),400):
                args = [path,fsid[I:I+400]]
                respones = self.save_share_file(args)
                if(respones['errno']!=0):
                    self.red("{0}\t文件存储出现问题:{1}".format(path,respones))
                    self.fail_save_file.append(path)
                else:
                    self.green("{0}\t文件转储成功！".format(path))


    def save_share(self,url,password=None,path='',fast_mode = True,max_workers= 5):
        """
        保存分享链接（注意：cookie必须包含BDCLND（当浏览器保存一次分享链接后会在cookie中出现））

        :param url:分享链接
        :param password:分享密码
        :param path:储存路径
        :param max_workers:多线程数
        :param fast_mode:是否启用多线程
        :return:返回响应码
        """
        self.fail_save_file = queue.Queue()
        file = self.verify_share(url, password)
        self.path = path
        if(file['errno']!=0):
            self.red("验证链接发生错误：{0}\t{1}".format(file['errno'],self.code(file['errno'])))
            if(self.log):
                self.red(str(file))
            return
        if(fast_mode):
            self.get_share_file_list(url,password,max_workers,file,fast_mode=fast_mode)
        else:
            file_list = self.get_share_file_list(url,password,max_workers,file,fast_mode=fast_mode,Create_folder=True)
            self.save_share_normal(file_list)
        if(self.fail_save_file.empty()):
            pass
        else:
            fail_save_file = []
            self.green("存在文件转储失败，启用单线程储存")
            while self.fail_save_file.empty() == False:
                fail_save_file.append(self.fail_save_file.get())
            for i in fail_save_file:
                Args = [i[0],i[-1]]
                self.save_mode(Args)
            if self.fail_save_file.empty():
                pass
            else:
                self.green("以下路径文件转储失败")
                while self.fail_save_file.empty() == False:
                    self.red(self.fail_save_file.get())
                return False
        self.green("成功转存文件！")
        return True

    def upload_file(self,file_path, upload_path, upload_size=1024*1024, max_workers=10):
        """
        文件上传接口
        :param file_path:需要上传的文件的本地
        :param upload_path: 文件上传的百度网盘储存路径
        :param upload_size:  文件切片大小单位byte
        :param max_workers: 文件切片上传线程
        :return: 返回服务器响应
        """
        respones = self.rapidupload(file_path,upload_path)
        if(respones['errno']==0):
            self.green("秒传成功！")
            return respones
        local_mtime = int(time.time())
        url = "https://pan.baidu.com/api/precreate?channel=chunlei&web=1&app_id=250528&clienttype=0&startLogTime={0}".format(
            local_mtime)
        data = "path={0}&autoinit=1&target_path=%2F&block_list=%5B%225910a591dd8fc18c32a8f3df4fdc1761%22%5D&local_mtime={1}".format(
            upload_path, local_mtime)
        header = {
            "referer": "https://pan.baidu.com/disk/home?",
            "cookie": self.cookie
        }
        arguments = [url, header, data.encode('utf-8'), 1]
        respones = self.POST(arguments)
        if respones['errno'] != 0:
            self.red("异常：{0}".format(respones))
            return
        uploadid = respones['uploadid']
        print(respones)
        Pool = ThreadPoolExecutor(max_workers=max_workers)
        partseq = 0
        file_size = os.path.getsize(file_path)
        file = open(file_path, 'rb')
        tasks = []
        block_list = []
        while True:
            pos = file.tell()
            if not file.read(upload_size):
                break
            arguments = [file_path, upload_path, uploadid, partseq, pos, upload_size]
            tasks.append(Pool.submit(self.upload_file_process, (arguments)))
            block_list.append("")
            partseq += 1
        file.close()
        T = tqdm(desc="正在上传", total=len(tasks))
        for i in as_completed(tasks):
            result = i.result()
            block_list[result[0]] = result[1]
            print(result)
            T.update(1)
        print(block_list,file_size,upload_path,uploadid)
        respones = self.upload_file_create(block_list,file_size,upload_path,uploadid)
        return respones

    def upload_file_create(self,block_list,file_size,upload_path,uploadid):
        """
        上传文件创建api
        :param block_list: 文件分片md5值
        :param file_size: 文件大小
        :param upload_path: 文件上传储存路径
        :param uploadid: 服务器返回
        :return: 返回服务器响应
        """
        header = {
            "cookie":self.cookie,
            "user-agent":self.Get_User_Agent(),
            "referer":"https://pan.baidu.com/disk/home?errno=0&errmsg=Auth%20Login%20Sucess&&bduss=&ssnerror=0&traceid="
        }
        url = "https://pan.baidu.com/api/create?isdir=0&rtype=1&channel=chunlei&web=1&app_id=250528&clienttype=0"
        data = {
            "path": upload_path,
            "size": file_size,
            "uploadid": uploadid,
            "target_path": "/",
            "block_list": json.dumps(block_list),
            "local_mtime": int(time.time())
        }
        data = urlencode(data)
        arguments = [url, header, data , 1]
        return self.POST(arguments)

    def upload_file_process(self,arguments):
        """
        文件分片上传线程
        :param arguments:
        :return:
        """
        with open(arguments[0], 'rb') as f:
            f.seek(arguments[4])
            data = f.read(arguments[5])
        file = {"file": ("blob", data, "application/octet-stream")}
        url = "https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2?method=upload&app_id=250528&channel=chunlei&clienttype=0&web=1&{0}&uploadid={1}&uploadsign=0&partseq={2}".format(
            urlencode({"path": arguments[1]}), arguments[2], arguments[3])
        header = {
            "user-agent":self.Get_User_Agent(),
            "cookie":self.cookie
        }
        while True:
            try:
                resopnes = requests.post(url, headers=header, files=file)
                if (resopnes.status_code == 200):
                    break
            except:
                print("上传异常\tseek:", arguments[4])
        return [arguments[3], json.loads(resopnes.content.decode('utf-8'))['md5']]

    def rapidupload(self,file_path,upload_path):
        """
        秒传接口
        :param file_path: 需要上传的文件的路径
        :param upload_path: 上传到百度网盘的绝对路径
        :return: 返回服务器响应信息
        """
        f = open(file_path,'rb')
        content = f.read(256*1024)
        slice_md5 = md5(content).hexdigest()
        f.seek(0)
        MD5 = md5()
        while True:
            content = f.read(4*1024*1024)
            if not content:
                break
            MD5.update(content)
        content_md5 = MD5.hexdigest()
        f.close()
        data="path={0}&content-length={1}&content-md5={2}&slice-md5={3}&target_path=\"/\"&local_mtime={4}".format(upload_path,os.path.getsize(file_path),content_md5,slice_md5,int(time.time()))
        url = "https://pan.baidu.com/api/rapidupload?rtype=1&channel=chunlei&web=1&app_id=250528&clienttype=0"
        header = {
            "referer":"https://pan.baidu.com/disk/home?",
            "cookie":self.cookie
        }
        arguments = [url,header,data.encode("utf-8"),1]
        respones = self.POST(arguments)
        return respones

# cookie = "BDUSS=Foa0pZU1lmUXk3bEk3T0xMMzZIZ3BweUsyNVlmSFFwbnAtVEU2RW1hUzA2MXRlRVFBQUFBJCQAAAAAAAAAAAEAAADrJoA4xOHEt8u5u~kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALReNF60XjReVm; STOKEN=3597c31d8f54182b6e3437fac4450afa3c5d3f57a117e953dcb6309c301d62a3; SCRC=04f14ad078bb9eb98b1d9aa076aa3a4c; BDCLND=T92OJa%2BEtLa6qCLrxb8dRLYBP97q0QEMuXO1d2qr7M8%3D; "
cookie = "STOKEN=5011c7a752dd45929ea789735389f7abefc720f1a4908e53d3ac1485270036b6;BDUSS=RqdH40MUp-cWJqelBQZlp4RUFyWjVYOGFqcUhZLTdXdXdwbjNZZU5JR0NnVnhlRVFBQUFBJCQAAAAAAAAAAAEAAABxRYqSZmtiNzg0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIL0NF6C9DReQ3;"
cookie = "STOKEN=31a4aed96253303006f947f388486090af1832ea0624169c111ae5b897224416;BDUSS=Jlcm5vZ3lkN0x1aXF5UDFiWWZhb2VOOGpOZjRHa0VJU2gtNGJjWm5mdE1hMk5lRUFBQUFBJCQAAAAAAAAAAAEAAABTR0i1yaPOw8zDzdMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEzeO15M3jteUT;"
A = BaiDuPan(cookie,bulid_chrome=True)
A.save_share('https://pan.baidu.com/s/1Bwm3lKu1kkZ6S0FJFpvU7w','27mj',max_workers=10)
input("继续")
file_list = A.get_share_file_list('https://pan.baidu.com/s/1Bwm3lKu1kkZ6S0FJFpvU7w','27mj',max_workers=10)
A.show_file(file_list)
input("继续")
respones = A.upload_file(r"D:\OptaneMemory.zip","/OptaneMemory.zip",upload_size=4*1024*1024)
input("继续")
A.close()
