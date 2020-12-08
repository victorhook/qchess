############################################################
#
# Author         : Victor Krook
# Last edited    : 2020-12-08 22:27:16
# Github         : https://github.com/victorhook
# Contact        : https://mrhookv.com/contact
#
############################################################


import os
import re
from datetime import datetime


TEXT = {
    'Author': 'Victor Krook',
    'Last edited': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'Github': 'https://github.com/victorhook',
    'Contact': 'https://mrhookv.com/contact'
}

START_AND_END = '#' * 60
RE_OLD_TEXT = re.compile('{0}.*?{0}'.format(START_AND_END), flags=re.DOTALL)


def prettify(text):
    output = START_AND_END + '\n#\n'
    for key, val in text.items():
        output += '# %s: %s\n' % (key.ljust(15), val)

    output += '#\n' + START_AND_END + '\n\n\n'
    return output


def trim_old_text(data):
    old = RE_OLD_TEXT.search(data)
    if old:
        data = re.sub(old.group(0), '', data)
    return data


def decorate_file(base, filename):
    with open(os.path.join(base, filename), 'r+') as f:
        data = f.read()
        data = trim_old_text(data)
        f.seek(0)
        f.write(prettify(TEXT))
        f.write(data.lstrip())


def decorate(root):
    for path, _, files in os.walk(root):
        if files:
            for f in files:
                if f.endswith('.py'):
                    decorate_file(path, f)


if __name__ == "__main__":
    decorate('.')

