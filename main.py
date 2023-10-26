import os
import csv
import time

from pathlib import Path
from selenium import webdriver
from datetime import datetime as dt
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service as ChromeService


class MannScraper:
    """Gets the table data for all the models and its variants using the model and variant dropdown"""
    main_page = 'https://catalog.mann-filter.com/EU/por/vehicle/MANN-FILTER%20Katalog%20Europa/Autom%C3%B3veis/' \
                'Linha%20Leve/ACURA/Legend'

    def __init__(self):
        """ Initialize the webdriver"""
        self.driver = None

    def get_model_variants_data(self, month: str, year: str):
        """Gets the table data by selecting the models and its variants in the dropdowns and then using pandas to
        extract the table"""
        actions = ActionChains(self.driver)
        characters = ['\\', '/', ':', '?', '<', '>', '|']
        wait5s = WebDriverWait(self.driver, 5)
        self.driver.get(self.main_page)
        time.sleep(2)
        self._click_accept_cookies()
        model_dropdown, variant_dropdown = wait5s.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, 'div.likeSelect')))
        model_elms = model_dropdown.find_elements(By.CSS_SELECTOR, '.rf-sel-opt')
        for idx, model_elm in enumerate(model_elms):
            model_dropdown, variant_dropdown = wait5s.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, 'div.likeSelect')))
            time.sleep(1)
            model_elms = model_dropdown.find_elements(By.CSS_SELECTOR, '.rf-sel-opt')
            model_name = model_elms[idx].get_attribute('innerText').strip()
            for char in characters:
                model_name = model_name.replace(char, '').strip()
            wait5s.until(EC.visibility_of(model_dropdown)).click()
            time.sleep(2)
            if idx == 7:
                scroll_origin = ScrollOrigin.from_element(model_elms[idx-1])
                actions.scroll_from_origin(scroll_origin, 0, 20).perform()
                time.sleep(2)
            model_elms[idx].click()
            time.sleep(2)
            model_dropdown, variant_dropdown = wait5s.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, 'div.likeSelect')))
            variant_elms = variant_dropdown.find_elements(By.CSS_SELECTOR, '.rf-sel-opt')
            for num, variant_elm in enumerate(variant_elms):
                model_dropdown, variant_dropdown = wait5s.until(EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 'div.likeSelect')))
                time.sleep(1)
                variant_elms = variant_dropdown.find_elements(By.CSS_SELECTOR, '.rf-sel-opt')
                variant_name = variant_elms[num].get_attribute('innerText').strip()
                for char in characters:
                    variant_name = variant_name.replace(char, '').strip()
                wait5s.until(EC.visibility_of(variant_dropdown)).click()
                time.sleep(2)
                if num == 7:
                    scroll_origin = ScrollOrigin.from_element(variant_elms[idx-1])
                    actions.scroll_from_origin(scroll_origin, 0, 20).perform()
                    time.sleep(2)
                variant_elms[num].click()
                time.sleep(2)
                print(f"\t\t{model_name}\t\t{variant_name}\t\t")
                self._get_table_data(model_name, month, variant_name, year)

    def _get_table_data(self, model_name, month, variant_name, year):
        """Gets the table data for model variant combination and writes it down into csv."""
        wait5s = WebDriverWait(self.driver, 5)
        table = wait5s.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table')))
        table_rows = table.find_elements(By.CSS_SELECTOR, '.row')
        csv_data = list()
        for i, row in enumerate(table_rows):
            table_headers = [elm.get_attribute('data-label').strip() for elm in
                             row.find_elements(By.CSS_SELECTOR, 'div')
                             if elm.get_attribute('data-label')]
            table_data = [elm.get_attribute('innerText').strip() for elm in row.find_elements(By.CSS_SELECTOR, 'div')
                          if not elm.get_attribute('data-label')]
            csv_data.append(dict(zip(table_headers, table_data)))
        self._write_csv_data(csv_data, model_name, variant_name, month, year)

    @staticmethod
    def _write_csv_data(dict_data: list[dict[str, str]], model_name: str, variant_name: str, month: str, year: str):
        """Create a csv file in filepath and write the same using DictWriter class from csv module.
        params dict_data: list of dict key value pairs.
        """
        filepath = Path('scraped-data') / f'{"-".join(model_name.split())}_{"-".join(variant_name.split())}({month}-{year}).csv'
        with open(file=filepath, mode='w', encoding='UTF-8', newline='\n') as csvfile:
            header_names = dict_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=header_names)
            writer.writeheader()
            writer.writerows(dict_data)

    def _click_accept_cookies(self):
        """Clicks on the accept button for cookies popup."""
        wait5s = WebDriverWait(self.driver, 5)
        try:
            accept_button = wait5s.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')))
            wait5s.until(EC.visibility_of(accept_button)).click()
        except exceptions.TimeoutException:
            pass


def main():
    CHROME_DRIVER_PATH = os.environ['CHROME_DRIVER_PATH']
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    month = str(dt.now().date().month)
    year = str(dt.now().date().year)
    mannscraper = MannScraper()
    mannscraper.driver = driver
    mannscraper.get_model_variants_data(month, year)


if __name__ == '__main__':
    main()
