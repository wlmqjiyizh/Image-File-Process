from glob import glob
from baseutils import *
import time
from PIL import Image
'''
将所有的png图片转换成jpg，输出到新文件夹
Created on 2021/04/11
'''

STATE_TXT_PATH = "state.txt"
TARGET_IMG_PATH = 'D:/dataset_副本/'
SOURCE_IMG_PATH = 'D:/dataset/'
index = -1


# 复制到哪了记个数
def add_state_in_txt():
    global index
    if index == -1:
        with open(STATE_TXT_PATH, "r") as file:
            index = file.readline()
        index = int(index)
    index = index + 1
    with open("state.txt", "w") as file:
        file.write(str(index))


time.sleep(30)
if index == -1:
    with open(STATE_TXT_PATH, "r") as file:
        index = file.readline()
    index = int(index)
glob(SOURCE_IMG_PATH + '/*')
for i, sub_path in enumerate(glob(SOURCE_IMG_PATH + '/*')):
    if i < index:
        print(get_time() + ' ' + sub_path + 'is' + str(i) + ', completed index=' + str(index) + 'Cur has been copied. Skip Now.')
        continue
    try:
        im = Image.open(sub_path)
        im.save(sub_path.replace('dataset', 'dataset_副本').replace('png', 'jpg'))
        im.close()
        add_state_in_txt()
        print(get_time() + ' ' + sub_path + "copy completed.")
    except Exception as e:
        print(get_time() + ' 本次处理图片失败:path=' + sub_path)
        print(e)

