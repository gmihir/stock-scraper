#all imports
import os, time, csv, credentials, pandas as pd, numpy as np
from pathlib import Path
from pandas import DataFrame
from selenium import webdriver
from credentials import email, password
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#all the variables
trading_view_url, finviz_url, nasdaq_url = "https://www.tradingview.com", "https://finviz.com/quote.ashx?t=", "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=&render=download"
name_list, symbol_list, price_list = list(), list(), list()
max_len = 0

def stock_adder():

    #setting up variables
    global trading_view_url, finviz_url, nasdaq_url, name_list, symbol_list, price_list

    #removes already existing file
    if os.path.exists("files/companylist.csv"):
        os.remove("files/companylist.csv")

    #changes download locations
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : '/Users/keskinmbaha/Desktop/All/MacBook/Learning to Code/stock-scraper/files'}
    options.add_experimental_option('prefs', prefs)

    #downloads a file listing all the stocks from major trading platforms
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.get(nasdaq_url)
    time.sleep(2) #implicit wait doesn't work

    #gets stocks and symbols from excel
    csv = pd.read_csv("files/companylist.csv")
    name_list = list(csv['Name'])
    symbol_list = list(csv['Symbol'])

    """
    #can add symbol one by one
    while true:
        symbol = input("Enter a stock symbol. Otherwise enter no.")

        if symbol == "no" or symbol == "No" or symbol == "NO" or symbol == "nO":
            break
        symbol_list.append(symbol)
    """

    driver.quit()


def paper_day_trader():

    #setting up variables
    global trading_view_url, finviz_url, nasdaq_url, name_list, symbol_list, price_list

    #changes download locations
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : '/Users/keskinmbaha/Desktop/All/MacBook/Learning to Code/stock-scraper/files'}
    options.add_experimental_option('prefs', prefs)

    #sets up the driver and action variables
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    actions = ActionChains(driver)
    driver.implicitly_wait(2)
    driver.maximize_window()

    #logins to trading view
    driver.get(trading_view_url)
    driver.find_element_by_class_name("tv-header__link.tv-header__link--signin.js-header__signin").click()
    
    try: driver.find_element_by_class_name("tv-signin-dialog__social.tv-signin-dialog__toggle-email.js-show-email").click()
    except: pass

    inputs = driver.find_elements_by_class_name("tv-control-material-input.tv-signin-dialog__input.tv-control-material-input__control")
    i = 0

    for inp in inputs:
        if i == 0:
            inp.send_keys(email)
            i += 1
        else:
            inp.send_keys(password)

    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1) #waits for login to register

    #looping through all the stocks
    for i in range(0,10):
        symbol = symbol_list[i]
        driver.find_element_by_class_name("tv-header-search__inputwrap").send_keys(symbol)
        actions.send_keys(Keys.ENTER).perform()
        
        driver.find_element_by_class_name("tv-symbol-price-quote__value.js-symbol-last").click() #loads the element fully so no empty string is appended
        price = driver.find_element_by_class_name("tv-symbol-price-quote__value.js-symbol-last").text
        price_list.append(price)

    #removes already existing file
    if os.path.exists("files/output.csv"):
        os.remove("files/output.csv")

    #finds largest length list
    largest_len(symbol_list)
    largest_len(name_list)
    largest_len(price_list)

    #padding lists to be same length
    pad_dict_list(symbol_list)
    pad_dict_list(name_list)
    pad_dict_list(price_list)

    #create new csv
    df = DataFrame({"symbol" : symbol_list, "name" : name_list, "price" : price_list})
    df.to_csv("files/output.csv", index=False, header=True)

    #sign out of tradingview and quits the browser
    driver.find_element_by_class_name("tv-header__dropdown-text.tv-header__dropdown-text--username.js-username.tv-header__dropdown-text--ellipsis.apply-overflow-tooltip.common-tooltip-fixed").click()
    driver.find_element_by_class_name("tv-header__dropdown-link.js-signout").click()
    driver.quit()

def pad_dict_list(dict_list):
    global max_len
    while len(dict_list) != max_len:
        dict_list.append("")

def largest_len(dict_list):
    global max_len
    if len(dict_list) > max_len:
        max_len = len(dict_list)

"""main method"""
stock_adder()
paper_day_trader()