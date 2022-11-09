from functools import partial
import concurrent.futures
import os, sys
import requests
from requests import adapters
from requests import Session

from src.misc.misc import zip_files, rename_remove_move, parse_chapter_input, LOADER
from src.misc.prompt import prompt


def main():
    answers = prompt()

    get_every(
        url=answers.url,
        chapters=answers.chapters,
        manga_name=answers.manga_name,
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)

    if len(_range) > 100:
        print("No more than 100 chapters allowed, please break it up")
        return

    chapter_data = get_chapter_ids(url, _range)
        
    if len(chapter_data) <= 0:
        print("chapters may not exist")

    s = requests.Session()
    adapter = adapters.HTTPAdapter(max_retries=5)
    s.mount('https://', adapter)

    for _chapter in chapter_data:
        download_chapter(_chapter, manga_name, s)

    print(f"\t\tALL CHAPTERS DOWNLOADED")


def get_chapter_ids(url: str, chapters: list[float]) -> list[dict]:
    lang_content_ratings = f'limit={len(chapters)}&translatedLanguage[]=en&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic'
    base_url = f"https://api.mangadex.org/chapter?manga={url}&{lang_content_ratings}&"
    
    for chapter in chapters:
        chapter_url = "chapter[]="
        if float.is_integer(chapter):
            chapter_url += f"{int(chapter)}&"
        else:
            chapter_url += f"{str(chapter)}&"

        base_url += chapter_url

    r = requests.get(base_url)

    try:
        r.raise_for_status()
        r.json()
    except Exception as e:
        print(e)
        sys.exit()

    _data = r.json().get('data')
    data = []
    for chapter in _data:
        data.append({
            'chapter': chapter['attributes']['chapter'],
            'id': chapter['id']
        })


    return data


def get_page_urls(uid: str) -> list[str]:
    r = requests.get(f'https://api.mangadex.org/at-home/server/{uid}')
    try:
        r.raise_for_status()
        r.json()
    except Exception as e:
        raise e

    # print(f'https://api.mangadex.org/at-home/server/{uid}')

    _data = r.json()
    base_img_url: str = f"{_data['baseUrl']}/data/{_data['chapter']['hash']}"

    img_urls: list[str] = []
    for img in _data['chapter']['data']:
        img_urls.append(f'{base_img_url}/{img}') 

    # pprint.pprint(img_urls[0])
    return img_urls

def download_chapter(_chapter: dict, manga_name: str, s: Session):
    chapter = float(_chapter['chapter'])
    uid = _chapter['id']

    if float.is_integer(chapter):
        point_chapter = False
        folder_name = f"{manga_name} {int(chapter)} (Digital)"
    else:
        point_chapter = True
        folder_name = f"{manga_name} {chapter} (Digital)"

    try:
        os.makedirs(f"{folder_name}", exist_ok=True)
        os.makedirs(f"{manga_name}", exist_ok=True)

        img_urls = get_page_urls(uid)

        if len(img_urls) <= 0:
            print("CHAPTER MIGHT NOT EXIST")
            return

        # loader = '|/-\\'

        pages = [i + 1 for i in range(len(img_urls) + 1)]

        _get_page = partial(get_page, chapter, folder_name, s, point_chapter, img_urls)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                _get_page,
                pages
            )

        zip_files(folder_name)
        rename_remove_move(folder_name, manga_name)

        sys.stdout.write('\033[2K\033[1G')
        print(f"[CHAPTER {chapter} DONE]: {len(img_urls)} pages")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, cleaning up...")
        sys.exit(0)


def get_page( chapter: float,
            folder_name: str,
            s: Session,
            point_chapter: bool,
            img_urls: list[str],
            page: int,
        ) -> None:
    r = s.get(img_urls[page - 1])
    r.raise_for_status()

    if point_chapter:
        file_name = f"{str(chapter).zfill(4)}_{str(page + 1).zfill(3)}.png"
    else:
        file_name = f"{str(int(chapter)).zfill(4)}_{str(page + 1).zfill(3)}.png"
    
    try:
        with open(os.path.join(folder_name, file_name), "wb") as f:
            f.write(r.content)
            # print(f"[DONE] {file_name} ({page})", end="")
            print(f"CHAPTER: {chapter} [{LOADER[page % len(LOADER)]}] {page}/{len(img_urls)}", end="", flush=True)
            sys.stdout.write('\033[2K\033[1G')

    except Exception as e:
        print(f"\nCouldn't write, {e} occured")


if __name__ == "__main__":
    main()
