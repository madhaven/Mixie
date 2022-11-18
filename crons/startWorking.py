# script to convert singular Mixie file to a workable model
from os.path import isfile
LOGGING = False # Turning on logging will output logs
def log(wait=False, *args, **kwargs):
    if LOGGING:
        print(*args, **kwargs)
        if wait:
            input()

def saveClass(lines, parents:list=[], name=None, imports=[]):
    log('\nsaving class', className)
    name = name+'.py' if name else lines[0][6:lines[0].rfind(':')] + '.py'
    file = open(name, 'w')
    for imp in imports:
        file.write(imp)
    for parent in parents:
        file.write('from %s import *\n\n'%parent)
    file.write(''.join(lines))
    file.close()

if isfile('Mixie.py'):
    log('Found Mixie in cwd')
    loc = ''
else:
    print(
        'The Mixie.py file was not found.',
        'The script will SEPERATE classes in file to the same location',
        'Drop Mixie.py here: ',
        sep='\n', end='')
    loc = input().removesuffix('Mixie.py')
file = open(loc + 'Mixie.py', 'r')
mixie = file.readlines()
file.close()

className = ''
allClasses = []
newClass = []
parents = []
mixieContent = []
allImports = []

for line in mixie:
    log(line, end='')
    if line[:6] == 'import' or line[:4] == 'from':
        allImports.append(line)
    if line[:6] == 'class ' and line[-2]==':':
        if newClass:
            saveClass(newClass, parents=parents, name=className, imports=allImports)
            parents = []
            newClass = []
            className = ''
        if line.rfind('(') == -1:
            className = line[6:line.rfind(':')]
            parents = []
        else:
            className = line[6:line.find('(')]
            parents = line[line.find('(')+1:line.find(')')]
            parents = parents.replace(' ', '').split(',')
        log('\nclass:', className, ':' if parents else '', *parents)
        if className == 'Mixie':
            mixieContent.append(line)
        else:
            newClass.append(line)
            allClasses.append(className)
    elif newClass:
        if line[:4] in {'    ', '\n'}:
            newClass.append(line)
        else:
            saveClass(newClass, parents=parents, name=className, imports=allImports)
            parents = []
            newClass = []
            className = ''
    else:
        mixieContent.append(line)

mixieImports = {
    'from %s import *\n'%x for x in allClasses
}
saveClass(mixieContent, name='Mixie', imports=mixieImports)
print('Convert completed.\nReady to Code')