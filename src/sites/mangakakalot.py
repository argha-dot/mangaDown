import os, sys, re

from requests import adapters, Session
from bs4 import BeautifulSoup
from bs4.element import Tag


from src.misc.misc import parse_chapter_input, zip_files, rename_remove_move, HEADERS
from src.misc.prompt import prompt

def main():
    answers = prompt()

    get_every(
        url=answers.url,
        chapters=answers.chapters,
        manga_name=answers.manga_name
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)

    s = Session()
    adapter = adapters.HTTPAdapter(max_retries=2)
    s.mount("https://", adapter)
    s.headers.update(HEADERS)

    chapter_urls = get_chapter_links(url, _range, s)
    print(chapter_urls)
    for chapter in chapter_urls:
        chapter_n = chapter['chapter']
        chapter_url = chapter['url']

        download_chapter(chapter_url, chapter_n, manga_name, s)


def get_chapter_links(manga_url: str, chapters: list[float], session: Session) -> list[dict]:
    r = session.get(manga_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    DOMAIN = re.findall(r"(https://[w|\d]{0,3}.[\w\d\.\-]+)", manga_url)[0]
    print(DOMAIN)
    chapter_urls: list[dict] = []

    try:
        chunk = soup.find('div', class_=re.compile("chapter-list"))
        if isinstance(chunk, Tag):
            for chapter in chapters:
                _ch = int(chapter) if float.is_integer(chapter) else chapter
                row = chunk.find('a', string=re.compile(f'Chapter {_ch}'))

                if isinstance(row, Tag):
                    if 'https://' in row['href']:
                        _url = row['href']
                    else:
                        _url = f"{ DOMAIN }{ row['href'] }"
                        pass
                    chapter_urls.append({
                        'chapter': chapter,
                        'url': _url
                    })
                else:
                    print(f"[CHAPTER MAY NOT EXIST]: {_ch}")

    except Exception as e:
        raise e

    return chapter_urls


def get_img_urls(chapter_url: str, session: Session) -> list[str]:
    r = session.get(chapter_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    tag = 'vung-doc'

    img_urls = []

    try:
        chunk = soup.find('div', class_=re.compile(tag)) # ['src']
        if isinstance(chunk, Tag):
            for tag in chunk.find_all('img'):
                # print(tag['src']) if tag.get( 'src' ) else print(tag['data-src'])
                if tag.get('src'):
                    img_urls.append(tag['src'])
                elif tag.get('data-src'):
                    img_urls.append(tag['data-src'])

                # img_urls.append(tag['data-src'])

    except Exception as e:
        print(f"[ ERROR OCCURRED: {chapter_url}: {e} ]")

    return img_urls


def download_chapter(chapter_url: str, chapter: float, manga_name: str, s: Session):
    if float.is_integer(chapter):
        point_chapter = False
        folder_name = f"{manga_name} {int(chapter)} (Digital)"
    else:
        point_chapter = True
        folder_name = f"{manga_name} {chapter} (Digital)"

    try:
        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)

        s.headers.update({
            "referer": re.findall(r"(https://[w|\d]{0,3}.[\w\d\.\-]+)", chapter_url)[0]
        })

        img_urls = get_img_urls(chapter_url, s)

        if len(img_urls) <= 0:
            print("CHAPTER MIGHT NOT EXIST")
            return

        loader = '|/-\\'


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
