import os, sys
import requests
from requests import adapters

from src.misc.misc import prompts, zip_files, rename_remove_move, parse_chapter_input


def main():
    answers = prompts()

    get_every(
        answers["url"],
        answers["chapters"],
        answers["manga_name"],
    )


def get_every(url: str, chapters: str, manga_name: str):
    _range = parse_chapter_input(chapters)

    if len(_range) > 100:
        print("No more than 100 chapters allowed, please break it up")
        return

    chapter_data = get_chapter_ids(url, _range)
        
    if len(chapter_data) <= 0:
        print("chapters may not exist")

    for _chapter in chapter_data:
        download_chapter(_chapter, manga_name)

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

def download_chapter(_chapter: dict, manga_name: str):
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

        loader = '|/-\\'

        s = requests.Session()
        adapter = adapters.HTTPAdapter(max_retries=5)
        s.mount('https://', adapter)

        for i, url in enumerate(img_urls):
            r = s.get(url)
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