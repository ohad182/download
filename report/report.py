import sys
import time
import os
import shutil
from threading import Lock

import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import WebDriverException

import common

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from common.hidden_chrome import HiddenChromeWebDriver
from common.models import ReportInformation


class Report(object):
    def __init__(self, report_info: ReportInformation, download_time=20, driver='assets/chromedriver.exe',
                 hidden=False, driver_path=None, notify_temp_dir=True):
        self.report_info = report_info
        self.app_temp_directory = common.create_temp_folder(notify_temp_dir)
        self.chrome_driver_path = driver_path if driver_path is not None else self.copy_driver(driver)
        self.download_time = download_time
        options = webdriver.ChromeOptions()
        options.add_argument("download.default_directory={}".format(self.app_temp_directory))
        if hidden:
            options.add_argument("--headless")
        else:
            options.add_argument("--start-maximized")
        prefs = {'download.default_directory': self.app_temp_directory}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=options)
        # self.driver = HiddenChromeWebDriver(executable_path=self.chrome_driver_path, options=options)
        self.wait = ui.WebDriverWait(self.driver, 60)

    def connect(self):
        self.driver.get(self.report_info.url)
        self.wait_loading_end()
        print("Page loading phase finished")

    def get_select_options(self, select_id):
        plain_select = self.driver.find_element(By.ID, select_id)
        select = ui.Select(plain_select)
        options = [x.text for x in select.options]
        return options

    def select_project_category(self, category, tab_index=None):
        lock = Lock()
        lock.acquire()
        select_id = self.report_info.select_category_id
        if tab_index is not None:
            self.switch_to_tab(tab_index)

        plain_select = self.driver.find_element(By.ID, select_id)
        select = ui.Select(plain_select)

        option_index = -1
        select_options = select.options
        for i in range(len(select_options)):
            if select_options[i].text == category:
                option_index = i
                break

        if option_index is -1:
            raise Exception("Cannot find option '{}' in dropdown '#{}'".format(category, select_id))

        try:
            select.select_by_index(option_index)
        except Exception as e:
            if len(select.all_selected_options) != 1 or select.all_selected_options[0].text != category:
                raise e
        finally:
            lock.release()

    def press_apply(self, tab_index=None):
        if tab_index is not None:
            self.switch_to_tab(tab_index)
        element = self.wait.until(
            EC.presence_of_element_located((By.ID, self.report_info.apply_id)))
        element.click()
        self.wait_loading_end()

    def wait_loading_end(self):
        time.sleep(1)
        self.wait.until(EC.invisibility_of_element_located((By.ID, self.report_info.loader_id)))
        time.sleep(1)

    def download(self, file_type="csv", output_file=None, tab_index=None):
        """
            main menu: m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_ctl01
        :return:
        """
        if tab_index is not None:
            self.switch_to_tab(tab_index)
        output_file = self.report_info.output_file if output_file is None else output_file
        file_type = file_type.lower()
        # time.sleep(1)
        # self.wait.until(EC.invisibility_of_element_located((By.ID, "m_sqlRsWebPart_ctl00_ReportViewer_AsyncWait_Wait")))

        main_menu_id = self.report_info.main_menu_id
        main_menu = self.wait.until(
            EC.presence_of_element_located((By.ID, main_menu_id)))
        main_menu.click()

        export_menu_id = self.report_info.export_menu_id
        export_menu = self.wait.until(
            EC.presence_of_element_located((By.ID, export_menu_id)))
        export_menues = self.driver.find_elements(By.ID, export_menu_id)
        export_menu = export_menues[-1]
        action = ActionChains(self.driver).move_to_element(export_menu)
        action.perform()
        time.sleep(1)

        export_type_id = self.report_info.export_type_id_prefix + self.get_file_type_extension(file_type)
        print("Searching for #{}".format(export_type_id))
        test = self.driver.find_elements(By.ID, export_type_id)
        export_leaf_menu = test[-1]
        export_leaf_menu.click()
        self.download_wait()
        self.move_file(output_file)

    def move_file(self, output_file):
        file_path = max([os.path.join(self.app_temp_directory, f) for f in os.listdir(self.app_temp_directory)],
                        key=os.path.getctime)
        shutil.copy(file_path, output_file)
        try:
            os.remove(file_path)
        except Exception as e:
            print("Failed to remove downloaded file {}".format(file_path))
        print("Report Successfully Downloaded to {}".format(output_file))

    def get_file_type_extension(self, file_type):
        value = "CSV"
        if 'csv' in file_type:
            value = "CSV"
        elif 'excel' in file_type:
            value = "EXCELOPENXML"
        return value

    def download_wait(self):
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < self.download_time:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(self.app_temp_directory):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        time.sleep(1)
        return seconds

    def refresh(self):
        self.driver.refresh()

    def close(self):
        self.driver.close()

    def switch_tabs(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)

    def switch_to_tab(self, tab_index):
        lock = Lock()
        lock.acquire()
        self.driver.switch_to.window(self.driver.window_handles[tab_index])
        lock.release()

    def open_new_tab(self, url=None):
        lock = Lock()
        lock.acquire()
        url = self.report_info.url if url is None else url
        try:
            self.driver.execute_script("window.open('{}');".format(url))
            self.wait_loading_end()
        except WebDriverException as e:
            pass
        finally:
            lock.release()

    def close_current_tab(self):
        self.driver.find_element_by_tag_name('html').send_keys(Keys.CONTROL + 'w')

    def copy_driver(self, driver_relative_path):
        app_driver_path = os.path.join(self.app_temp_directory, "chromedriver.exe")
        if os.path.exists(app_driver_path) and os.path.isfile(app_driver_path):
            print("Chrome driver already in place")
        else:
            chrome_driver = self.get_resource(driver_relative_path)
            shutil.copy(chrome_driver, app_driver_path)
            print("Copied driver to: {}".format(app_driver_path))

        return app_driver_path

    def write_manager_init(self):
        manager_ini_folder = os.path.join(os.path.expanduser("~"), ".wdm")
        manager_ini = self.get_resource('assets/default.ini')
        print("manager ini: {}".format(manager_ini))
        with open(manager_ini) as f:
            try:
                os.makedirs(manager_ini_folder)
            except:
                pass
            manager_ini = os.path.join(manager_ini_folder, 'config.ini')
            with open(manager_ini, 'w') as mf:
                for line in f.readlines():
                    mf.write(line)
                print("Wrote ini file at {}".format(manager_ini))

    def get_resource(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')
        print("Base path: {}".format(base_path))
        return os.path.join(base_path, relative_path)