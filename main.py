import sys
from os import makedirs, sep
from os.path import exists
from re import findall

from requests import get

json_header = {"accept": "application/json", "referer": "https://www.pixiv.net", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
image_header = json_header.copy()
image_header['accept'] = "image/*"
user_cookies = {}


def getInfo(user_id: str, offset: int, limit: int, languages: str = "zh") -> dict:
    req = get(
        url=f"https://www.pixiv.net/ajax/user/{user_id}/illusts/bookmarks?tag=&offset={offset}&limit={limit}&rest=show&lang={languages}",
        headers=json_header, cookies=user_cookies)
    return req.json()


def handleString(string: str) -> str:
    return string.replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(" ", "")


def download_image(url: str, path: str) -> None:
    suffix_list = ["jpg", "png", "gif", "jpeg", "webp"]
    for suffix in suffix_list:
        req = get(url=f"{url}.{suffix}", headers=image_header)
        if req.status_code == 200:
            suffix = req.headers["Content-Type"].split("/")[-1]
            page = url[url.index('_p'):]
            with open(handleString(f"{path}{page}.{suffix}"), "wb") as f:
                f.write(req.content)
            break


def is_exist_dirs(dir_path: str) -> None:
    if not exists(dir_path):
        makedirs(dir_path)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python main.py user_id cookies")
        exit(1)
    else:
        user_cookies["user_id"] = sys.argv[1]
        user_cookies["PHPSESSID"] = sys.argv[2]
    is_exist_dirs("pixiv")
    b = getInfo(user_cookies["user_id"], 0, 48)
    total = b["body"]["total"]
    number = total // 48
    residue = total % 48
    for i in range(number):
        d = getInfo(user_cookies["user_id"], i * 48, 48)
        for j in d["body"]["works"]:
            print(f"https://www.pixiv.net/artworks/{j['id']} {j['title']} {j['url']}")
            for n in range(j["pageCount"]):
                a = findall("https://i.pximg.net/c/250x250_80_a2/.*/img/(.*)_p0_.*1200.jpg", j["url"])
                download_image(f"https://i.pximg.net/img-original/img/{a[0]}_p{n}", f"pixiv{sep}{j['title']}")
