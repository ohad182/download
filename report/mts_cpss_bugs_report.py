import io
import traceback
from csv import reader as csv_reader, writer as csv_writer
from report.base_report import BaseReport
from common.models import ReportInformation


class MtsCpssBugsReport(BaseReport):
    COLUMNS_TO_REMOVE = ['SECURITY', 'CSPENDINGSTAGE', 'CUSTOMERFIXDECISION']

    def __init__(self, report_info: ReportInformation, update_driver_lock=None, tools_url=None):
        super(MtsCpssBugsReport, self).__init__(report_info, driver_update_lock=update_driver_lock)
        self.tools_url = tools_url

    def get_report_content(self, **kwargs):
        try:
            print(f"Starts {self.report_info.name} Report")
            mts_lines = self.process_mts_data(kwargs.get('mts_content', None))

            # start debug
            # self.write_file('C:\\temp\\bi\\mts_file.txt', mts_lines)
            # end debug

            print("Done processing MTS data")

            print("Starts CPSS Report")
            self.open_url()
            cpss_lines = self._get_table_content()
            cpss_lines = self._copy_column_values(cpss_lines, "CPSSVERSION", "JPROJECT", "CPSS")
            self.write_file("C:\\temp\\test.csv", cpss_lines)
            cpss_lines = self._add_group(cpss_lines, "CPSS")
            if "CPSSVERSION" in cpss_lines[0]:
                cpss_lines[0] = cpss_lines[0].replace("CPSSVERSION", "PROJECTVERSION")

            # start debug
            # self.write_file('C:\\temp\\bi\\cpss_file.txt', cpss_lines)
            # end debug

            self.write_full_table(cpss_lines=cpss_lines, mts_lines=mts_lines)

            print("Done CPSS Report")
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        finally:
            self.close()

        return None

    def _add_group(self, table_content, group_name: str):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content
        headers = lines[0].split(',')
        headers.append("GROUP")
        lines[0] = ','.join(headers)
        for index, line_data in enumerate(csv_reader(lines[1:])):  # start from first line (index based - skip 0)
            if ',' in lines[index + 1]:
                lines[index + 1] = self.join_csv_line(line_data + [group_name])
        return lines

    def _copy_column_values(self, content_lines, source_column, target_column, empty_replacement=""):
        if isinstance(content_lines, str):
            content_lines = content_lines.splitlines()
        headers = content_lines[0].split(',')
        source_index = headers.index(source_column)
        target_index = headers.index(target_column)
        for index, line_data in enumerate(
                csv_reader(content_lines[1:])):  # start from first line (index based - skip 0)
            if ',' in content_lines[index + 1]:
                if ',' in line_data[source_index]:
                    line_data[target_index] = f"'{line_data[source_index]}'"
                else:
                    line_data[target_index] = line_data[source_index] if line_data[
                                                                             source_index].strip() != "" else empty_replacement
                csv_line = self.join_csv_line(line_data)
                content_lines[index + 1] = csv_line
        return content_lines

    def _remove_columns(self, table_content):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content

        headers = lines[0].split(',')
        for column_remove in MtsCpssBugsReport.COLUMNS_TO_REMOVE:
            remove_index = headers.index(column_remove)
            headers.pop(remove_index)
            for index, line_data in enumerate(csv_reader(lines[1:])):  # start from first line (index based - skip 0)
                if ',' in lines[index + 1]:
                    line_data.pop(remove_index)
                    lines[index + 1] = self.join_csv_line(line_data)
        lines[0] = self.join_csv_line(headers)

        return lines

    def join_csv_line(self, line_parts):
        output = io.StringIO()
        writer = csv_writer(output)
        writer.writerow(line_parts)
        value = output.getvalue()
        return value

    def join_line(self, line_parts):
        joined = None
        for part in line_parts:
            if ',' in part:
                if joined is None:
                    joined = f"\"{part}\""
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

    def _trim_table(self, table_content):
        if isinstance(table_content, str):
            lines = table_content.splitlines()
        else:
            lines = table_content

        start_index = 0
        for i in range(len(lines)):
            current_line = lines[i].lower()
            if current_line.startswith('jproject') or current_line.startswith('jid'):
                start_index = i
                break
        end_index = -1
        while True:
            if lines[end_index] == '':
                end_index = end_index - 1
            else:
                break
        return table_content[start_index:end_index]

    def get_mts_table(self, mts_content):
        mts_table_str = ""
        try:
            content_empty = True
            for report in mts_content:
                can_write = False
                for line_content in report['data'].splitlines():
                    line_content = line_content.strip()
                    if line_content != "":
                        if can_write:
                            mts_table_str = mts_table_str + line_content + "\n"
                        if (line_content.lower().startswith('jproject') or line_content.lower().startswith(
                                'jid')) and not can_write:
                            can_write = True
                            if content_empty:
                                mts_table_str = line_content + "\n"
                                content_empty = False
        except Exception as e:
            print(e)
        return mts_table_str

    def process_mts_data(self, mts_content):
        table_content = self.get_mts_table(mts_content)
        if mts_content == "":
            raise Exception("Unable to process mts table")
        table_content = self._remove_columns(table_content)
        table_content = self._add_group(table_content, "MTS")
        return table_content

    def write_file(self, path, lines):
        if isinstance(lines, str):
            lines = lines.splitlines()
        can_write = False
        result_empty = True
        with open(path, 'w') as output:
            for line_content in lines:
                line_content = line_content.strip()
                if line_content != "":
                    if can_write:
                        try:
                            output.write(line_content + "\n")
                        except Exception as e:
                            print("unable to write: {}".format(line_content))
                        continue
                    if (line_content.lower().startswith('jproject') or line_content.lower().startswith(
                            'jid')) and not can_write:
                        can_write = True
                        if result_empty:
                            output.write(line_content + "\n")
                            result_empty = False

    def write_full_table(self, cpss_lines, mts_lines):
        result_empty = True
        with open(self.report_info.output_file, 'w') as output:
            can_write = False
            all_lines = cpss_lines + mts_lines
            for line_content in all_lines:
                line_content = line_content.strip()
                if line_content != "":
                    if line_content.lower().startswith('jproject') or line_content.lower().startswith('jid'):
                        can_write = False
                    if can_write:
                        try:
                            output.write(line_content + "\n")
                        except Exception as e:
                            print("unable to write: {}".format(line_content))
                        continue
                    if (line_content.lower().startswith('jproject') or line_content.lower().startswith(
                            'jid')) and not can_write:
                        can_write = True
                        if result_empty:
                            output.write(line_content + "\n")
                            result_empty = False

        print(f"Report generated at: {self.report_info.output_file}")
