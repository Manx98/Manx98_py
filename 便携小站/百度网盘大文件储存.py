from BaiDuPan import  BaiDuPan
Pan =  BaiDuPan(bulid_chrome=True)
Pan.load_cookie()
for i in Pan.load_url_list():
    try:
        path = Pan.create_folder("/"+i[0])
        if not Pan.save_share(url=i[1],password=i[2],path=path):
            Pan.delete_files(path)
    except:
        Pan.delete_files(path)
        print("ERROR:\t",i)
input("继续")
Pan.close()
