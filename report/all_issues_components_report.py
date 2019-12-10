import traceback
from report.base_report import BaseReport
from common.models import ReportInformation


class AllIssuesComponentReport(BaseReport):
    def __init__(self, report_info: ReportInformation, update_driver_lock=None):
        super(AllIssuesComponentReport, self).__init__(report_info, notify_temp_dir=False,
                                                       driver_update_lock=update_driver_lock)

    def get_options_map(self):
        pass

    def get_report_content(self, **kwargs):
        option = kwargs.get("option", None)
        result = ""
        if option is None:
            print("Error! no option provided")
            return result

        try:
            print("started {}".format(option))
            self.open_url(verbose=False)
            self.select_project_category(option)
            self.press_apply()
            result = self._get_table_content()
            print("done {}".format(option))
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        finally:
            self.close()

        return result

    @staticmethod
    def write_report(results, report_data: ReportInformation):
        try:
            with open(report_data.output_file, 'w') as result_file:
                result_empty = True
                for report in results:
                    can_write = False
                    for line_content in report['data'].splitlines():
                        line_content = line_content.strip()
                        if line_content != "":
                            if can_write:
                                try:
                                    result_file.write(line_content + "\n")
                                except Exception as e:
                                    print("unable to write: {}".format(line_content))
                                continue
                            if line_content.lower().startswith('jproject') and not can_write:
                                can_write = True
                                if result_empty:
                                    result_file.write(line_content + "\n")
                                    result_empty = False

            print(f"Report generated at: {report_data.output_file}")
        except Exception as e:
            print(e)
