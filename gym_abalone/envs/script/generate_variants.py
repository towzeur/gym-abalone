import urllib.request as urllib2
from bs4 import BeautifulSoup
import PIL
import glob
from PIL import Image
import numpy as np
import json
import os

url = "https://abaloneonline.wordpress.com/tag/starting-positions/"


def download_image(pic_name, pic_url):

    with open(pic_name, 'wb') as f:
        r = urllib2.urlopen(pic_url)
        if r.status == 200:
            f.write(r.read())

def download():
    req = urllib2.urlopen(url)
    if req.status == 200:
    
        soup = BeautifulSoup(req, "lxml")
        imgs = soup.find('div', {'class':'entry-content'}).find_all('a')
        for img in imgs:
            pic_url = img['href']
            pic_name = f"80/{pic_url.split('/')[-1]}"

            print(pic_name)
            download_image(pic_name, pic_url)


def mse(pixel0, pixel1):
    return sum((p0-p1)**2 for p0, p1 in zip(pixel0, pixel1)) / len(pixel0) 


def detect_pixel(pixel):
    '''
    find the closest between 
        ''  : void  : (170, 146, 102)
        'w' : white : (210, 210, 210)
        'b' : black : ( 68,  68,  68)
    '''
    colors = [(170,146,102), (210,210,210), (68,68,68)]
    p_color = ['_', 'w', 'b']

    i_min = np.argmin([mse(pixel, c) for c in colors])
    return p_color[i_min]


def repr_board(out):
    '''
    #     _ _ _ _ _
    #    w w w w w w
    #   w b w _ _ _ w
    #  _ w w _ _ w w _
    # _ _ _ _ _ _ _ _ _
    #  _ b b _ _ b b _
    #   b _ _ _ b w b
    #    b b b b b b
    #     _ _ _ _ _
    '''

    tmp = [5, 6, 7, 8, 9, 8, 7, 6, 5]
    print(sum(tmp))
    i = 0
    j = 0
    for x in out:
        if i==0:
            print(' '*(9-tmp[j]), end='')
        print(x, end=' ')
        if i < tmp[j]-1:
            i += 1
        else:
            i = 0
            j += 1
            print()
    print()

def process():

    # find all the positions from red pixel in the test image 
    data = np.array(Image.open('80/_test.png'))
    pos = []
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            r, g, b = data[row, col, :3]
            if (r, g, b) == (255, 0, 0):
                pos.append((row, col))


    configs = {}
    images = glob.glob('80/*')
    for image_id, image in enumerate(images):
        print(image)
    
        base =  os.path.basename(image)
        name = os.path.splitext(base)[0]
        data = np.array(Image.open(image))

        config = {
            'id' : image_id,
            'board_nb' : 61,
            'players' : 2,
            'players_sets': [[] for i in range(2)]
        }

        out = []
        for i, (row, col) in enumerate(pos):
            r, g, b = data[row, col, :3]
            value = detect_pixel((r,g,b))
            if value !=  '_':
                config['players_sets'][{'b':0, 'w':1}[value]].append(i)
            out.append(value)


        if len(config['players_sets'][0]) != len(config['players_sets'][1]):
            repr_board(out)

        configs[name] = config

    # Writing JSON data
    with open('../assets/variants.json', 'w') as f:
        json.dump(configs, f, indent=2)

if __name__ == '__main__':

     process()
