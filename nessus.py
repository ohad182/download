import time
import selenium.webdriver.support.ui as ui
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

driver_path = 'chromedriver78.0.3904.105.exe'
user_name = "felixka@marvell.com"
password = "Root12345"

scan_name = "Test"

# Initialize driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(executable_path=driver_path, options=options)
wait = ui.WebDriverWait(driver, 60)

driver.get("https://10.5.80.56:8834/")
wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
user_name_input = driver.find_element_by_xpath("//input[@type='text']")
user_name_input.send_keys(user_name)
password_input = driver.find_element_by_xpath("//input[@type='password']")
password_input.send_keys(password)
password_input.send_keys(Keys.RETURN)

wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='titlebar']")))

scan_name_tds = driver.find_elements_by_class_name('scan-visible-name')
current_scan_td = next((x for x in scan_name_tds if x.text == scan_name), None)

scan_row = current_scan_td.find_element_by_xpath("..")  # taking the parent table row from table cell
# # )*[@id='DataTables_Table_0']/tbody/tr/td[9]/i" td class = scan-action-1
run_button = scan_row.find_element_by_class_name("scan-action-1")
run_button.click()

# wait for scan to complete
time.sleep(30)

scan_name_tds = driver.find_elements_by_class_name('scan-visible-name')
current_scan_td = next((x for x in scan_name_tds if x.text == scan_name), None)

scan_row = current_scan_td.find_element_by_xpath("..")  # taking the parent table row from table cell
scan_row.click()

report_button = wait.until(
    EC.presence_of_element_located((By.XPATH, "//*[@id='report']")))  # wait for visible and click
report_button.click()
html_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='report']/ul/li[2]")))  # download html
html_button.click()

generate_button = wait.until(
    EC.presence_of_element_located((By.ID, "report-save")))  # wait for visible and click

generate_button.click()

driver.close()
