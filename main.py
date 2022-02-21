from src.sites.manga4life import main as manga4life
from src.sites.mangadex import main as mangadex
from src.sites.mangakakalot import main as mangakakalot


def main():
    site: str = ""
    while True:
        try:
            site = input("Manga4Life[M4L], MangaDex[MD], MangaKaKalot[MKK]: ").strip().upper()
        except KeyboardInterrupt:
            break
        if site not in ["M4L", "MD", "MKK"]: 
            print("M4L or, MD or MKK")
            continue
        else:
            break

    if site == "M4L":
        manga4life()
    elif site == "MD":
        mangadex()
    elif site == "MKK":
        mangakakalot()


if __name__ == "__main__":
    main()
