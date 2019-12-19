from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.exceptions import SiteErrorException


class Downloader(object):
    def __init__(self, url, driver='assets/chromedriver.exe'):
        self.chrome_driver_path = driver
        self.site_url = url
        self.ext_sht = Keys.CONTROL + "m"
        chop = webdriver.ChromeOptions()
        chop.add_extension('assets/Flash-Video-Downloader_v29.1.0.crx')
        self.driver = webdriver.Chrome(executable_path=self.chrome_driver_path, chrome_options=chop)
        self.wait = ui.WebDriverWait(self.driver, 10)
        self.counterWait = ui.WebDriverWait(self.driver, 35)
        # self.set_extension_shortcut()

    def set_extension_shortcut(self):
        self.driver.get('chrome://extensions-frame/')
        self.driver.find_element(By.XPATH, "//a[@class='extension-commands-config']").click()
        self.driver.find_element(By.XPATH, "//span[@class='command-shortcut-text']").send_keys(self.ext_sht)
        self.driver.find_element(By.ID, "extension-commands-dismiss").click()

    def connect(self):
        self.driver.get(self.site_url)

    def perform_search(self, search_text):
        search = self.driver.find_element(By.XPATH, "//input[@name='term'][@type='text']")
        search.send_keys(search_text)
        search = self.driver.find_element(By.XPATH, "//form[@id='mainSearch']/div/span/button")
        search.click()

    def select_season(self, season_num):
        season_link = self.driver.find_element(By.XPATH, "//li[@data-season='{}']".format(season_num))
        season_link.click()

    def select_episode(self, episode_num):
        episode_link = self.counterWait.until(lambda driver: driver.find_element(By.XPATH,
                                                                          "//ul[@id='episode']/li[@data-episode='{}']".format(
                                                                              episode_num)))
        episode_link = self.driver.find_element(By.XPATH,
                                                "//ul[@id='episode']/li[@data-episode='{}']".format(episode_num))
        episode_link.click()

        timer = self.wait.until(lambda driver: driver.find_element(By.XPATH, "//p[@id='waitTime']"))
        timer.location_once_scrolled_into_view
        # footer = self.driver.find_element_by_tag_name('footer')
        # footer.location_once_scrolled_into_view
        # actions = ActionChains(self.driver)
        # actions.move_to_element(footer)
        # p id =waitTime

    def activate_extension(self):
        self.driver.find_element(By.TAG_NAME, "body").send_keys(self.ext_sht)

    def download_using_flash(self):
        try:
            p_button = self.counterWait.until(lambda driver: driver.find_element(By.XPATH,
                                                                                 "//button[@id='proceed']"))
            try:
                error = self.counterWait.until(lambda driver: driver.find_element(By.XPATH,
                                                                                  "//div[@class='err']"))
                if 'שגיאה' in error.text:
                    raise SiteErrorException
            except NoSuchElementException as e:
                print("no such element {}".format(e.msg))
            # EC.
            # self.wait.
            self.activate_extension()

        except TimeoutException as e:
            print("timeout exception")
            error = self.driver.find_element(By.XPATH, "//div[@class='err']")
            if error:
                raise SiteErrorException()
        except SiteErrorException as e:
            raise e

    def refresh(self):
        self.driver.refresh()

    def close(self):
        self.driver.close()

    def switch_tabs(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)

    def open_new_tab(self, url):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        self.driver.get(url)

    def close_current_tab(self):
        self.driver.find_element_by_tag_name('html').send_keys(Keys.CONTROL + 'w')
