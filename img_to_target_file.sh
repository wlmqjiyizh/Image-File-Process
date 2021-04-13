#!/bin/bash
# 循环执行 get_all_img_to_target_file.py
# Created on 2021/04/11
echo "开始脚本......"
int=1
while(( $int<=1000 ))
do
    echo $int
    let "int++"
    python get_all_img_to_target_file.py
    wait
done
echo "结束脚本......"