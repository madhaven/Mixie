#To read the comments in my music folder

from staggerstuff import *

dirr = 'D:\\Music\\' 

for filename in fetchfiles(dirr):
    if filename[-3:]=='mp4' or 'desktop.ini' in filename: continue
    try:
        file = read_tag(filename)
        print(file.comment, filename.split('\\')[len(filename.split('\\'))-1])
    except Exception as e: input(str(e)+' : '+filename)
        
input("Complete ?")