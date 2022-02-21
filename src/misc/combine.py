import os, shutil, zipfile, re


def get_all_file_paths(directory):
    file_paths = []

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


def delete_folder(folder_name):
    try:
        shutil.rmtree(folder_name)
    #         print("[FOLDER REMOVED]", f"{folder_name}/")
    except Exception as e:
        raise e


def move_em(folder_name):
    for folder in os.listdir(folder_name):
        if os.path.isdir(os.path.join(folder_name, folder)):
            file_names = os.listdir(os.path.join(folder_name, folder))

            for file_name in file_names:
                shutil.move(
                    os.path.join(folder_name, folder, file_name),
                    os.path.join(folder_name, file_name),
                )
            #             print(f"[FILES MOVED TO] {folder_name}")
            delete_folder(os.path.join(folder_name, folder))
    pass


def extract_all_files(file_list, folder_name):
    for file in file_list:
        try:
            with zipfile.ZipFile(file) as z:
                z.extractall(folder_name)
                print(f"[FILE EXTRACTED] {file}")
        except Exception as e:
            print(e)


def zip_em_up(folder):
    try:
        file_paths = get_all_file_paths(folder)
        with zipfile.ZipFile(f"{folder}.zip", "w") as zip_file:
            for file in file_paths:
                zip_file.write(f"{file}")

        print("[FILE ZIPPED]", f"{folder}.zip")
    except Exception as e:
        raise e


def rename_folder(folder_name):
    try:
        os.rename(f"{folder_name}.zip", f"{folder_name}.cbz")
        print("[FILE RENAMED]", f"{folder_name}.zip to {folder_name}.cbz")
    except Exception as e:
        raise e


def main():
    manga_name = input("Manga name: ")

    try:
        while True:
            num = input("Folder num: ").rjust(4, "0")
            start = float(input("Starting Chapter: "))
            end = float(input("Ending Chapter: "))

            folder_name = f"{manga_name} - Volume {num}"
            files = get_all_file_paths(f"{manga_name}")
            file_list = []

            for _, file in enumerate(files):
                res = re.search(r".+\\.+\s([\d\.]+)\s\(\w+\)\.cb[zr]", file)
                if res:
                    res = float(res.group(1))
                    if res >= start and res <= end:
                        file_list.append(file)
                else:
                    pass
                    # print(f"INVALID REGEX {file}")

            # pprint.pprint(file_list)

            extract_all_files(file_list, folder_name)
            # move_em(folder_name)
            zip_em_up(folder_name)
            rename_folder(folder_name)
            delete_folder(folder_name)
    except KeyboardInterrupt:
        print("[DONE]...")
        pass

    # delete_folder(f"{manga_name}")
    # os.makedirs(f"{manga_name}")


if __name__ == "__main__":
    main()
