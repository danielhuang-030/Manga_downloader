'''
Main downloader, XU Zhengyi, 2020/05/05
'''
import base64
import logging
import os
import random
import re
import subprocess
import time
from io import BytesIO
from PIL import ImageOps

import PIL.Image as pil_image
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait

# DO NOT REMOVE THIS LINE. Used for __subclasses__()
from website_actions import *
from website_actions.abstract_website_actions import WebsiteActions

logging.basicConfig(format='[%(levelname)s](%(name)s) %(asctime)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


def detect_chrome_major_version():
    """
    Chrome major version for undetected_chromedriver's version_main.

    When omitted, uc may fetch a driver for the newest Chrome while apt's
    google-chrome-stable is one major behind (e.g. driver 147 vs browser 146),
    causing SessionNotCreatedException.
    """
    for binary in (
        'google-chrome-stable',
        'google-chrome',
        'chromium',
        'chromium-browser',
    ):
        try:
            out = subprocess.check_output(
                [binary, '--version'],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=15,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
        m = re.search(r'(\d+)\.', out)
        if m:
            major = int(m.group(1))
            logging.info('Detected Chrome major version %s (%s)', major, binary)
            return major

    logging.warning(
        'Could not detect Chrome major version (no chrome/chromium in PATH). '
        'If WebDriver fails with a version mismatch, set uc.Chrome(version_main=...).'
    )
    return None


def get_cookie_dict(cookies):
    cookies_split = cookies.split('; ')
    if len(cookies_split) == 1:
        cookies_split = cookies.split(';')
    cookies_dict = {}
    for i in cookies_split:
        if i == '':
            continue
        kv = i.split('=')
        cookies_dict[kv[0]] = '='.join(kv[1:])
    return cookies_dict


def add_cookies(driver, cookies, domain=None, path='/'):
    """
    Inject cookies on the current page. For Bookwalker TW, pass domain='.bookwalker.com.tw'
    so session cookies are visible on pcreader.bookwalker.com.tw (not only www).
    """
    for i in cookies:
        payload = {'name': i, 'value': cookies[i], 'path': path}
        if domain:
            payload['domain'] = domain
        driver.add_cookie(payload)


class Downloader:
    '''
    Main download class
    '''

    def __init__(
            self, manga_url, cookies, imgdir, res, sleep_time=2, loading_wait_time=20,
            cut_image=None, file_name_prefix='', number_of_digits=3, start_page=None,
            end_page=None
    ):
        self.manga_url = manga_url
        self.cookies = get_cookie_dict(cookies)
        self.imgdir = imgdir
        self.res = res
        self.sleep_time = sleep_time
        self.loading_wait_time = loading_wait_time
        self.cut_image = cut_image
        self.file_name_model = '/'
        if len(file_name_prefix) != 0:
            self.file_name_model += file_name_prefix + '_'

        self.file_name_model += '%%0%dd.png' % number_of_digits
        self.start_page = start_page - 1 if start_page and start_page > 0 else 0
        self.end_page = end_page
        self.image_box = None

        self.init_function()

    def check_implementation(self, this_manga_url):
        is_implemented_website = False
        for temp_actions_class in WebsiteActions.__subclasses__():
            if temp_actions_class.check_url(this_manga_url):
                is_implemented_website = True
                self.actions_class = temp_actions_class()
                logging.info('Find action class, use %s class.',
                             self.actions_class.get_class_name())
                break

        if not is_implemented_website:
            logging.error('This website has not been added...')
            raise NotImplementedError

    def str_to_data_uri(self, str):
        return ("data:text/plain;charset=utf-8;base64,%s" %
                base64.b64encode(bytes(str, 'utf-8')).decode('ascii'))

    def get_driver(self):
        option = uc.ChromeOptions()
        option.set_capability('unhandledPromptBehavior', 'accept')
        option.add_argument('--high-dpi-support=1')
        option.add_argument('--device-scale-factor=1')
        option.add_argument('--force-device-scale-factor=1')
        chrome_major = detect_chrome_major_version()
        # Align UA major with installed Chrome; mismatches (e.g. UA 122 vs browser 146) may break reader JS.
        ua_major = chrome_major if chrome_major is not None else 122
        option.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/%d.0.0.0 Safari/537.36' % ua_major
        )
        option.add_argument("--app=%s" % self.str_to_data_uri('Manga_downloader'))
        # Classic --headless is easy to fingerprint; Chrome 109+ supports --headless=new (closer to real).
        headless_env = os.environ.get('MANGA_HEADLESS', 'new').strip().lower()
        if headless_env in ('0', 'false', 'no', 'off'):
            logging.info('Headless disabled (MANGA_HEADLESS=%s); requires a display (e.g. local, or xvfb).', headless_env)
        elif headless_env == 'old':
            option.add_argument('--headless')
            logging.info('Using legacy --headless (MANGA_HEADLESS=old)')
        else:
            option.add_argument('--headless=new')
            logging.info('Using --headless=new (set MANGA_HEADLESS=old or 0 to change)')
        # Docker / Linux: default /dev/shm is tiny; Chrome tab crashes without these.
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--disable-gpu')
        if chrome_major is not None:
            self.driver = uc.Chrome(options=option, version_main=chrome_major)
        else:
            self.driver = uc.Chrome(options=option)
        self.driver.set_window_size(self.res[0], self.res[1])
        viewport_dimensions = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
        logging.info('Viewport dimensions %s', viewport_dimensions)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
              Object.defineProperty(navigator, 'webdriver', {
                get: () => false
              })
              window.navigator.chrome = undefined;
              Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
              });
              Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
              });
              const originalQuery = window.navigator.permissions.query;
              window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
              );
            """
        })

    def init_function(self):
        if self.cut_image is not None and self.cut_image != 'dynamic':
            self.left, self.upper, self.right, self.lower = self.cut_image
        self.get_driver()
        random.seed()

    def login(self):
        logging.info('Login...')
        driver = self.driver
        driver.get(self.actions_class.login_url)
        driver.delete_all_cookies()
        cookie_domain = getattr(self.actions_class, 'cookie_domain', None)
        if cookie_domain:
            logging.info(
                'Using cookie domain %s (reader may load on another subdomain).',
                cookie_domain,
            )
        add_cookies(driver, self.cookies, domain=cookie_domain)
        logging.info('Login finished...')

    def prepare_download(self, this_image_dir, this_manga_url):
        if not os.path.isdir(this_image_dir):
            os.mkdir(this_image_dir)
        logging.info('Loading Book page...')
        driver = self.driver
        driver.get(this_manga_url)
        logging.info('Book page Loaded...')
        logging.info('Preparing for downloading...')
        time.sleep(self.loading_wait_time)

    def download_book(self, this_image_dir):
        driver = self.driver
        logging.info('Run before downloading...')
        self.actions_class.before_download(driver)
        logging.info('Start download...')
        try:
            page_count = self.actions_class.get_sum_page_count(driver)
            logging.info('Has %d pages.', page_count)
            end_page = page_count
            if self.end_page and self.end_page <= page_count:
                end_page = self.end_page
            self.actions_class.move_to_page(driver, self.start_page)

            time.sleep(self.sleep_time)

            for i in range(self.start_page, end_page):
                self.actions_class.wait_loading(driver)
                image_data = self.actions_class.get_imgdata(driver, i + 1)
                with open(this_image_dir + self.file_name_model % i, 'wb') as img_file:
                    if self.cut_image is None:
                        img_file.write(image_data)
                    elif self.cut_image == "dynamic":
                        org_img = pil_image.open(BytesIO(image_data))
                        if self.image_box is None:
                            org_img.load()
                            invert_im = org_img.convert("RGB")
                            invert_im = ImageOps.invert(invert_im)
                            self.image_box = invert_im.getbbox()
                        org_img.crop(self.image_box).save(img_file, format='PNG')
                    else:
                        org_img = pil_image.open(BytesIO(image_data))
                        width, height = org_img.size
                        org_img.crop(
                            (self.left, self.upper, width - self.right, height - self.lower)).save(img_file, format='PNG')

                logging.info('Page %d Downloaded', i + 1)
                if i == page_count - 1:
                    logging.info('Finished.')
                    self.image_box = None
                    return

                self.actions_class.move_to_page(driver, i + 1)

                WebDriverWait(driver, 300).until_not(
                    lambda x: self.actions_class.get_now_page(x) == i + 1)

                time.sleep(self.sleep_time + random.random() * 2)
        except Exception as err:
            with open("error.html", "w", encoding="utf-8") as err_source:
                err_source.write(driver.page_source)
            driver.save_screenshot('./error.png')
            logging.error('Something wrong or download finished,Please check the error.png to see the web page.\r\nNormally, you should logout and login, then renew the cookies to solve this problem.')
            logging.error(err)
            self.image_box = None
            return

    def download(self):
        total_manga = len(self.manga_url)
        total_dir = len(self.imgdir)
        if total_manga != total_dir:
            logging.error('Total manga urls given not equal to imgdir.')
            return

        for i in range(total_manga):
            t_manga_url = self.manga_url[i]
            t_img_dir = self.imgdir[i]
            self.check_implementation(t_manga_url)
            if i == 0:
                self.login()
            logging.info("Starting download manga %d, imgdir: %s",
                         i + 1, t_img_dir)
            self.prepare_download(t_img_dir, t_manga_url)
            self.download_book(t_img_dir)
            logging.info("Finished download manga %d, imgdir: %s",
                         i + 1, t_img_dir)
            time.sleep(2)
        self.driver.close()
        self.driver.quit()
