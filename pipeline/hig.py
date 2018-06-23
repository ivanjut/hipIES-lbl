# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/hig.py
# Compiled at: 2015-07-17 13:23:47


def load(path):
    with open(path) as (f):
        content = f.read()
    return hig(d)


def parsetodict(content):
    """
    :type content: str
    :param content:
    :return:
    """
    if '=' in content:
        content.partition('=')


def dict2str(d, depth=0):
    content = ''
    for key in d:
        if type(d[key]) is dict:
            content += (u'{0}{1} = {{\n').format(u'\t' * depth, str(key))
            content += dict2str(d[key], depth + 1)
            content = content[:-1] + (u'\n{0}}},\n').format(u'\t' * depth)
        elif type(d[key]) is tuple:
            content += (u'{0}{1} = {2},\n').format(u'\t' * depth, key, '[ ' + (' ').join(map(str, d[key])) + ' ]')
        elif type(d[key]) is list:
            content += (u'{0}{1} = {2},\n').format(u'\t' * depth, key, '[ ' + (' ').join(map(str, d[key])) + ' ]')
        elif type(d[key]) is unicode:
            content += (u'{0}{1} = "{2}",\n').format(u'\t' * depth, key, str(d[key]))
        elif type(d[key]) is str:
            content += (u'{0}{1} = "{2}",\n').format(u'\t' * depth, key, str(d[key]))
        else:
            content += (u'{0}{1} = {2},\n').format(u'\t' * depth, key, str(d[key]))

    content = content[:-2] + u'\n'
    return content


class hig:

    def __init__(self, **d):
        self.__dict__.update(d)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return

    def __str__(self):
        return dict2str(self.__dict__)

    def write(self, path):
        with open(path, 'w') as (f):
            f.write(str(self))


if __name__ == '__main__':
    d = {'hipRMCInput': {'instrumentation': {'inputimage': 'data/mysphere.tif', 'imagesize': [512, 512], 'numtiles': 1, 
                                           'loadingfactors': [
                                                            0.111]}, 
                       'computation': {'runname': 'test', 'modelstartsize': [
                                                        32, 32], 
                                       'numstepsfactor': 1000, 
                                       'scalefactor': 32}}}
    h = hig(**d)
    print h
# okay decompiling hig.pyc
