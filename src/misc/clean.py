import os, zipfile, re
from src.misc.misc import (
    rename_remove_move,
    parse_chapter_input,
    zip_files 
)


def extract_all(file):
    with zipfile.ZipFile(file) as z:
        z.extractall()


def get_all_file_paths(directory):
    file_paths = []

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


def delete(folder: str, first: bool):
    files = get_all_file_paths(folder)
    if first:
        os.remove(files[0])
    else:
        os.remove(files[-1])
    

def type_one():
    manga_name = input("Manga name: ").strip()
    chapters = parse_chapter_input(input("Chapters: ").strip())
    first = int(input("First or last: "))

    for chapter in chapters:
        if chapter.is_integer():
            chap_num = int(chapter)
        else:
            chap_num = chapter
        file = f'{manga_name}/{manga_name} {chap_num} (Digital).cbz'

        extract_all(file)
        delete(f"{manga_name} {chap_num} (Digital)", True if first else False)
        zip_files(f"{manga_name} {chap_num} (Digital)")
        rename_remove_move(f"{manga_name} {chap_num} (Digital)", f"{manga_name}")


def type_two():
    manga_name = input("Manga name: ").strip()
    first = int(input("First or last: "))
    files = get_all_file_paths(manga_name)

    for file in files:
        res = re.search(r".+\\.+\s([\d\.]+)\s\(\w+\)\.cb[zr]", file)

        if res:
            extract_all(file)
            delete(f"{manga_name} {res.group(1)} (Digital)", True if first else False)
            zip_files(f"{manga_name} {res.group(1)} (Digital)")
            rename_remove_move(f"{manga_name} {res.group(1)} (Digital)", f"{manga_name}")


def main():
    # type_two()
    pass


if __name__ == "__main__":
    main()
