from selenium import webdriver
import os, sys, getopt
import time

server_mode = False

if len(sys.argv) >= 2:
    if sys.argv[2] == '-server':
        server_mode = True

if server_mode is False:
    print("Running in dev mode.")

search_term = "carrots"

driver = webdriver.Chrome(executable_path=r"webDrivers\chromedriver.exe")

driver.get("https://www.target.com/s?searchTerm=" + search_term)
time.sleep(5)
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
item_names = driver.find_elements_by_xpath("//a[@data-test='product-title']")
item_prices = driver.find_elements_by_xpath(
    "//span[@data-test='product-price'] | //span[@data-test='product-max-price']")

print(len(item_names))
print(len(item_prices))
length = len(item_prices)
for i in range(0, length):
    print(item_names[i].text + " " + item_prices[i].text)

driver.quit()
print("Finished!")

