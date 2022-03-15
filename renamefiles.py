#To correct names that have ' in them because they caused errors in the other scripts

from os import listdir, rename
dirr='D:/Music'

def ren(dirr, intent=0):
    if not dirr: return None
    elif dirr[-1] != '/' and dirr[-1] != '//': dirr=dirr+'/'
    print(" "*4*intent+"READING "+dirr)
    for x in listdir(dirr):
        if len(x.split('.')) >= 2:
            print(" "*4*(intent+1)+"CHECKING "+x)
            if "'" in x.split('.')[0]:
                rename(dirr+x, dirr+x.replace("'", ""))
                x=x.replace("'", "")
                print(" "*4*(intent+1)+"RENAMED "+dirr+x)
    folders = [x for x in listdir(dirr) if len(x.split('.')) == 1]
    
    for x in folders:
        ren(dirr+x+'/', intent+1)

ren(dirr)
input("Complete ?")