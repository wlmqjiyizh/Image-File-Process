#!/bin/bash

# 循环执行png to jpg程序
# Created by 2021/04/11
echo "开始脚本......"
int=1
while(( $int<=1000 ))
do
    echo $int
    let "int++"
    python all_img_png_to_jpg.py
    wait
done
echo "结束脚本......"