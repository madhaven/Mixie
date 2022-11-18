from os.path import isfile

def saveClass(lines):
    name = lines[0][6:lines[0].rfind(':')] + '.py'
    file = open(name, 'w')
    file.write(''.join(lines))
    file.close()

if False and isfile('Mixie.py'):
    print('Found Mixie in cwd')
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

mixieClassing = False
newClass = []
mixieContent = []
for line in mixie:
    if line[:6] == 'class ' and line[-2]==':':
        if line.rfind('(') == -1:
            className = line[6:line.rfind(':')]
            parents = None
        else:
            className = line[6:line.find('(')]
            parents = line[line.find('(')+1:line.find(')')]
            parents = parents.replace(' ', '').split(',')
        print('classFound:', className)
        if line[6:11] == 'Mixie':
            mixieClassing = True
        if mixieClassing:
            mixieContent.append(line)
        else:
            newClass.append(line)
    elif newClass:
        if line[:4] == '    ':
            if mixieClassing:
                mixieContent.append(line)
            else:
                newClass.append(line)
        else:
            mixieClassing = False
            saveClass(newClass)
            newclass = []
    else:
        mixieContent.append(line)