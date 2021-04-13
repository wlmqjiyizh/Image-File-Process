import os
from image_label.vis_tool import *

'''
图片切分。一张大图切成若干小图
Created on 2021/04/11
'''


# 一张大图切成若干张小图. 切割过程中会避开bboxs
def cut_image(img_path: str,
              xml_path: str,
              max_long=1000,
              max_short=600,
              save_img_with_bboxs=False,
              output_folder='data'):
    '''
    过程中会输出小图及对应的xml到output_folder文件夹下
    :param img_path: 大图路径
    :param xml_path: 大图对应的labelimg标注的xml文件的路径
    :param max_long: 给定的小图最大宽度
    :param max_short: 给定的小图最大高度
    :param save_img_with_bboxs: if True,输出含bboxs的小图
    :param output_folder: 输出小图及xml的文件夹.如果路径下没有会自动创建
    '''
    img = mmcv.imread(img_path)
    width, height = (img.shape)[1], (img.shape)[0]
    bboxs = get_bboxs_from_xml(xml_path)
    bboxs = bboxs.tolist()
    # 矩阵,形如img,标识每一个像素是否在bboxs内。 例:img_pixel_state[i][j]=False,表示img[i][j]这个像素在bboxs内
    img_pixel_state = [[True for _ in range(height + 1)] for _ in range(width + 1)]
    for bbox in bboxs:
        x_min, y_min, x_max, y_max = bbox[0], bbox[1], bbox[2], bbox[3]
        for x_index in range(x_min, x_max + 1):
            for y_index in range(y_min, y_max + 1):
                img_pixel_state[x_index][y_index] = False

    # 先计算x（竖）的分割线
    x_seg_lines = [0]
    while x_seg_lines[-1] < width:
        x_try_seg_line = x_seg_lines[-1] + max_long - 1
        if x_try_seg_line >= width:
            x_try_seg_line = width
        diff = 1
        # 画的线有可能穿过bboxs，缩小宽度使线不穿过bboxs
        x_seg_line = x_try_seg_line
        while True:
            can_be_seg_line = True
            for y_index in range(height + 1):
                if not img_pixel_state[x_seg_line][y_index]:
                    can_be_seg_line = False
                    break
            if can_be_seg_line:
                break
            x_seg_line = x_try_seg_line - diff
            diff = diff + 1
        x_seg_lines.append(x_seg_line)
    # 对每一个竖的分割区间，再去切横着的区间
    # list of subimg's [x_min, y_min, x_max, y_max]
    sub_imgs = []  # [[x_min, y_min, x_max, y_max]
    for i in range(len(x_seg_lines) - 1):
        cur_x_interval = [x_seg_lines[i], x_seg_lines[i + 1]]
        cur_y_seg_lines = [0]
        while cur_y_seg_lines[-1] < height:
            y_try_seg_line = cur_y_seg_lines[-1] + max_short - 1
            if y_try_seg_line >= height:
                y_try_seg_line = height
            diff = 1
            y_seg_line = y_try_seg_line
            while True:
                can_be_seg_line = True
                for x_index in range(cur_x_interval[0], cur_x_interval[1] + 1):
                    if not img_pixel_state[x_index][y_seg_line]:
                        can_be_seg_line = False
                        break
                if can_be_seg_line:
                    break
                y_seg_line = y_try_seg_line - diff
                diff = diff + 1
            cur_y_seg_lines.append(y_seg_line)
        # 得到横的区间。将子图[x_min, y_min, x_max, y_max]加入sub_imgs
        for index in range(len(cur_y_seg_lines) - 1):
            cur_y_interval = [cur_y_seg_lines[index], cur_y_seg_lines[index + 1]]
            cur_img = [cur_x_interval[0], cur_y_interval[0], cur_x_interval[1], cur_y_interval[1]]
            sub_imgs.append(cur_img)

    # 切出每个子图
    patches = mmcv.imcrop(img, np.asarray(sub_imgs))
    image_beans = []
    # 对于每个子图，得到ImageBean
    for sub_img in sub_imgs:
        sub_img_x_min, sub_img_y_min, sub_img_x_max, sub_img_y_max = sub_img[0], sub_img[1], sub_img[2], sub_img[3]
        # 得到在子图里的bboxs
        bboxs_in_cur_sub_img = []
        for bbox in bboxs:
            bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max = bbox[0], bbox[1], bbox[2], bbox[3]
            if sub_img_x_min < bbox_x_min and sub_img_y_min < bbox_y_min and sub_img_x_max > bbox_x_max and sub_img_y_max > bbox_y_max:
                new_bbox_for_sub_img = [bbox_x_min - sub_img_x_min, bbox_y_min - sub_img_y_min,
                                        bbox_x_max - sub_img_x_min, bbox_y_max - sub_img_y_min]
                bboxs_in_cur_sub_img.append(new_bbox_for_sub_img)
        # 对于每个子图，创建一个ImageBean
        image_bean = ImageBean(folder='',
                               filename='',
                               path='',
                               size=ImageBean.Size(
                                   width=sub_img_x_max - sub_img_x_min + 1,
                                   height=sub_img_y_max - sub_img_y_min + 1,
                                   depth=3
                               ))
        image_bean.objects = []
        # 子图的各bbox更新入ImageBean
        for sub_bbox in bboxs_in_cur_sub_img:
            cur_object_for_image_bean = ImageBean.Object(name='1',
                                                         bndbox=ImageBean.Object.Bndbox(
                                                             x_min=sub_bbox[0],
                                                             y_min=sub_bbox[1],
                                                             x_max=sub_bbox[2],
                                                             y_max=sub_bbox[3]
                                                         ))
            image_bean.objects.append(cur_object_for_image_bean)
        image_beans.append(image_bean)

    # 将子图及其新的xml，存入/data/目录下
    if not os.path.exists(os.path.join(output_folder)):
        os.makedirs(output_folder)
    for i in range(len(patches)):
        patch = patches[i]
        new_img_path = output_folder + '/' + img_path.replace('.jpg', '_patch' + str(i + 1) + '.jpg')
        xml_path = new_img_path.replace('.jpg', '.xml')
        cur_image_bean = image_beans[i]
        absolute_path = os.path.split(os.path.realpath(__file__))[0]
        cur_image_bean.folder = output_folder
        cur_image_bean.filename = new_img_path
        cur_image_bean.path = absolute_path + '\\' + new_img_path
        # 存子图
        mmcv.imwrite(patch, new_img_path)
        # 存xml
        image_bean_to_xml(cur_image_bean, xml_path)
        if save_img_with_bboxs:
            # 测试(optional)
            add_bboxs_to_img(new_img_path, xml_path, new_img_path.replace('.jpg', '_with_bboxs.jpg'))


# def find_abandon_interval

if __name__ == '__main__':
    cut_image('img_demo.jpg', 'img_demo_labels.xml')
