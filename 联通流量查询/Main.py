import requests
import  re
from bs4 import BeautifulSoup
import  time
import  os
from colorama import init
init(autoreset=True)
def green(text, T=False):
    """绿字
    :param text:
    :param T: 是否换行
    :return:
    """
    if (T):
        print("\033[1;32m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;32m{0}\033[0m".format(text))


def red( text, T=False):
    """红字

    :param text:
    :param T: 是否换行
    :return:
    """
    if (T):
        print("\033[1;31m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;31m{0}\033[0m".format(text))


def blue( text, T=False):
    """蓝字

    :param text:
    :param T: 是否换行
    :return:
    """
    if (T):
        print("\033[1;36m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;36m{0}\033[0m".format(text))


def yellow( text, T=False):
    """黄字

    :param text:
    :param T: 是否换行
    :return:
    """
    if (T):
        print("\033[1;33m{0}\033[0m".format(text), end="")
    else:
        print("\033[1;33m{0}\033[0m".format(text))

cookie = "MUT_S=android9; login_type=06; login_type=06; u_account=17684032131; city=085|789|90063345|-99; c_version=android@7.0200; d_deviceCode=869377036408377; random_login=0; cw_mutual=6ff66a046d4cb9a67af6f2af5f74c3211b96739ad07fbd8ba18ec72b80568c6d; c_mobile=17684032131; wo_family=0; u_areaCode=789; on_info=b7ebdc40ed1791ad2f844a90b2dc06c5; mobileServicecb=9cb8f2016f458baef33f2b68e6f7cfb0; mobileService1=j5skyvl8czBV6b6i-eWNoDwZRrtTdno69RTKMoeSRytMY6eCPCuM!740660488; logHostIP=null; route=2dc77cfc60930473fd85e0ebdbff03bc; dailyltroute=613b725948f9ce5c3effd7d75762779be0cf4b06; ecs_acc=dfU31Z8Pu11Tx/p3ZUdTdRUTEZk+Q1+Is8UvxnVJR/fS3xnTU3jjDi1CS5xM8jMk7HV1VXwfFrAC4ngYeNeiU992tg1SrDwBQE0dQjmJ9I5w+367pMklSriO60WRCvBcA1ztUR161L4ryX2MmFPf+tTIZlKDUEr/g6OBH/Xm/vk=; req_mobile=17684032131; req_serial=; req_wheel=ssss; logHostIP=null; c_sfbm=4g_1; dNG=408b2eee65c5e2ac8345f84109ee7eb9; u_account=17684032131; ecs_acc=MBBNhrjfoBEkPnFbyqwime3B+P4xeK8rwHQq8r/S81SO49YHt626CdKlU9E1qXA6BjiJFfITL9PSazXpE8y7UQ8iaruOKmrAety8qdH3FkFWytNe8uIgKIsizuE54i4HnlVii0xd6A7c7UEBWpCRE5QSgFIPB5W2afwdDn5xVKk=; a_token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1ODE3NzEyNDksInRva2VuIjp7ImxvZ2luVXNlciI6IjE3Njg0MDMyMTMxIiwicmFuZG9tU3RyIjoieWhlYTdhZTAxNTgxMTY2NDQ5In0sImlhdCI6MTU4MTE2NjQ0OX0.4V4YY4zuDDdy7PnoTcwPBoLk6T_EW-5n9ThRYoe8zDr90EyrWLB7TA1gDVCvOZwDZE6EVTrLjvWsQsGbxMqlmg; c_id=c3dd00bebdf39646d44a711385b47650222cf8f86d702a662632d2b36b7b1595; enc_acc=ppGSPgIToKmJiMGNqRN/lNC61af1SbFPqOAuC17CZ6PPjPH/t4Po0fECYuv5tnMDOzn1KvTm9X1jMOasEViIA2ZXIWOOXbhrpvZe+eZ0gq6LrHH/XQxT+Hr/HgRjVGOobuLKU34F0DOOMyOzN6Q+MIFT9uc4eyz1wWxUcio9yOw=; ecs_acc=ppGSPgIToKmJiMGNqRN/lNC61af1SbFPqOAuC17CZ6PPjPH/t4Po0fECYuv5tnMDOzn1KvTm9X1jMOasEViIA2ZXIWOOXbhrpvZe+eZ0gq6LrHH/XQxT+Hr/HgRjVGOobuLKU34F0DOOMyOzN6Q+MIFT9uc4eyz1wWxUcio9yOw=; t3_token=a3133962dc26a052917633e7b462169e; invalid_at=c3b28f82ef6fa01fbc4a1d89b004d6a3918868848827611a46766605cbd0039c; third_token=eyJkYXRhIjoiMTMyYzJlNGFmOTFiOWU0ZTRmMmMyMDQwOWVkNWU5NDI4MjI0ZmEzM2E5NDA3NzcyM2Y4ZDYzYzY4YTg5NTM0NmVlNjg3Mjg4OWZkYWQ0NDI2ZDc3ZGE4MjQ2OTFhYzlkMDcwZmI3ODI2M2MwNDY5MzRhODFiZGI4MDJmZTU1YzgwNzNjNTAwY2ZkYTRjODRlNDM2MTI5MGQ0NjI3N2Y4MiIsInZlcnNpb24iOiIwMCJ9; ecs_token=eyJkYXRhIjoiNWVjMzc1MzNjZDhiYmJhZTEwYWQ1NDMzYjIyNDJkODc2M2Q4ZWU2M2U4ZjAxYTk5OGEzNTQ2NDcwMDFmNzI3NDgwYWY0YjJhZTY5MDZjNjkwZmViYTY1N2U2ZTBkOGNiNGY1Yjk0NTE4OTg0ZjgwZGQ2YjIyOTI0Y2I4MmU5YjVhNzQ0ZmFhNjUxM2Y5OTRhMWM5NDkwMjVkZTUwNzRhODA2N2NmZWMwYTBiNWU1OTYyOWQ0MjU2ODcyYzgzODI0IiwidmVyc2lvbiI6IjAwIn0=; jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2JpbGUiOiIxNzY4NDAzMjEzMSIsInBybyI6IjA4NSIsImNpdHkiOiI3ODkiLCJpZCI6ImVmOWZhYmUxZDQzOGNkYzIwMzk2YTg2NmY4NmZlNzQ1In0.bpPf8yIkCa30l7bZFp1bG_BlDMJQ3yG4Wk8d2szmWik; c_sfbm=4g_1; route=751df16222283a79398e5c964ba647a1; clientid=98|0"
data = "menuId=000200020004"
url = "https://m.client.10010.com/mobileService/operationservice/queryOcsPackageFlowLeftContent.htm"
header = {
    "cookie":cookie,
    "user-agent":r"Mozilla/5.0 (Linux; Android 9; CLT-AL00 Build/HUAWEICLT-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.87 Mobile Safari/537.36; unicom{version:android@7.0200,desmobile:17684032131};devicetype{deviceBrand:HUAWEI,deviceModel:CLT-AL00};{yw_code:}"
}
RE = re.compile(r'[\t\r\n\t ]')
#wait_time = input("输入刷新时间：")
while True:
    red(time.ctime())
    try:
        text = requests.post(url,data=data,headers = header).text
    except:
        os.system('cls')
        continue
    BS = BeautifulSoup(text, 'lxml')
    TotleData = [RE.sub('', i.text) for i in BS.find_all(class_="TotleData")]
    key = [RE.sub('', i.text) for i in BS.find_all(class_="fz")]
    infopackage = [RE.sub('', i.text) for i in BS.find_all(class_="infopackage5")]
    total = [RE.sub('', i.text) for i in BS.find_all(class_="fy wz_22")]
    lastData = [RE.sub('', i.text) for i in BS.find_all(class_="lastData")]
    infopackage = [i for i in infopackage if (len(re.findall('共', i)) == 0)]
    for i in range(len(key)):
        green(key[i]+":",True)
        red(total[i])
    for i in range(len(infopackage)):
        green(infopackage[i]+":",True)
        yellow(TotleData[i]+'\t',True)
        red(lastData[i])
    input("继续:")
    os.system('cls')