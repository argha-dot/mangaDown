import os, sys, shutil
import requests
from requests import adapters

from misc import rename_remove_move, zip_files, prompts, parse_chapter_input, HEADERS


def main():
    answers = prompts()

    get_every(
        answers["url"],
        answers["chapters"],
        answers["manga_name"],
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)
    # print(_range)

    for chapter in _range:
        download_chapter(url, chapter, manga_name)

    print(f"\t\tALL CHAPTERS DOWNLOADED")


def download_chapter(url: str, chapter: float, manga_name: str):
    total_pages: int = 0
    folder_name: str = ""

    if float.is_integer(chapter):
        point_chapters = False
        folder_name = f"{manga_name} {int(chapter)} (Digital)"
    else:
        point_chapters = True
        folder_name = f"{manga_name} {chapter} (Digital)"

    try:
        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)
        loader = '|/-\\'

        s = requests.Session()
        adapter = adapters.HTTPAdapter(max_retries=5)
        s.mount('https://', adapter)
        s.headers.update(HEADERS)

        for i in range(1, 100000 + 1):
            if point_chapters:
                url_img = f"{url}{str(chapter)[0:-2].zfill(4)}.{str(chapter)[-1]}-{str(i).zfill(3)}.png"
            else:
                url_img = f"{url}{str(int(chapter)).zfill(4)}-{str(i).zfill(3)}.png"

            r = s.get(url_img)

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
                    # print(f"[DONE] {file_name} ({url_img})")
                    print(f"CHAPTER: {chapter} [{loader[i % len(loader)]}] {i}", end="", flush=True)
                    sys.stdout.write('\033[2K\033[1G')

            except Exception as e:
                print(f"Couldn't write {file_name}, {e} occured!")
                sys.exit(1)

        zip_files(folder_name)
        rename_remove_move(folder_name, manga_name)

        sys.stdout.write('\033[2K\033[1G')
        print(f"[CHAPTER {chapter} DONE]: {total_pages - 1} pages")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, cleaning up...")
        sys.exit(0)


if __name__ == "__main__":
    main()
