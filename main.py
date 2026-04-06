'''
Main file — copy from README and fill cookies locally; do not commit real cookies.
'''

from downloader import Downloader

settings = {
    # Manga urls, should be the same website
    'manga_url': [
        'https://www.bookwalker.com.tw/browserViewer/000000/read',
    ],
    # Your cookies (export from browser after login; keep local-only)
    'cookies': 'YOUR_COOKIES_HERE',
    # Folder names to store the Manga, the same order with manga_url
    'imgdir': [
        './downloads/example',
    ],
    # Resolution, (Width, Height), For coma this doesn't matter.
    'res': (1445, 2048),
    # Sleep time for each page (Second), normally no need to change.
    'sleep_time': 1,
    # Time wait for page loading (Second), if your network is good, you can reduce this parameter.
    'loading_wait_time': 20,
    # Cut image, (left, upper, right, lower) in pixel, None means do not cut the image. This often used to cut the edge.
    # Like (0, 0, 0, 3) means cut 3 pixel from bottom of the image.
    # or set dynamic to allow the scrypt to cut_images dynamictly (This work only correct if start_page is None)
    # this removed whitespace on the corners, initialised by the Cover.
    'cut_image': None,
    # File name prefix, if you want your file name like 'klk_v1_001.jpg', write 'klk_v1' here.
    'file_name_prefix': '',
    # File name digits count, if you want your file name like '001.jpg', write 3 here.
    'number_of_digits': 3,
    # Start page, if you want to download from 3 page, set this to 3, None means from 0
    'start_page': None,
    # End page, if you want to download until 10 page, set this to 10, None means until finished
    'end_page': None,
}

if __name__ == '__main__':
    downloader = Downloader(**settings)
    downloader.download()
