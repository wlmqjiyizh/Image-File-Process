import xml.etree.ElementTree as ET
import dataclasses
import numpy as np

'''
xml工具类
Created by jiangyizhang on 2021/04/09
'''


# labelImg工具生成的xml，其数据对应的Bean
@dataclasses.dataclass
class ImageBean:
    # 内部类：bounding box
    @dataclasses.dataclass
    class Object:
        @dataclasses.dataclass
        class Bndbox:
            x_min: int
            y_min: int
            x_max: int
            y_max: int

        name: str  # bbox的label
        bndbox: Bndbox  # bbox的坐标

    # 内部类：图片尺寸
    @dataclasses.dataclass
    class Size:
        width: int  # 宽
        height: int  # 长
        depth: int  # 深度

    # -------- xml里包含的字段 -------------------
    folder: str
    filename: str  # 相对路径
    path: str  # 绝对路径
    size: Size
    objects = []  # Object对象的list [object 1, object 2, ..., object n]

    # -------- 自己添加的字段 ---------------------
    num_of_bbox = 0  # bbox的个数


# 输入xml路径，返回ImageBean
def xml_to_image_bean(xml_path: str):
    xml_tree = ET.parse(xml_path)
    xml_root = xml_tree.getroot()

    folder = xml_root.find('folder').text
    filename = xml_root.find('filename').text
    path = xml_root.find('path').text
    xml_root_size = xml_root.find('size')
    width = int(xml_root_size.find('width').text)
    height = int(xml_root_size.find('height').text)
    depth = int(xml_root_size.find('depth').text)
    imageBean = ImageBean(folder=folder,
                          filename=filename,
                          path=path,
                          size=ImageBean.Size(
                              width=width,
                              height=height,
                              depth=depth))
    imageBean.objects = []
    for object in xml_root.findall('object'):
        name = object.find('name').text
        bndbox = object.find('bndbox')
        x_min = int(bndbox.find('xmin').text)
        y_min = int(bndbox.find('ymin').text)
        x_max = int(bndbox.find('xmax').text)
        y_max = int(bndbox.find('ymax').text)
        cur_object = ImageBean.Object(name=name,
                                      bndbox=ImageBean.Object.Bndbox(
                                          x_min=x_min,
                                          y_min=y_min,
                                          x_max=x_max,
                                          y_max=y_max
                                      ))
        imageBean.objects.append(cur_object)

    imageBean.num_of_bbox = len(imageBean.objects)
    return imageBean


# 给出image_bean，输出xml到save_path路径
def image_bean_to_xml(image_bean: ImageBean, save_path: str):
    annotation = ET.Element('annotation')

    folder = ET.SubElement(annotation, 'folder')
    folder.text = image_bean.folder

    file_name = ET.SubElement(annotation, 'filename')
    file_name.text = image_bean.filename

    path = ET.SubElement(annotation, 'path')
    path.text = image_bean.path

    size = ET.SubElement(annotation, 'size')
    width = ET.SubElement(size, 'width')
    width.text = str(image_bean.size.width)
    height = ET.SubElement(size, 'height')
    height.text = str(image_bean.size.height)
    depth = ET.SubElement(size, 'depth')
    depth.text = str(image_bean.size.depth)

    for bbox_object in image_bean.objects:
        object = ET.SubElement(annotation, 'object')
        object_name = ET.SubElement(object, 'name')
        object_name.text = bbox_object.name
        object_bndbox = ET.SubElement(object, 'bndbox')
        object_bndbox_x_min = ET.SubElement(object_bndbox, 'xmin')
        object_bndbox_x_min.text = str(bbox_object.bndbox.x_min)
        object_bndbox_y_min = ET.SubElement(object_bndbox, 'ymin')
        object_bndbox_y_min.text = str(bbox_object.bndbox.y_min)
        object_bndbox_x_max = ET.SubElement(object_bndbox, 'xmax')
        object_bndbox_x_max.text = str(bbox_object.bndbox.x_max)
        object_bndbox_y_max = ET.SubElement(object_bndbox, 'ymax')
        object_bndbox_y_max.text = str(bbox_object.bndbox.y_max)

    tree = ET.ElementTree(annotation)
    tree.write(save_path, encoding='utf-8')


def get_bboxs_from_xml(xml_path: str):
    image_bean = xml_to_image_bean(xml_path)
    bboxs = []
    for bbox_object in image_bean.objects:
        bbox = bbox_object.bndbox
        x_min, y_min, x_max, y_max = bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max
        bboxs.append([x_min, y_min, x_max, y_max])
    bboxs = np.asarray(bboxs)
    return bboxs