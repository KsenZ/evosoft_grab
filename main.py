from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup as bs

from time import sleep
import csv
import requests
import random


def get_proxy():
    response = requests.get("https://free-proxy-list.net/")
    soup = bs(response.content, "html.parser")
    tds = soup.find("tbody").find_all("tr")
    proxies = []
    for io in tds:
        proxies.append(f"{io.find_all('td')[0].text}:{io.find_all('td')[1].text}")
    return proxies


def main():
    url = "https://www.nseindia.com"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")
    options.add_argument(f"proxy-server={random.choice(get_proxy())}")

    service = ChromeService(executable_path="driver/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.maximize_window()
        driver.get(url=url)
        sleep(5)
        market_data = driver.find_element(By.XPATH, '//*[text()="Market Data"]')
        pre_open_market = driver.find_element(By.XPATH, '//*[text()="Pre-Open Market"]')
        action = ActionChains(driver)
        action.move_to_element(market_data)
        action.move_to_element(pre_open_market)
        action.click(pre_open_market)
        action.perform()
        sleep(5)
        table = driver.find_element(By.XPATH, '//*[@id="livePreTable"]')
        with open('table.csv', 'w', newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=';', dialect='unix', quoting=csv.QUOTE_MINIMAL)
            rows = table.find_elements(By.XPATH, '//*[@id="livePreTable"]/tbody/tr')
            n = 1
            if n < len(rows):
                for row in rows:
                    for name in row.find_elements(By.XPATH, f'//*[@id="livePreTable"]/tbody/tr[{n}]/td[2]'):
                        for final_price in row.find_elements(By.XPATH, f'//*[@id="livePreTable"]/tbody/tr[{n}]/td[7]'):
                            wr.writerow([name.text, final_price.text])
                    n += 1

        driver.back()
        sleep(3)
        scroll = driver.find_element(By.XPATH, '//*[@id="main_slider"]/div[2]/ul')
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll)
        sleep(3)
        nifty_bank = driver.find_element(By.XPATH, '//*[@id="nse-indices"]/div[2]/div/div/nav/div/div/a[4]')
        view_all = driver.find_element(By.XPATH, '//*[@id="tab4_gainers_loosers"]/div[3]/a')
        action.move_to_element(nifty_bank)
        action.click(nifty_bank)
        action.perform()
        sleep(3)
        driver.execute_script("arguments[0].scrollIntoView(true);", nifty_bank)
        action.click(view_all)
        action.perform()
        sleep(3)
        scroll_table = driver.find_element(By.XPATH, '//*[@id="radio_stock"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll_table)
        sleep(5)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
