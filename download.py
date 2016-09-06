import os

import requests
import hashlib
import win32api

from tinydb import TinyDB, Query

db = TinyDB('db.json')

tempdir = r'temp'
printdir = r'print'


def clean_dir(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def make_or_clean_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        clean_dir(path)


def download_file(fileurl, f):
    r = requests.get(fileurl, stream=True)

    with open(f, 'wb') as fd:
        for chunk in r.iter_content(1024):
            fd.write(chunk)


def hash_file(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    print(hasher.hexdigest())
    return hasher.hexdigest()


def should_print_entry(newhash, url):
    printme = False
    entry = Query()
    result = db.search(entry.url == url)
    if not result:
        # add new one
        print("new file")
        db.insert({'url': url, 'md5': newhash})
        printme = True
    elif len(result) == 1:
        # compare hashes of existing one
        if result[0]['md5'] == newhash:
            print("old file")
        else:
            print("update file")
            # update entry
            db.update({'md5': newhash}, entry.url == url)
            printme = True
    else:
        print("error: more than one element found")
    return printme


# TODO
def print_files():
    for the_file in os.listdir(printdir):
        printpath = os.path.abspath(os.path.join(printdir, the_file))
        print(printpath)
        win32api.ShellExecute(0, "print", printpath, None, ".", 0)


def main():
    # start here
    make_or_clean_dir(tempdir)
    make_or_clean_dir(printdir)

    with open('input.txt') as inputfile:
        urls = inputfile.read().splitlines()
    for url in urls:
        filename = url.split(sep='/')[-1]
        tempfile = os.path.join(tempdir, filename)

        download_file(url, tempfile)
        newhash = hash_file(tempfile)
        # search for existing entry
        printfile = should_print_entry(newhash, url)
        if printfile:
            os.rename(tempfile, os.path.join(printdir, filename))
    print_files()


if __name__ == "__main__":
    main()

print(db.all())
