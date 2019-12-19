import requests
import json

def bulid_div(image,url,title):
    return '<div class="vid"><a href="{0}" target="_blank"><img class="SS" src="{1}"/></a><p>{2}</p></div>\n'.format(url,image,title)
def bulid_html(data):
    a = """<!doctype html><html><head><meta charset="utf-8"><style>*{padding: 0px;margin: 0px;}.vid{margin: 0% 0% 20% 10%;float: left;text-align: center;}.SS{width: 400px; height:400px}p{font-size: 15px;}</style></head><body>"""
    b = """</body></html>"""
    return a+data+b
url="http://www.andi007.top//api/getVideoList"
header={
"user-agent":"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0"
}
data={
'pagesize':20,
'page':1,
'cid':18,
'token':'b8dw2r549u758jau254aaf9405bd35d2',
'_t':1573840763848,
'agent_id':2
}
D = "";
for i in range(13,14):
    data['cid']=i
    for i in range(1,8):
            try:
                i = requests.post(data=data,url=url,headers=header).text
                r=json.loads(i)
                for i in r['info']:
                    try:
                        D+=bulid_div(i['img'],i['video'],i['title'])
                    except:
                        print(i)
            except:
                print(i)
S = bulid_html(D)
with open(r'C:\Users\Shinelon\Desktop\try.html','w',encoding='utf-8') as f:
    f.write(S)