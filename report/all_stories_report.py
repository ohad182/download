import re
from csv import reader
import traceback
from report.base_report import BaseReport
from common.models import ReportInformation


class AllStoriesReport(BaseReport):
    COLUMNS_TO_REMOVE = ['COMMITTEDVERSION', 'EPICKEY']

    def __init__(self, report_info: ReportInformation, update_driver_lock=None, tools_url=None):
        super(AllStoriesReport, self).__init__(report_info, driver_update_lock=update_driver_lock)
        self.tools_url = tools_url

    def get_report_content(self, **kwargs):
        result = ""
        try:
            print("Starts Tools Report")
            self.open(self.tools_url)
            self.select_project_category('MTS')
            self.press_apply()
            tools_table = self._get_table_content()
            tools_lines = tools_table.splitlines()

            # start debug
            # with open('C:\\temp\\bi\\original_tools.txt', 'w') as orig_tools_file:
            #     orig_tools_file.write('\n'.join(tools_lines))
            # end debug

            tools_lines = self._filter_by(tools_lines, "JPROJECT", "SW Infrastructure and Tools")
            print(f"Collected {len(tools_lines)} items from tools report")
            tools_lines = self._update_sprint_name(tools_lines)
            tools_lines = self._remove_columns(tools_lines)
            tools_lines = self._copy_column_values(tools_lines, 'EPICNAME', 'JPROJECT')
            tools_lines = self._add_group(tools_lines, "Tools")

            # start debug
            # with open('C:\\temp\\bi\\modified_tools.txt', 'w') as mod_tools_file:
            #     mod_tools_file.write('\n'.join(tools_lines))
            # end debug

            print("started {}".format(self.report_info.category))
            self.report_info.print_getting()
            self.open_url(verbose=True)
            self.select_project_category(self.report_info.category)
            self.press_apply()
            result = self._get_table_content()

            # with open('C:\\temp\\bi\\original_mts.txt', 'w') as orig_tools_file:
            #     orig_tools_file.write('\n'.join(tools_lines))

            mts_lines = result.splitlines()
            # mts_lines = self._remove_columns(mts_lines)
            mts_lines = self._add_group(mts_lines, "MTS")

            if mts_lines[0] == tools_lines[0]:
                if mts_lines[-1] == '':
                    mts_lines.pop(-1)
                mts_lines.extend(tools_lines[1:])
                result = '\n'.join(mts_lines)
            else:
                print("ERROR! MTS and TOOLS columns not match!")

            print("done {}".format(self.report_info.category))
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        finally:
            self.close()

        return result

    def _add_group(self, table_content, group_name: str):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content
        headers = lines[0].split(',')
        headers.append("GROUP")
        lines[0] = ','.join(headers)
        for index, line_data in enumerate(reader(lines[1:])):  # start from first line (index based - skip 0)
            if ',' in lines[index + 1]:
                # lines[index + 1] = "{},{}".format(lines[index + 1], group_name)
                # splitted_line = self.split_line(lines[index + 1])
                # splitted_line.append(len(headers), group_name)
                lines[index + 1] = self.join_line(line_data + [group_name])
        return lines

    def _copy_column_values(self, content_lines, source_column, target_column):
        headers = content_lines[0].split(',')
        source_index = headers.index(source_column)
        target_index = headers.index(target_column)
        for index, line_data in enumerate(reader(content_lines[1:])):  # start from first line (index based - skip 0)
            if ',' in content_lines[index + 1]:
                line_data[target_index] = line_data[source_index]
                # splitted_line = self.split_line(content_lines[index + 1])
                # splitted_line[target_index] = splitted_line[source_index]
                content_lines[index + 1] = self.join_line(line_data)
        return content_lines

    def _remove_columns(self, table_content):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content

        headers = lines[0].split(',')
        for column_remove in AllStoriesReport.COLUMNS_TO_REMOVE:
            remove_index = headers.index(column_remove)
            headers.pop(remove_index)
            for index, line_data in enumerate(reader(lines[1:])):  # start from first line (index based - skip 0)
                if ',' in lines[index + 1]:
                    line_data.pop(remove_index)
                    lines[index + 1] = self.join_line(line_data)
        lines[0] = ','.join(headers)

        return lines

    def _filter_by(self, table_content, column_name, column_value):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content
        new_data = [lines[0]]
        headers = lines[0].split(',')
        source_index = headers.index(column_name)
        for index, line_data in enumerate(reader(lines[1:])):  # start from first line (index based - skip 0)
            if ',' in lines[index + 1]:
                if column_value in line_data[source_index]:
                    new_data.append(lines[index + 1])

        return new_data

    def _update_sprint_name(self, table_content):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content
        headers = lines[0].split(',')
        sprint_index = headers.index("SPRINT")

        for index, line_data in enumerate(reader(lines[1:])):  # start from first line (index based - skip 0)
            if ',' in lines[index + 1]:
                search = re.search(r"tools\s*(\w*)\s*(\d*)", line_data[sprint_index], re.IGNORECASE)
                if search:
                    new_sprint = f"MTS {search.group(1)} {search.group(2)} Sprint"
                    line_data[sprint_index] = new_sprint
                    lines[index + 1] = self.join_line(line_data)
        return lines

    def join_line(self, line_parts):
        joined = None
        for part in line_parts:
            if ',' in part:
                if joined is None:
                    joined = "\"part\""
                else:
                    joined = f"{joined},\"{part}\""
            else:
                if joined is None:
                    joined = part
                else:
                    joined = f"{joined},{part}"
        return joined
    # def split_line(self, line):
    #     return regex.split(r'(?<![({][^,]*),(?![^,]*[})])', line)
