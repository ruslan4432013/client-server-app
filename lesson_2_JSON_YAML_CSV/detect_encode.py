import chardet


def get_encoding(file):
    with open(file, 'rb') as file:
        file_text = file.read()
        encoding = chardet.detect(file_text)['encoding']
        return encoding
