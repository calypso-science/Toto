import sys,os
import glob

root='D:\\wherry'
folderout='D:\data\\raw'

all_folder=glob.glob(os.path.join(root,'*'))
print(all_folder)