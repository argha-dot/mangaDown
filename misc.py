import os, shutil
from zipfile import ZipFile


def prompts():
    print("Use '..' for ranges, and ' ' to indicate a chapter or a range\n")
    url = input("Link: ").strip()
    chapters = input("The Chapters: ").strip()
    manga_name = input("Manga Name: ").strip()

    return {
        "url": url,
        "chapters": chapters,
        "manga_name": manga_name,
    }


def get_all_file_paths(directory):
    file_paths = []

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


def rename_remove_move(folder_name, manga_name):
    os.rename(f"{folder_name}.zip", f"{folder_name}.cbz")
    # print("[FILE RENAMED]", f"{folder_name}.zip to {folder_name}.cbz")

    shutil.rmtree(folder_name)
    # print("[FOLDER REMOVED]", f"{folder_name}/")

    shutil.move(f"{folder_name}.cbz", os.path.join(f"{manga_name}", f"{folder_name}.cbz"))


def zip_files(folder_name):
    file_paths = get_all_file_paths(folder_name)
    with ZipFile(f"{folder_name}.zip", "w") as zip_file:
        for file in file_paths:
            zip_file.write(f"{file}")


