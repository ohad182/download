import os
from datetime import datetime

APP_NAME = "Automated Reports"
APP_DATA = 'APPDATA'

ALL_COMPONENTS_REPORT_NAME = 'AllIssuesComponents'
ALL_COMPONENTS_REPORT_URL = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All_Issues_of_a_Project_with%20components.rdl'
DEFAULT_ALL_COMPONENTS_PROJECTS = ["Hawk", "Alleycat5", "Phoenix", "Falcon"]

VERSIONS_REPORT_NAME = 'Versions'
VERSIONS_REPORT_URL = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/Versions%20Data.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErratum%25255fHierarchy%25252erdl%2Dp%5FID%253D121%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'

ALL_STORIES_REPORT_NAME = 'AllStories'
ALL_STORIES_REPORT_URL = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All%20Stories%20by%20Rank%20with%20sub%20tasks.rdl'

MTS_PROJECTS_REPORT_NAME = 'MtsBugs'
MTS_PROJECTS_URL = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/NPS%20All%20Bugs%20for%20project.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErrata%252520with%252520same%252520JIRA%252520id%25252erdl%2Dp%5FID%253D96%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'

# Website ID fields
APPLY_ID = "m_sqlRsWebPart_ctl00_ctl19_ApplyParameters"
LOADER_ID = "m_sqlRsWebPart_ctl00_ReportViewer_AsyncWait_Wait"
SELECT_CATEGORY_ID = "m_sqlRsWebPart_ctl00_ctl19_ctl06_ctl03_ddValue"
VERSION_DROPDOWN_ID = 'm_sqlRsWebPart_ctl00_ctl19_ctl06_ctl05_ddValue'
MAIN_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_ctl01_t"
EXPORT_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_Export"
EXPORT_TYPE_ID_PREFIX = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_"

NEW_DRIVER_DATE = datetime.strptime('2019-12-09', '%Y-%m-%d').date()

MTS_IGNORE_OPTIONS = ['ARC-II-III', 'Astute', 'Belkin', 'CORE', 'CPSS', 'CPSS_JOBS', 'CS Belkin', 'CS Cisco', 'CS Dell',
                      'CS Demo', 'CS Dormant', 'CS Eltex', 'CS Extreme', 'CS Internal Info', 'CS Larch', 'CS Netgear',
                      'CS Tachi', 'Contax', 'Contax_Maintenance', 'Contax_PostRTS', 'Continuous Integration', 'DFM',
                      'FE_Test', 'FPA', 'Franchise', 'Franchise_Eltex', 'Franchise_Larch', 'Hybrid-Stack', 'ISR',
                      'LGS3xx', 'LGS5xx', 'Lessons Learned', 'MK CS Tachi', 'MKT Pilgrim', 'MTS Microsoft',
                      'MTS Opportunities', 'MTS Robot Pilot', 'MTS SIP5', 'MTS_Off_The_Shelf', 'MTS_PIPE', 'Micro-Init',
                      'NG-GS7XXTP', 'NG-XS728T', 'NG-XS748T', 'NPS ET', 'NPS Internal Info', 'NetGear_MS510',
                      'Nikola_ESW2_SG350G', 'Nikola_ESW2_SG550X', 'Nikola_SG500X', 'Nikola_SG500XG', 'Nikola_Sx200',
                      'Nikola_Sx300', 'Nikola_Sx500', 'OAM FW', 'OpenSwitch', 'Plasma_ARCII', 'PoE',
                      'Python Automation', 'RD_Aldrin', 'RD_Lewis', 'RD_xCat3', 'RnD Demo', 'Ryan', 'SAI-SONiC',
                      'SAI1.0', 'SNI', 'SONIC', 'SONIC-Alibaba', 'SV Networking Automation',
                      'SW Infrastructure and Tools', 'Serdes', 'Switch Dashboard', 'TI-PoE', 'TL-SH1226',
                      'Tachi', 'Tachi 2 (920)', 'Tesla 2.0', 'Tesla 2.1', 'Tesla 2.2', 'Tesla 2.2.5', 'Tesla 2.2.7',
                      'Tesla 2.2.8', 'Tesla 2.3', 'Tesla 2.3.5', 'Tesla 2.4', 'Tesla 2.4.5', 'Test Security',
                      'Test import web project', 'Troya', 'Validation Book', 'Validation Infra']


def create_temp_folder(notify: bool):
    app_data = os.getenv(APP_DATA)
    if app_data is not None:
        app_data = os.path.join(app_data, APP_NAME)
        try:
            os.makedirs(app_data)
        except:
            pass

    if notify:
        print("App temp directory: {}".format(app_data))
    return app_data


def rreplace(s: str, old: str, new: str, occurences):
    li = s.rsplit(old, occurences)
    return new.join(li)


def change_file_name(filepath, to):
    path, ext = os.path.splitext(filepath)
    filename = os.path.split(path)[-1]
    new_path = rreplace(filepath, filename, to, -1)
    return new_path


def str_to_bool(value: str) -> bool:
    return value.lower() in ["true", "t", "1", "yes""y"]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
