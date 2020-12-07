from PIL import Image

path = '/home/victor/coding/projects/qchess/qchess_web/static/images/'

img = Image.open(path + 'img.png')
x, y = 0, 0
SIZE = 135
pad = 21

for i in range(12):
    if i % 6 == 0 and i != 0:
        y += SIZE
        x = 0

    img2 = img.crop((x, y, x+SIZE, y+SIZE))
    x += pad + SIZE
    img2.save('%s/pieces/_%s.png' % (path, i))



