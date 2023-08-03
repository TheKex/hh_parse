from pprint import pprint
import re
import time
from concurrent.futures import ProcessPoolExecutor

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from compensation.compensation import parse_compensation

WORKERS = 4

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def wait_element(driver, delay_seconds=1, by=By.TAG_NAME, value=None):
    """
    Иногда элементы на странце не прогружаются сразу
    Функция ждет delay_seconds если элемент еще не прогрузился
    Если за отведенное время элемент не прогружается выбрасывается TimeoutException
    :param driver: driver
    :param delay_seconds: максимальное время ожижания
    :param by: поле поиска
    :param value: значение поиска
    :return: найденный элемент
    """

    return WebDriverWait(driver, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


def search_terms_in_vacancy(driver, vacancy_link, terms):
    driver.get(vacancy_link)
    vacancy_content_element = wait_element(
        driver=driver,
        delay_seconds=20,
        by=By.CLASS_NAME,
        value='vacancy-description'
    )
    vacancy_content = vacancy_content_element.text
    for term in terms:
        if re.search(term, vacancy_content, flags=re.IGNORECASE):
            return True
    return False


def get_page_vacancies(driver, link):
    driver.get(link)

    wait_attempts_count = 5
    vacancies_tag = vacancies_list_tags = None
    result_vacancies_list = []
    for _ in range(wait_attempts_count):
        time.sleep(0.5)
        vacancies_tag = wait_element(
            driver=driver,
            delay_seconds=5,
            by=By.ID,
            value='a11y-main-content'
        )
        vacancies_list_tags = vacancies_tag.find_elements(By.CLASS_NAME, 'serp-item')
        if len(vacancies_list_tags) != 20:
            break

    for vacancy_tag in vacancies_list_tags:
        title_tag = vacancy_tag.find_element(By.CLASS_NAME, 'serp-item__title')
        vacancy_title = title_tag.text
        vacancy_link = title_tag.get_attribute('href')

        try:
            compensation_tag = vacancy_tag.find_element(By.CLASS_NAME, 'bloko-header-section-2')
            compensation = compensation_tag.text
        except NoSuchElementException:
            compensation_tag = None
            compensation = ''

        result_vacancies_list.append({
            'title': vacancy_title,
            'link': vacancy_link,
            'compensation': parse_compensation(compensation)
        })
    return result_vacancies_list


def parse_chunk_of_hh_pages(links, chrome_options):
    driver = webdriver.Chrome(options=chrome_options)
    result = []
    for link in links:
        result += get_page_vacancies(driver, link)
    driver.close()
    return result


def parse_hh_by_chunks(chrome_options, links_list, chunk_size=4):
    result = []
    divided_link_list = list(divide_chunks(links_list, chunk_size))
    with ProcessPoolExecutor(max_workers=4) as pool:
        result += pool.map(
            parse_chunk_of_hh_pages,
            divided_link_list,
            [chrome_options] * len(divided_link_list)
        )
    return result


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    base_url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
    driver.get(base_url)

    pager_tag = wait_element(
        driver=driver,
        delay_seconds=5,
        by=By.CLASS_NAME,
        value='pager'
    )
    pages_tags = pager_tag.find_elements(By.CLASS_NAME, 'pager-item-not-in-short-range')

    last_page_tag = pages_tags[-1].find_element(By.CLASS_NAME, 'bloko-button').find_element(By.TAG_NAME, 'span')
    last_page = int(last_page_tag.text)
    driver.close()
    # for i in range(last_page):
    #    link = f'{base_url}&page={i}'
    #    vacancies_list += get_page_vacancies(driver, link)

    link_list = [f'{base_url}&pase={i}' for i in range(last_page)]

    chunks = int(len(link_list) / WORKERS)
    vacancies_list = [item for sublist in parse_hh_by_chunks(chrome_options, link_list, chunks) for item in sublist]

    print(len(vacancies_list))

    vacancy_chrome_options = Options()
    vacancy_chrome_options.page_load_strategy = 'eager'
    vacancy_chrome_options.add_argument('--headless')
    vacancy_driver = webdriver.Chrome(options=vacancy_chrome_options)

    # pprint([vacancy for vacancy in vacancies_list if
    #         search_terms_in_vacancy(vacancy_driver, vacancy['link'], ['django', 'flask'])])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
