import os
import re

def module_installed(name, version_string=None):
    stream = os.popen('pip3 list')

    output = stream.read()
    output = str.split(output, '\n')
    tbl = {}
    for line in output:
        ppp = re.match('([^ ]*) *([^ ]*) *', line)
        if ppp:
            name = ppp[1]
            version = ppp[2]

            tbl[name] = version

    result = True

    if not name in tbl.keys():
        result = False

    elif version_string:
        result = version_string == tbl[name_ver[0]]

    return result

if True:
    print(module_installed('ufw'))
