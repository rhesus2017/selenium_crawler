# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from logging.handlers import TimedRotatingFileHandler
import traceback
from datetime import datetime
import time
import json
import re
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger()
logger.setLevel('INFO')
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)1.1s %(lineno)3s:%(funcName)-16.16s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

current_dir = os.path.dirname(os.path.abspath(__file__))
current_filename = os.path.splitext(os.path.basename(__file__))[0]
filename = current_dir + os.sep + "log" + os.sep + current_filename + ".log"
handler = TimedRotatingFileHandler(filename=filename, when='midnight', backupCount=7, encoding='utf8')
handler.suffix = '%Y%m%d'
handler.setFormatter(formatter)
logger.addHandler(handler)

chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920,9720')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36')

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/Users/ktj/Documents/github/selenium_crawler/driver/chromedriver')
driver.implicitly_wait(3)


def naver_map_crawler(keyword, address, keyword_index, last):
    result = ''
    next_keyword = 'false'
    start = datetime.now()

    try:
        logger.info('=' * 80)
        logger.info(f'[{keyword_index} / {last}] {keyword}')
        logger.info('=' * 80)

        # ?????? ???????????? ??????
        city = address.split(' ')[1]
        logger.info(f'[{city} {keyword}]??? ???????????? ???????????????.')
        driver.get(f'https://map.naver.com/v5/search/{city} {keyword}')

        # ????????? ????????? ?????? 3??? ??????
        time.sleep(3)

        # ???????????? ?????? [1]
        if next_keyword == 'false':

            # ?????? ??????????????? ??????
            driver.switch_to.frame(driver.find_element_by_tag_name('#searchIframe'))

            # ????????? ?????? ?????? ?????? ??????
            check_load = driver.find_elements_by_css_selector('#_pcmap_list_scroll_container + div > a:last-child')
            if len(check_load) > 0:
                next_keyword = 'false'
            else:
                search_failed = driver.find_element_by_css_selector('#app-root > div > div > div > div')
                search_failed = search_failed.text
                if search_failed == '????????? ?????? ????????? ????????????.':
                    next_keyword = 'true'

        # ??? ???????????? ???????????? ????????? ????????? ?????? [2]
        if next_keyword == 'true':

            # ??? ???????????? ???????????? ??????
            logger.info(f' - ????????? ?????? ????????? ????????????. ??? ???????????? ???????????? [{keyword}]??? ???????????? ???????????????.')
            driver.get(f'https://map.naver.com/v5/search/{keyword}')

            # ????????? ????????? ?????? 3??? ??????
            time.sleep(3)

            # ?????? ??????????????? ??????
            driver.switch_to.frame(driver.find_element_by_tag_name('#searchIframe'))

            # ????????? ?????? ?????? ?????? ??????
            check_load = driver.find_elements_by_css_selector('#_pcmap_list_scroll_container + div > a:last-child')
            if len(check_load) > 0:
                next_keyword = 'false'
            else:
                search_failed = driver.find_element_by_css_selector('#app-root > div > div > div > div')
                search_failed = search_failed.text
                if search_failed == '????????? ?????? ????????? ????????????.':
                    next_keyword = 'true'

        # ??? ???????????? ???????????? ????????? ????????? ?????? [3]
        if next_keyword == 'true':

            # ~??? ??????
            short_keyword = re.split('( \w+???$)', keyword)
            short_keyword = short_keyword[0]

            # ??? ???????????? ???????????? ??????
            logger.info(f' - ????????? ?????? ????????? ????????????. ??? ???????????? ???????????? [{short_keyword}]??? ???????????? ???????????????.')
            driver.get(f'https://map.naver.com/v5/search/{short_keyword}')

            # ????????? ????????? ?????? 3??? ??????
            time.sleep(3)

            # ?????? ??????????????? ??????
            driver.switch_to.frame(driver.find_element_by_tag_name('#searchIframe'))

            # ????????? ?????? ?????? ?????? ??????
            check_load = driver.find_elements_by_css_selector('#_pcmap_list_scroll_container + div > a:last-child')
            if len(check_load) > 0:
                pass
            else:
                search_failed = driver.find_element_by_css_selector('#app-root > div > div > div > div')
                search_failed = search_failed.text
                if search_failed == '????????? ?????? ????????? ????????????.':
                    logger.info('- ????????? ?????? ????????? ????????????. ?????? ???????????? ???????????????.')
                    result = '???????????? ??????'
                    return result

        # ????????? ?????? ??????
        li_lists_len = len(driver.find_elements_by_css_selector('#_pcmap_list_scroll_container > ul > li'))
        logger.info(f' - {li_lists_len}?????? ???????????? ???????????????.')

        for i in range(1, li_lists_len + 1):

            # ??????????????? 20????????? ?????? ?????? ??????
            if i == 21:
                logger.info('- ???????????? ?????? ????????????. ?????? ???????????? ???????????????.')
                result = '?????? ??????'
                return result

            # ?????? ???????????? ?????? ???????????? ?????? ?????? ??????
            try:
                # ?????? ??????????????? ??????
                driver.switch_to.default_content()

                # ?????? ???????????? ?????? ???????????? ???????????? ??????
                driver.find_element_by_css_selector('#container > shrinkable-layout > div > app-base > search-layout > div.sub.ng-star-inserted.-covered')
                logger.info(f'[1/{li_lists_len}]?????? ???????????? ???????????????.')

            # ?????? ???????????? ?????? ???????????? ?????? ?????? ?????? ??????
            except NoSuchElementException as e:

                # ?????? ??????????????? ??????
                driver.switch_to.frame(driver.find_element_by_tag_name('#searchIframe'))

                # ????????? ??????
                logger.info(f'[{i}/{li_lists_len}]?????? ???????????? ???????????????.')
                main_list_divs = driver.find_element_by_css_selector(f'#_pcmap_list_scroll_container > ul > li:nth-child({i}) > div > a > div > div > span')
                main_list_divs.click()

                # ?????? ??????????????? ??????
                driver.switch_to.default_content()

            # ?????? ??????????????? ??????
            driver.switch_to.frame(driver.find_element_by_tag_name('#entryIframe'))

            # ????????? ????????? ?????? 3??? ??????
            time.sleep(3)

            # ???????????? ?????? ?????? ???????????? ????????????
            if driver.find_element_by_css_selector('#_title > span:nth-child(2)').text == '?????????':
                logger.info(' - ??????????????????. ?????? ???????????? ???????????????')
                continue

            # ????????????????????? ?????? ?????? ????????????
            if driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > strong').text == '??????':

                # ?????? ??? ????????? ????????? ?????? ?????????
                real_address_01 = ''
                address_01 = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > div span:nth-child(1)').text
                address_01_split = address_01.split(' ')
                for index, address_01 in enumerate(address_01_split):
                    if index == 0:
                        continue
                    elif index == 1:
                        real_address_01 = address_01
                    else:
                        real_address_01 = real_address_01 + ' ' + address_01

                real_address_01 = re.split('(\w+[???|???|???|???|???|???|???|???] \d+-?\d*)', real_address_01)
                if len(real_address_01) != 1:
                    real_address_01 = real_address_01[0] + real_address_01[1]
                else:
                    real_address_01 = real_address_01[0]
                real_address_01.strip()

                # ?????? ?????? ????????????
                logger.info(' - ?????? ?????? ????????? ???????????????.')
                change_button = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > div span:nth-child(2)')
                change_button.click()

                # ?????? ??? ????????? ?????? ?????? ?????????
                real_address_02 = ''
                address_02 = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > div span:nth-child(1)').text
                address_02_split = address_02.split(' ')
                for index, address_02 in enumerate(address_02_split):
                    if index == 0:
                        continue
                    elif index == 1:
                        real_address_02 = address_02
                    else:
                        real_address_02 = real_address_02 + ' ' + address_02

                real_address_02 = re.split('(\w+[???|???|???|???|???|???|???|???] \d+-?\d*)', real_address_02)
                if len(real_address_02) != 1:
                    real_address_02 = real_address_02[0] + real_address_02[1]
                else:
                    real_address_02 = real_address_02[0]
                real_address_02.strip()

            # ??????????????? ?????? ?????? ?????? ????????????
            else:

                # ?????? ??? ????????? ????????? ?????? ?????????
                real_address_01 = ''
                address_01 = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(2) > div span:nth-child(1)').text
                address_01_split = address_01.split(' ')
                for index, address_01 in enumerate(address_01_split):
                    if index == 0:
                        continue
                    elif index == 1:
                        real_address_01 = address_01
                    else:
                        real_address_01 = real_address_01 + ' ' + address_01

                real_address_01 = re.split('(\w+[???|???|???|???|???|???|???|???] \d+-?\d*)', real_address_01)
                if len(real_address_01) != 1:
                    real_address_01 = real_address_01[0] + real_address_01[1]
                else:
                    real_address_01 = real_address_01[0]
                real_address_01.strip()

                # ?????? ?????? ????????????
                logger.info(' - ?????? ?????? ????????? ???????????????.')
                change_button = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(2) > div span:nth-child(2)')
                change_button.click()

                # ?????? ??? ????????? ?????? ?????? ?????????
                real_address_02 = ''
                address_02 = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(2) > div > div > div:nth-child(2)').text
                address_02 = address_02.split(' ??????')[0]
                address_02_split = address_02.split(' ')
                for index, address_02 in enumerate(address_02_split):
                    if index == 0:
                        continue
                    elif index == 1:
                        real_address_02 = address_02
                    else:
                        real_address_02 = real_address_02 + ' ' + address_02

                real_address_02 = re.split('(\w+[???|???|???|???|???|???|???|???] \d+-?\d*)', real_address_02)
                if len(real_address_02) != 1:
                    real_address_02 = real_address_02[0] + real_address_02[1]
                else:
                    real_address_02 = real_address_02[0]
                real_address_02.strip()

            # ?????? ????????????
            logger.info(' - ?????? ??? ????????? ????????? JSON??? ????????? ???????????????.')
            logger.info(f'    - ?????? ??? ????????? ????????? ?????? : {real_address_01}')
            logger.info(f'    - ?????? ??? ????????? ?????? ?????? : {real_address_02}')
            logger.info(f'    - JSON??? ?????? : {address}')

            regexp_01 = re.compile(rf'{real_address_01}')
            regexp_02 = re.compile(rf'{real_address_02}')
            if regexp_01.search(address) or regexp_02.search(address):
                logger.info('    - ?????? ??? ?????? ????????? JSON??? ????????? ???????????????.')
            else:
                logger.info('    - ?????? ??? ?????? ????????? JSON??? ????????? ???????????? ????????????.')

                # ?????? ????????? 1?????? ??????
                if li_lists_len == 1:
                    result = '?????? ?????????'
                    return result

                # ?????? ????????? 1????????? ?????? ??????
                else:

                    # ?????? ??????????????? ??????
                    driver.switch_to.default_content()

                    # ?????? ????????? ??????
                    close_button = driver.find_element_by_css_selector('.sub > entry-layout > entry-close-button > button')
                    close_button.click()

                    # ?????? ??????????????? ??????
                    driver.switch_to.frame(driver.find_element_by_tag_name('#searchIframe'))

                    # ?????? ??????????????? ????????? ???????????? ??????
                    if i == li_lists_len:
                        logger.info('1')
                        result = '?????? ?????????'
                        return result

                    # ?????? ??????????????? ?????? ????????? ???????????? ????????? ??????
                    else:
                        result = '?????? ?????????'
                        continue

            # ????????????
            if driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1) > strong').text == '??????':
                phone = ''
                logger.info(f' - ???????????? : {phone}')
            else:
                phone = driver.find_element_by_css_selector('#app-root div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li:nth-child(1)').text.replace('??????', '').replace('??????', '')
                phone = phone.strip()
                logger.info(f' - ???????????? : {phone}')

            # ?????? ???
            if len(driver.find_elements_by_css_selector('#_title + div > span')) == 3:
                visitant_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(2) em').text.replace(',', '')
                blog_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(3) em').text.replace(',', '')
                logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                logger.info(f' - ????????? ?????? ?????? : {blog_review}')
            elif len(driver.find_elements_by_css_selector('#_title + div > span')) == 2:
                if driver.find_element_by_css_selector('#_title + div > span:nth-child(1)').text.find('???????????????') != -1:
                    visitant_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(1) em').text.replace(',', '')
                    blog_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(2) em').text.replace(',', '')
                    logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                    logger.info(f' - ????????? ?????? ?????? : {blog_review}')
                else:
                    visitant_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(2) em').text.replace(',', '')
                    blog_review = 0
                    logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                    logger.info(f' - ????????? ?????? ?????? : {blog_review}')
            elif len(driver.find_elements_by_css_selector('#_title + div > span')) == 1:
                if driver.find_element_by_css_selector('#_title + div > span:nth-child(1)').text.find('???????????????') != -1:
                    visitant_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(1) em').text.replace(',', '')
                    blog_review = 0
                    logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                    logger.info(f' - ????????? ?????? ?????? : {blog_review}')
                else:
                    visitant_review = 0
                    blog_review = driver.find_element_by_css_selector('#_title + div > span:nth-child(1) em').text.replace(',', '')
                    logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                    logger.info(f' - ????????? ?????? ?????? : {blog_review}')
            elif len(driver.find_elements_by_css_selector('#_title + div > span')) == 0:
                visitant_review = 0
                blog_review = 0
                logger.info(f' - ????????? ?????? ?????? : {visitant_review}')
                logger.info(f' - ????????? ?????? ?????? : {blog_review}')

            # ??????
            result = '??????'
            break

    except Exception as e:
        logger.error(traceback.format_exc())

    finally:
        elapsed_time = (datetime.now() - start).total_seconds()
        logger.info("????????????  {:5.2f}".format(elapsed_time))

    return result


