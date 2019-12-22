import os
import sys
import shutil
import common
import time
import selenium.webdriver.support.ui as ui
from datetime import datetime
from abc import ABC, abstractmethod

from common.app_dir import AppDir
from common.hidden_chrome import HiddenChromeWebDriver
from common.models import ReportInformation
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class BaseReport(ABC):

    def __init__(self, report_info: ReportInformation, download_time=20, driver_path='assets/chromedriver.exe',
                 driver_update_lock=None):
        self.update_driver_lock = driver_update_lock
        self.report_info = report_info
        self.app_temp_directory = AppDir().app_directory
        self.chrome_driver_path = self._update_driver(driver_path)
        self.download_time = download_time
        options = webdriver.ChromeOptions()
        options.add_argument("download.default_directory={}".format(self.app_temp_directory))
        prefs = {'download.default_directory': self.app_temp_directory}
        options.add_experimental_option("prefs", prefs)

        is_headless = common.str_to_bool(os.environ.get("HEADLESS", "False"))  # if specified headless as true, be true
        if is_headless:
            options.add_argument("--headless")
            self.driver = HiddenChromeWebDriver(executable_path=self.chrome_driver_path, options=options)
        else:
            options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=options)
        self.wait = ui.WebDriverWait(self.driver, 60)

    def _get_table_content(self):
        content = None
        try:
            content = self.driver.execute_script(
                """
var oReq = window.XMLHttpRequest ? new window.XMLHttpRequest() : new ActiveXObject('MSXML2.XMLHTTP.3.0');
if (oReq != null) { 
    oReq.open('GET', $find($find('m_sqlRsWebPart_ctl00_ReportViewer')._internalViewerId).ExportUrlBase+'CSV', false); 
    oReq.send(null);
    if (oReq.status === 200) {
      console.log(oReq.responseText);
      return oReq.responseText;
    }
} 
else { 
    window.console.log('AJAX (XMLHTTP) not supported'); 
} 
                """)
            # print(f"excute result: {stam}")
        except WebDriverException as e:
            # this is ok exception
            pass
        return content

    @abstractmethod
    def get_report_content(self, **kwargs):
        pass

    def open_url(self, verbose=True):
        self.driver.get(self.report_info.url)
        self.wait_loading_end()
        if verbose:
            print("Page loading phase finished")

    def close(self):
        self.driver.quit()

    def wait_loading_end(self):
        self.wait.until(EC.invisibility_of_element_located((By.ID, self.report_info.loader_id)))
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "VisibleReportContentm_sqlRsWebPart_ctl00_ReportViewer_ctl09")))

    def get_select_options(self, select_id, ignore_options=None):
        if ignore_options is None:
            ignore_options = []
        plain_select = self.driver.find_element(By.ID, select_id)
        select = ui.Select(plain_select)
        options = [x.text for x in select.options if x.text not in ignore_options]
        return options

    def select_project_category(self, category):
        select_id = self.report_info.select_category_id
        plain_select = self.driver.find_element(By.ID, select_id)
        select = ui.Select(plain_select)

        select_options = select.options
        option_index = next((idx for idx, option in enumerate(select_options) if option.text == category), -1)

        if option_index is -1:
            raise Exception("Cannot find option '{}' in dropdown '#{}'".format(category, select_id))

        try:
            select.select_by_index(option_index)
        except Exception as e:
            if len(select.all_selected_options) != 1 or select.all_selected_options[0].text != category:
                raise e

    def press_apply(self):
        """

        :return:
        """
        element = self.wait.until(
            EC.presence_of_element_located((By.ID, self.report_info.apply_id)))
        element.click()
        self.wait_loading_end()

    def _update_driver(self, driver_relative_path):
        if self.update_driver_lock is not None:
            self.update_driver_lock.acquire(True)
        app_driver_path = os.path.join(self.app_temp_directory, "chromedriver.exe")
        copy_driver = True
        if os.path.exists(app_driver_path) and os.path.isfile(app_driver_path):
            if datetime.fromtimestamp(os.path.getmtime(app_driver_path)).date() >= common.NEW_DRIVER_DATE:
                copy_driver = False
            else:
                print("Chrome driver requires update!")
        if copy_driver:
            chrome_driver = self.get_resource(driver_relative_path)
            shutil.copy(chrome_driver, app_driver_path)
            print("Copied driver to: {}".format(app_driver_path))
        if self.update_driver_lock is not None:
            self.update_driver_lock.release()
        return app_driver_path

    def get_resource(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, "_MEIPASS", None)
        else:
            base_path = os.path.abspath('.')
        print("Base path: {}".format(base_path))
        return os.path.join(base_path, relative_path)

    def load(self):
        pass
