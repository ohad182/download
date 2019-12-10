from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class FileWatcher(PatternMatchingEventHandler):
    def __init__(self, patterns="*", ignore_patterns="",
                 ignore_directories=True, case_sensitive=False):
        super(FileWatcher, self).__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                                          ignore_directories=ignore_directories, case_sensitive=case_sensitive)


def create_fs_observer(download_dir):
    def on_created(event):
        pass
        # print(f"{event.src_path} has been created!")

    def on_deleted(event):
        pass
        # print(f"{event.src_path} has been deleted")

    def on_modified(event):
        pass
        # print(f"{event.src_path} has been modified")

    def on_moved(event):
        pass
        # print(f"{event.src_path} moved to {event.dest_path}")

    observer = Observer()
    fs_watcher = FileWatcher()
    fs_watcher.on_created = on_created
    fs_watcher.on_deleted = on_deleted
    fs_watcher.on_modified = on_modified
    fs_watcher.on_moved = on_moved

    observer.schedule(fs_watcher, download_dir)
    return observer
# fs_thread = threading.Thread(target=lambda: observer.start())
# fs_thread.setDaemon(True)
# observer = create_fs_observer(report.app_temp_directory)
# fs_thread.start()
# fs_thread.join()
