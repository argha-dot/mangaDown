import os, sys, shutil
from datetime import date

import requests

from misc import rename_remove_move, zip_files, prompts


def download_chapter(url, chapter, manga_name):
    total_pages = 0
    folder_name = ""

    if float.is_integer(chapter):
        point_chapters = False
        folder_name = f"{manga_name} {int(chapter)} ({date.today().year}) (Digital)"
    else:
        point_chapters = True
        folder_name = f"{manga_name} {chapter} ({date.today().year}) (Digital)"

    try:
        print("[", end="", flush=True)

        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)

        for i in range(1, 100000 + 1):
            if point_chapters:
                url_img = f"{url}{str(chapter)[0:-2].zfill(4)}.{str(chapter)[-1]}-{str(i).zfill(3)}.png"
            else:
                url_img = f"{url}{str(int(chapter)).zfill(4)}-{str(i).zfill(3)}.png"


            r = requests.get(url_img)

            try:
                r.raise_for_status()
            except Exception:
                if i == 1:
                    shutil.rmtree(folder_name)
                    print(f"CHAPTER MAY NOT EXIST Chapter: {chapter}]")
                    return
                else:
                    total_pages = i
                    break

            if point_chapters:
                file_name = f"{str(chapter).zfill(4)}_{str(i).zfill(3)}.png"
            else:
                file_name = f"{str(int(chapter)).zfill(4)}_{str(i).zfill(3)}.png"

            try:
                with open(os.path.join(folder_name, file_name), "wb") as f:
                    f.write(r.content)
                    print("=", end="", flush=True)
                    # print(f"[DONE] {file_name} ({url_img})")

            except Exception:
                print(f"Couldn't write {file_name}, occured!")

        zip_files(folder_name)
        rename_remove_move(folder_name, manga_name)

        sys.stdout.write('\033[2K\033[1G')
        print(f"[CHAPTER {chapter} DONE]: {total_pages - 1} pages")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, cleaning up...")
        sys.exit(1)


def get_every(url: str, chapters: str, manga_name: str):
    _range: list[float] = []    
    strings: list[str] = []

    for _str in chapters.split():
        if ".." in _str:
            nums = _str.split("..")
            strings.extend([str(x) for x in range(int(nums[0]), int(nums[1]) + 1)])
        else:
            strings.append(_str)

    _range.extend(list(map(float, strings)))
    # print(_range)

    for chapter in _range:
        download_chapter(url, chapter, manga_name)

    print(f"\t\tALL CHAPTERS DOWNLOADED")


def main():
    answers = prompts()

    get_every(
        answers["url"],
        answers["chapters"],
        answers["manga_name"],
    )


if __name__ == "__main__":
    main()
