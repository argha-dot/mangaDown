import os, zipfile, re, shutil
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


def delete(folder: str, files: str):
    file_paths = get_all_file_paths(folder)
    _files = list(map(int, files.split(":")))

    if len(_files) == 2:
        for f in file_paths[_files[0] - 1: _files[1]]:
            os.remove(f)
    elif len(_files) == 1:
        os.remove(file_paths[_files[0]])
    

def type_one():
    manga_name = input("Manga name: ").strip()
    chapters = parse_chapter_input(input("Chapters: ").strip())
    first = input("Pages to delete (index starts from 0, and use -1 for last page): ")

    for chapter in chapters:
        if chapter.is_integer():
            chap_num = int(chapter)
        else:
            chap_num = chapter

        if os.path.exists(f"{manga_name}/{manga_name} {chap_num} (Digital).cbz"):
            file = f'{manga_name} {chap_num} (Digital)'
        elif os.path.exists(os.path.join(manga_name, f"{manga_name} {chap_num} (2021) (Digital).cbz")):
            file = f'{manga_name} {chap_num} (2021) (Digital)'
        else:
            raise Exception( "File Not Found" )

        extract_all(f"{manga_name}/{ file }.cbz")
        # delete(file, "1:1" if first else "-1")
        delete(file, first.replace("..", ":"))
        zip_files(file)
        rename_remove_move(file, f"{manga_name}")


def type_two():
    manga_name = input("Manga name: ").strip()
    first = int(input("First or last: "))
    files = get_all_file_paths(manga_name)

    for file in files:
        res = re.search(r".+\\.+\s([\d\.]+)\s\(\w+\)\.cb[zr]", file)

        if res:
            extract_all(file)
            if os.path.exists(f"{manga_name} {res.group(1)} (Digital)"):
                delete(f"{manga_name} {res.group(1)} (Digital)", "1" if first else "-1")
                zip_files(f"{manga_name} {res.group(1)} (Digital)")
                rename_remove_move(f"{manga_name} {res.group(1)} (Digital)", f"{manga_name}")

            elif os.path.exists(f"{manga_name} {res.group(1)} (2021) (Digital)"):
                delete(f"{manga_name} {res.group(1)} (2021) (Digital)", "1" if first else "-1")
                zip_files(f"{manga_name} {res.group(1)} (2021) (Digital)")
                rename_remove_move(f"{manga_name} {res.group(1)} (2021) (Digital)", f"{manga_name}")


def one_piece_color():
    try:
        while True:
            get_rid_of_cover()
    except KeyboardInterrupt:
        print("KE")


def get_rid_of_cover():
    manga_name = "One Piece"
    file_name = float( input("File Name: ") )
    volume_num = int(input("Volume Number: "))

    _pages_to_del = int(input("Pages to del [ chapter ]: "))
    pages_to_del = f"1..{_pages_to_del}"

    pages_to_get = int(input("Pages to get [ volume ]: "))

    chapter = int(file_name) if file_name.is_integer() else file_name

    chapter_number = f"{manga_name} {chapter} (Digital)"
    file_path = os.path.join(f"{manga_name}", f"{chapter_number}.cbz")

    if os.path.exists(file_path):
        print("hello")
        extract_all(file_path)
        delete(chapter_number, pages_to_del.replace("..", ":"))
        # zip_files(f"{manga_name} {chapter} (Digital)")
        # rename_remove_move(f"{manga_name} {chapter} (Digital)", f"{manga_name}")

    v_folder_name = f"{manga_name} - Volume {volume_num}"
    v_file_path = os.path.join(f"{manga_name}", f"{v_folder_name}.cbz")

    if not os.path.exists(v_file_path):
        v_folder_name = f"{manga_name} - Volume 0{volume_num}"
        v_file_path = os.path.join(f"{manga_name}", f"{v_folder_name}.cbz")


    print(v_file_path)
    if os.path.exists(v_file_path):
        extract_all(v_file_path)
        _v_name = f"One Piece - Volume 00{volume_num}"
        if not os.path.exists(_v_name):
            _v_name = f"One Piece - Volume 000{volume_num}"

        files = get_all_file_paths(_v_name)
        os.makedirs("_cover", exist_ok=True)
        for f in files[0: pages_to_get]:
            shutil.copy(f, "_cover")

        shutil.move(f"_cover", chapter_number)
        zip_files(chapter_number)
        rename_remove_move(f"{chapter_number}", f"{manga_name}")
        shutil.rmtree(_v_name)



def main():
    type_one()
    # type_two()
    # one_piece_color()
    pass


if __name__ == "__main__":
    main()
