from image_label.xml_tool import *
import mmcv

'''
图片可视化操作
Created on 2021/04/11
'''


# 给出图片路径、xml文件路径、输出带有bbox的图片到out_path
def add_bboxs_to_img(img_path: str, xml_path: str, out_path: str):
    bboxs = get_bboxs_from_xml(xml_path)
    mmcv.imshow_bboxes(img_path, bboxs, show=False, out_file=out_path)