if __name__ == '__main__':
    success = 0
    no_result = 0
    no_match = 0
    lots_of_items = 0
    start = datetime.now()
    db = None

    try:
        # JSON?????? ????????????
        with open('/Users/ktj/Documents/github/selenium_crawler/json/store.json??????', 'r', encoding='UTF-8') as f:
            json_data = json.load(f)

        # ????????? ??????
        for row in json_data:

            keyword = row['title'].strip()
            address = row['com_addr']
            index = row['idx']

            result = naver_map_crawler(keyword, address, index, len(json_data))
            # result = naver_map_crawler('?????????', '????????? ????????? ????????? ???????????? 1402 105???', 8, 8478)
            logger.info(f"[{keyword}] ??? ????????? ?????? : {result}")

            if result == '??????':
                success = success + 1
            elif result == '?????? ?????????':
                no_match = no_match + 1
            elif result == '???????????? ??????':
                no_result = no_result + 1
            elif result == '?????? ??????':
                lots_of_items = lots_of_items + 1

            logger.info(f'?????? : {success} / ?????? ????????? : {no_match} / ???????????? ?????? : {no_result} / ?????? ?????? : {lots_of_items}')

    except Exception as e:
        logger.error(traceback.format_exc())

    finally:
        driver.quit()
        db.close()
        elapsed_time = (datetime.now() - start).total_seconds()
        logger.info("??? ????????????  {:5.2f}".format(elapsed_time))
