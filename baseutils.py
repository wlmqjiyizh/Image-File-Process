import time
'''
通用工具
Created by jiangyizhang on 2021/04/07
'''


# 获取当前时间
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())