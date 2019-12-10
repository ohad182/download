from chardet.universaldetector import UniversalDetector

detector = UniversalDetector()
targetFormat = 'utf-8'


def readlines(filepath: str):
    lines = []
    try:
        codec = get_encoding_type(filepath)
        with open(filepath, 'r', encoding=codec) as f:
            lines = f.readlines()
    except UnicodeEncodeError as e:
        print(e)

    return lines


def get_encoding_type(file_path: str):
    detector.reset()
    with open(file_path, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    print(file_path, detector.result['encoding'])
    return detector.result['encoding']
