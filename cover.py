import zipfile, os, re, shutil
from src.misc.misc import (
    zip_files,
    rename_remove_move
)

def extract_all(file):
    with zipfile.ZipFile(file) as z:
        z.extractall()


def get_all_file_paths(directory) -> list[str]:
    file_paths = []

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


def main():
    manga_name = input("Manga Name: ").strip()

    try:
        while True:
            chapter = float(input("Chapter: "))
            chapter = int(chapter) if chapter.is_integer() else chapter
            cover_path = input("Image Path: ").strip()

            print(chapter)

            files = get_all_file_paths(manga_name)
            print(files)

            for f in files:
                res = re.search(rf".+\\.+\s{chapter}\s\(\w+\)\.cb[zr]", f)
                if res:
                    print(f)

                    extract_all(f)

                    img_folder_name = f.split("\\")[-1][0:-4]
                    img_files = get_all_file_paths(img_folder_name)

                    os.remove(img_files[0])
                    shutil.move(f"{ cover_path }.jpg", img_folder_name)

                    zip_files(img_folder_name)
                    rename_remove_move(img_folder_name, f"{manga_name}")

    except KeyboardInterrupt:
        print("KI")


if __name__ == "__main__":
    main()
