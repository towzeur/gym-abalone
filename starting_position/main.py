import urllib.request as urllib2
from bs4 import BeautifulSoup

url = "https://abaloneonline.wordpress.com/tag/starting-positions/"


def download_image(pic_name, pic_url):

    with open(pic_name, 'wb') as f:
        r = urllib2.urlopen(pic_url)
        if r.status == 200:
            f.write(r.read())

def main():
    req = urllib2.urlopen(url)
    if req.status == 200:
    
        soup = BeautifulSoup(req, "lxml")
        imgs = soup.find('div', {'class':'entry-content'}).find_all('a')
        for img in imgs:
            pic_url = img['href']
            pic_name = f"80/{pic_url.split('/')[-1]}"

            print(pic_name)
            download_image(pic_name, pic_url)

if __name__ == '__main__':

    main()
