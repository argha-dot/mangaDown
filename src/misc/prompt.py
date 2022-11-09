from dataclasses import dataclass
import sys

@dataclass
class Prompt:
    url: str
    manga_name: str
    chapters: str

def prompt_user() -> Prompt:
    print("Use '..' for ranges, and ' ' to indicate a chapter or a range\n")

    try:
        url = input("Link: ").strip()
        chapters = input("The Chapters: ").strip()
        manga_name = input("Manga Name: ").strip()
    except KeyboardInterrupt:
        sys.exit(0)

    return Prompt(
        url=url,
        manga_name=manga_name,
        chapters=chapters
    )

def prompt() -> Prompt:
    answers = prompt_user()
    manga_name = answers.manga_name
    url = answers.url

    if manga_name == "":
        manga_name = url[0:-1].split("/")[-1].replace("-", " ") if url.endswith("/") else url.split("/")[-1].replace("-", " ")
    print(manga_name)

    return Prompt(
        url=url,
        manga_name=manga_name,
        chapters=answers.chapters
    )
