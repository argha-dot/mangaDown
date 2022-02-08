import os, sys, re

import requests
from requests import adapters
from bs4 import BeautifulSoup
from bs4.element import Tag

from misc import prompts, parse_chapter_input, zip_files, rename_remove_move

def main():
    answers = prompts()

    get_every(
        answers["url"],
        answers["chapters"],
        answers["manga_name"],
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)

    chapter_urls = get_chapter_links(url, _range)
    for chapter in chapter_urls:
        chapter_n = chapter['chapter']
        chapter_url = chapter['url']

        download_chapter(chapter_url, chapter_n, manga_name)


def get_chapter_links(manga_url: str, chapters: list[float]) -> list[dict]:
    r = requests.get(manga_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    DOMAIN = 'https://ww1.mangakakalot.tv'
    chapter_urls: list[dict] = []

    try:
        chunk = soup.find('div', attrs={ 'class': 'chapter-list' })
        if isinstance(chunk, Tag):
            for chapter in chapters:
                _ch = int(chapter) if float.is_integer(chapter) else chapter
                row = chunk.find('a', string=re.compile(f'Chapter {_ch}'))
                # print(f"{ DOMAIN }{ row['href'] if isinstance(row, Tag) else None }")
                if isinstance(row, Tag):
                    chapter_urls.append({
                        'chapter': chapter,
                        'url': f"{ DOMAIN }{ row['href'] }"
                    })
                else:
                    print(f"[CHAPTER MAY NOT EXIST]: {_ch}")

    except Exception as e:
        raise e

    return chapter_urls


def get_img_urls(chapter_url: str) -> list[str]:
    r = requests.get(chapter_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    img_urls = []

    try:
        chunk = soup.find('div', id='vungdoc') # ['src']
        if isinstance(chunk, Tag):
            for tag in chunk.find_all('img'):
                img_urls.append(tag['data-src'])

    except Exception:
        print(f"[ ERROR OCCURRED: {chapter_url} ]")

    return img_urls


def download_chapter(chapter_url: str, chapter: float, manga_name: str):
    if float.is_integer(chapter):
        point_chapter = False
        folder_name = f"{manga_name} {int(chapter)} (Digital)"
    else:
        point_chapter = True
        folder_name = f"{manga_name} {chapter} (Digital)"

    try:
        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)

        img_urls = get_img_urls(chapter_url)

        if len(img_urls) <= 0:
            print("CHAPTER MIGHT NOT EXIST")
            return

        loader = '|/-\\'

        s = requests.Session()
        adapter = adapters.HTTPAdapter(max_retries=5)
        s.mount('https://', adapter)

        for i, page_url in enumerate(img_urls):
            r = s.get(page_url)
            r.raise_for_status()

            if point_chapter:
                file_name = f"{str(chapter).zfill(4)}_{str(i + 1).zfill(3)}.png"
            else:
                file_name = f"{str(int(chapter)).zfill(4)}_{str(i + 1).zfill(3)}.png"
            
            try:
                with open(os.path.join(folder_name, file_name), "wb") as f:
                    f.write(r.content)
                    # print(f"[DONE] {file_name} ({url})")
                    print(f"CHAPTER: {chapter} [{loader[i % len(loader)]}] {i}/{len(img_urls)}", end="", flush=True)
                    sys.stdout.write('\033[2K\033[1G')

            except Exception as e:
                print(f"\nCouldn't write, {e} occured")

        zip_files(folder_name)
        rename_remove_move(folder_name, manga_name)

        sys.stdout.write('\033[2K\033[1G')
        print(f"[CHAPTER {chapter} DONE]: {len(img_urls)} pages")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, cleaning up...")
        sys.exit(0)


if __name__ == "__main__":
    main()
