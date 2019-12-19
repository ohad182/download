import traceback
from report.base_report import BaseReport
from common.models import ReportInformation


class VersionsReport(BaseReport):
    def __init__(self, report_info: ReportInformation, update_driver_lock=None):
        super(VersionsReport, self).__init__(report_info, driver_update_lock=update_driver_lock)

    def get_report_content(self, **kwargs):
        result = ""
        try:
            print("started {}".format(self.report_info.category))
            self.report_info.print_getting()
            self.open_url(verbose=False)
            self.select_project_category(self.report_info.category)
            self.press_apply()
            result = self._get_table_content()
            print("done {}".format(self.report_info.category))
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        finally:
            self.close()

        return result
