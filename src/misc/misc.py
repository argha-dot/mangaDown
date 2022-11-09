import os, shutil
from zipfile import ZipFile

LOADER = '|/-\\'

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "referer": "https://manga4life.com/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "sec-gpc": '1',
    "upgrade-insecure-requests": "1",
    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
}

DOMAINS = {
    'https://ww2.mangakakalot.tv': 'vung-doc',
    'https://readmanganato.com': 'chapter-reader'
}


def parse_chapter_input(chapters: str) -> list[float]:
    _range: list[float] = []
    strings: list[str] = []

    for _str in chapters.split():
        if ".." in _str:
            nums = _str.split("..")
            strings.extend([str(x) for x in range(int(nums[0]), int(nums[1]) + 1)])
        else:
            strings.append(_str)

    _range.extend(list(map(float, strings)))

    return _range


# def _prompts():
#     print("Use '..' for ranges, and ' ' to indicate a chapter or a range\n")
#
#     try:
#         url = input("Link: ").strip()
#         chapters = input("The Chapters: ").strip()
#         manga_name = input("Manga Name: ").strip()
#     except KeyboardInterrupt:
#         sys.exit(0)
#
#     return {
#         "url": url,
#         "chapters": chapters,
#         "manga_name": manga_name,
#     }
#
#
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

