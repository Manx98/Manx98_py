#三国演义 人物统计
# import jieba
# def comm(name):
#     if(name=="玄德" or name == "玄德曰"):
#         return "刘备"
#     elif(name=="孔明曰"or name=="孔明" or name=="诸葛亮"):
#         return "孔明"
#     elif(name=="关公"or name=="云长"):
#         return "关公"
#     elif(name=="孟德" or name=="丞相"):
#         return "曹操"
#     else:
#         return name
# text = open("threekingdoms.txt","r",encoding="gb18030").read()
# words = jieba.lcut(text)
# count = {}
# excult = {"将军","却说","二人","不可","荆州","不能","如此","商议","如何","主公","军士","次日","大喜","天下","引兵","军马","于是","今日","左右"}
# for i in words:
#     i = comm(i)
#     if(len(i)<=1 or i in excult):
#         continue
#     elif(i in count):
#         count[i]+=1
#     else:
#         count[i]=1
# items = list(count.items())
# items.sort(key = lambda x:x[1],reverse=True)
# for i in range(20):
#     name,counts = items[i]
#     print("{0:<10}{1:>10}".format(name,counts))
#请在...补充一行或多行代码
#CalStatisticsV1.py


#hamet
# HametTxt = open("hamet.txt","r").read()
# HametTxt = HametTxt.lower()
# for i in "~!@#$%^&*()_+-=:;,./?><\\'\"":
#     HametTxt.replace(i," ")
# words = HametTxt.split(' ')
# counts = {}
# for i in words:
#     if(len(i)<=1):
#         continue
#     elif(i in counts):
#         counts[i]+=1
#     else:
#         counts[i]=1
# items = list(counts.items())
# items.sort(key = lambda x:x[1],reverse=True)
# for i in range(10):
#     word ,count = items[i]
#     print("{0:<10}{1:>10}次".format(word,count))


# import jieba
# txt = open('沉默的羔羊.txt', 'r', encoding='utf-8').read()
# words = jieba.lcut(txt)
# counts = {}
# for i in words:
#     if(len(i)<=1):
#         continue
#     elif(i in counts):
#         counts[i]+=1
#     else:
#         counts[i]=1
# items=list(counts.items())
# items.sort(key = lambda x:x[1],reverse=True)
# print(items[0][0])
"""
import jieba
import wordcloud
from scipy.misc import imread
map = imread("map.png")
w = wordcloud.WordCloud(font_path="msyh.ttc",width=800,height=800)
txt = open("沉默的羔羊.txt","r",encoding="utf-8").read()
words = jieba.lcut(txt)
print(words)
w.generate(" ".join(words))
w.to_file("mn.png")
"""
from tqdm import tqdm
import time
import os
with tqdm(total=100) as pbar:
    for i in range(20):
        time.sleep(1)
        pbar.update(1)