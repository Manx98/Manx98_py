from aiohttp import ClientSession
import ujson as json
import pymssql
import queue
import asyncio

class movie_douban:
    url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=time&page_limit=20&page_start=40"
    pramar = {

    }
    num = 100;
    json_data = queue.Queue()
    base_data = queue.Queue()
    full_info_url = queue.Queue()
    html_source = queue.Queue()
    full_info = queue.Queue()
    def __init__(int num = 100):
        pass
    
    def thread_builder(function):
        pass

    def get_json_data():
        pass

    def get_json_info():
        pass

    def get_html_source():
        pass
    
    def get_full_info():
        pass
    
    def DB_save():
        pass