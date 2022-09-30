import os, sys
import concurrent.futures
from functools import partial

from requests import adapters, Session

from src.misc.misc import (
    rename_remove_move,
    zip_files, 
    prompts, 
    parse_chapter_input, 
    HEADERS,
    LOADER
)


def main():
    answers = prompts()

    get_every(
        answers["url"],
        answers["chapters"],
        answers["manga_name"],
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)
    print(_range)

    s = Session()
    adapter = adapters.HTTPAdapter(max_retries=2)
    s.mount("https://", adapter)
    s.headers.update(HEADERS)
        
    for chapter in _range:
        download_chapter(url, chapter, manga_name, s)

    print(f"\t\tALL CHAPTERS DOWNLOADED")


def download_chapter(url: str, chapter: float, manga_name: str, s: Session):
    # total_pages: int = 0
    folder_name: str = ""

    if float.is_integer(chapter):
        point_chapter = False
        folder_name = f"{manga_name} {int(chapter)} (Digital)"
    else:
        point_chapter = True
        folder_name = f"{manga_name} {chapter} (Digital)"

    try:
        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)

        pages = [i for i in range(1, 1000)]
        cont = [ True ]

        loader_counter = [ 0 ]

        _get_page = partial(get_page, url, chapter, folder_name, s, point_chapter, loader_counter, cont)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                _get_page,
                pages
            )
        zip_files(folder_name)
        rename_remove_move(folder_name, manga_name)

        sys.stdout.write('\033[2K\033[1G')
        if loader_counter:
            print(f"[CHAPTER {chapter} DONE]: {loader_counter} pages")
        else:
            print(f"CHAPTER MAY NOT EXIST Chapter: {chapter}]")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, cleaning up...")
        sys.exit(0)


def get_page(url: str,
             chapter: float,
             folder_name: str,
             session: Session,
             point_chapter: bool,
             loader_counter: list[int],
             cont: list[bool],
             page: int) -> None:
    if cont[0]:
        if point_chapter:
            url_img = f"{url}{str(chapter)[0:-2].zfill(4)}.{str(chapter)[-1]}-{str(page).zfill(3)}.png"
        else:
            url_img = f"{url}{str(int(chapter)).zfill(4)}-{str(page).zfill(3)}.png"

        r = session.get(url_img)

        try:
            r.raise_for_status()
        except Exception:
            if page == 1:
                cont[0] = False
                return
            else:
                cont[0] = False
                return

        if point_chapter:
            file_name = f"{str(chapter).zfill(4)}_{str(page).zfill(3)}.png"
        else:
            file_name = f"{str(int(chapter)).zfill(4)}_{str(page).zfill(3)}.png"

        try:
            with open(os.path.join(folder_name, file_name), "wb") as f:
                f.write(r.content)
                print(f'CHAPTER: {chapter} [{LOADER[loader_counter[0] % len(LOADER)]}] {loader_counter[0]}\t', end="", flush=True)
                sys.stdout.write('\033[2K\033[1G')
                loader_counter[0] += 1

        except Exception as e:
            print(f"Couldn't write {file_name}, {e} occured!")
            sys.exit(1)

        return


if __name__ == "__main__":
    main()
