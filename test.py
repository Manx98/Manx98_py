#task的使用
import asyncio
from multiprocessing import Manager,Pipe
from threading import Condition,Semaphore
from concurrent .futures import wait,ThreadPoolExecutor,as_completed,FIRST_COMPLETED
A = ThreadPoolExecutor(max_workers=20)
for i in A.map(function_name,kwargs_list):
    print(i.result())
future = A.submit(function_name,(kwargs))
future.result()
future.done()
future.cancel()
task = [A.submit(function_name,(kwargs)) for i in range(20)]
wait(task,return_when=FIRST_COMPLETED)
for i in as_completed(task):
    print("result:",i.result())
A = Semaphore(20)
B = A.acquire()
B.release()
A = Condition()
A.acquire()
A.wait()
A.notify()
A.release()
async def hello(name):
    print('hello to :',name)
    return "BBBB"
#获取了一个协程对象
c = hello('bobo')
#创建一个事件循环对象
loop = asyncio.get_event_loop()
#就协程进行进一步的封装，封装到了task对象中
task = [loop.create_future(c) for i in range(100)]
print(task)
loop.run_until_complete(asyncio.wait(task) )
for i in task:
    print(i)