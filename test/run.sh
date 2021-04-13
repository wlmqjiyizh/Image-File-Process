#!/bin/bash
# Shell脚本的Helloworld
# Created on 2021/04/10

echo "开始测试......"
python python1.py
wait
python python2.py
wait
python python3.py

int=1
while(( $int<=5 ))
do
    echo $int
    let "int++"
    python python1.py
    wait
done

echo "结束测试......"
