from download.Downloader import Downloader
from common.exceptions import SiteErrorException

down = Downloader('https://www.sdarot.pm/')
# down.close()

down.connect()


# down.close_current_tab()
# down.open_new_tab('http://www.facebook.com')
# down.switch_tabs()
# down.close_current_tab()

def download():
    try:
        attempt = 1
        down.perform_search("דקסטר")
        down.select_season(2)
        down.select_episode(13)
        down.download_using_flash()
    except SiteErrorException as e:
        print('site error {}: {}'.format(attempt, e))
        attempt += 1
        down.refresh()
        download()


download()
