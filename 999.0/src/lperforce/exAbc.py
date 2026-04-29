import sys


def exAbc(exPath=''):
    print('exAbc{exPath}')
    with open(exPath,'w') as f:
        pass

def exFbx(exPath='exPath'):
    pass


if __name__ == '__main__':
    print ("exAbc('{}')".format(sys.argv[2]))
    exec("exAbc('{}')".format(sys.argv[2]))