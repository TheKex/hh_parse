from pprint import pprint
import re

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from compensation.compensation import parse_compensation


def search_terms_in_vacancy(vacancy_link, terms):
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(vacancy_link)
    vacancy_content = driver.find_element(By.CLASS_NAME, 'vacancy-description').text
    driver.close()
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
    vacancies_tag = driver.find_element(By.CLASS_NAME, 'vacancy-serp-content')

    vacancies_list_tags = vacancies_tag.find_elements(By.CLASS_NAME, 'serp-item')
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
    pprint([vacancy for vacancy in vacancies_list if search_terms_in_vacancy(vacancy['link'], ['django', 'flask'])])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
