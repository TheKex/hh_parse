from pprint import pprint
import re
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


from compensation.compensation import parse_compensation


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
    print(vacancy_link, 'POGNALI NAHOI')
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2")


    # class="vacancy-serp-content tag^ main
    # actions = ActionChains(driver)
    # actions.send_keys(Keys.END)
    # actions.perform()

    wait_attempts_count = 10
    vacancies_tag = vacancies_list_tags = None
    for _ in range(wait_attempts_count):
        time.sleep(1)
        print('attempt', _)
        vacancies_tag = driver.find_element(By.ID, 'a11y-main-content')
        vacancies_list_tags = vacancies_tag.find_elements(By.CLASS_NAME, 'serp-item')
        if len(vacancies_list_tags) != 20:
            break
    pager_tag = driver.find_element(By.CLASS_NAME, 'pager')
    pages_tags = pager_tag.find_elements(By.CLASS_NAME, 'pager-item-not-in-short-range')

    last_page_tag = pages_tags[-1].find_element(By.CLASS_NAME, 'bloko-button').find_element(By.TAG_NAME, 'span')
    last_page = last_page_tag.text
    print('last page', last_page)
    vacancies_list = []
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

        vacancies_list.append({
            'title': vacancy_title,
            'link': vacancy_link,
            'compensation': parse_compensation(compensation)
        })

    print(len(vacancies_list))

    vacancy_chrome_options = Options()
    vacancy_chrome_options.page_load_strategy = 'eager'
    vacancy_chrome_options.add_argument('--headless')
    vacancy_driver = webdriver.Chrome(options=vacancy_chrome_options)

    # pprint([vacancy for vacancy in vacancies_list if
    #         search_terms_in_vacancy(vacancy_driver, vacancy['link'], ['django', 'flask'])])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
