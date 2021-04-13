from glob import glob
import os
import shutil
from PIL import Image
from baseutils import get_time
'''
将绘画合集中数据，放到统一的Target File Path中
Created by jiangyizhang on 2021/04/01
'''
ABSOLUTELY_INPUT_IMG_PATH = 'D:/JPG格式历代绘画合集14000幅 - 副本'  # 绝对路径
TARGET_IMG_PATH = 'D:/dataset/'
IMG_FORMATS = ['.jpg', 'jpeg', '.png', '.tif']
img_num = 0


def main():
    # 重置TARGET_IMG_PATH
    # if os.path.exists(os.path.join(TARGET_IMG_PATH)):
    #     shutil.rmtree(TARGET_IMG_PATH)
    # os.makedirs(TARGET_IMG_PATH)
    if not os.path.exists(os.path.join(TARGET_IMG_PATH)):
        os.makedirs(TARGET_IMG_PATH)
    # 遍历文件树
    __pre_order(ABSOLUTELY_INPUT_IMG_PATH)
    print('图片数量=' + str(img_num))


# 对文件树先序遍历
def __pre_order(path: str):
    sub_paths = glob(path + '/*')
    for index, sub_path in enumerate(sub_paths):
        if __is_file(sub_path):
            __pre_order(sub_path)
        elif __is_img(sub_path):
            try:
                __process_img(sub_path)
            except Exception as e:
                print(get_time() + ' 本次处理图片失败:path=' + sub_path)
                print(e)
        else:
            print(get_time() + sub_path + ' 解析出了问题')


# 遍历到图片，处理之
def __process_img(img_path: str):
    global img_num
    img_num = img_num + 1
    # 1.直接复制
    # shutil.copy(img_path, TARGET_IMG_PATH)
    # 2.jpg to png
    im = Image.open(img_path)
    # relative_jpg_img_path = img_path[img_path.rfind('\\') + 1:]
    relative_jpg_img_path = img_path.replace(ABSOLUTELY_INPUT_IMG_PATH + '\\', TARGET_IMG_PATH)
    relative_jpg_img_path = relative_jpg_img_path.replace('\\', '---')
    new_img_path = ''
    for format in IMG_FORMATS:
        if format in relative_jpg_img_path:
            new_img_path = relative_jpg_img_path.replace(format, '.png')
            break
    if new_img_path == '':
        im.close()
        return
    print(get_time() + ' 存第' + str(img_num) + '张 ' + new_img_path)
    im.save(new_img_path)
    im.close()
    # 删除之
    os.remove(img_path)
    print(get_time() + ' 删除：' + img_path)


# 路径是否是文件夹
def __is_file(str: str):
    return '.' not in str


# 路径是否是图片
def __is_img(str: str):
    for format in IMG_FORMATS:
        if format in str:
            return True
    return False


if __name__ == '__main__':
    import time
    time.sleep(30)  # 延时30s,再执行
    main()
