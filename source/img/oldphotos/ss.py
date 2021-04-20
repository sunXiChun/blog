#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
 
files = os.listdir('.')
for f in files:
    x = os.path.splitext(f)
    #判断jpg文件
    if x[1] == ".jpg":  
        #重命名
        name = x[0] + ".png"   
        os.rename(f,name)
