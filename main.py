import os
import random
from pathlib import Path
from typing import List
from urllib.parse import unquote, urlparse

import requests
from dotenv import load_dotenv

VK_API_URL = "https://api.vk.com/method"


def get_comics_id() -> int:
    url = f"https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_id = response.json()["num"]
    return random.randint(1, last_id)


def get_comics(comics_id: int) -> dict:
    url = f"https://xkcd.com/{comics_id}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()

    return comics


def save_comics(img_url: str) -> str:
    file_path = urlparse(unquote(img_url)).path
    _, filename = os.path.split(file_path)
    file_path = f"{filename}"

    response = requests.get(img_url)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def delete_comics(file_path: str) -> None:
    Path(file_path).unlink(missing_ok=True)


def get_vk_photo_url(
    access_token: str, group_id: str, api_version: str = "5.131"
) -> str:
    url = f"{VK_API_URL}/photos.getWallUploadServer"
    params = {
        "access_token": access_token,
        "group_id": group_id,
        "v": api_version,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    img_vk = response.json()
    return img_vk["response"]["upload_url"]


def send_vk_img(vk_url: str, file_path: str) -> dict:
    with open(file_path, "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(vk_url, files=files)
        response.raise_for_status()

        return response.json()


def save_vk_img(
    photo_vk_data: dict, access_token: str, group_id: str, api_version: str = "5.131"
) -> List:
    url = f"{VK_API_URL}/photos.saveWallPhoto"
    params = photo_vk_data.copy()
    params.update(
        {
            "access_token": access_token,
            "group_id": group_id,
            "v": api_version,
        }
    )
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["response"]


def post_comics_vk(
    title: str,
    vk_img: List,
    access_token: str,
    group_id: str,
    api_version: str = "5.131",
) -> str:
    url = f"{VK_API_URL}/wall.post"
    params = {
        "access_token": access_token,
        "v": api_version,
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": title,
        "attachments": f"photo{vk_img[0]['owner_id']}_{vk_img[0]['id']}",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["response"]["post_id"]


if __name__ == "__main__":
    load_dotenv()
    vk_access_token = os.getenv("VK_APP_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    comics_id = get_comics_id()
    comics = get_comics(comics_id)
    file_path = save_comics(comics["img"])

    url_for_img = get_vk_photo_url(vk_access_token, vk_group_id)
    img_vk_data = send_vk_img(url_for_img, file_path)
    delete_comics(file_path)
    img_saved = save_vk_img(img_vk_data, vk_access_token, vk_group_id)
    post_id = post_comics_vk(comics["alt"], img_saved, vk_access_token, vk_group_id)
    print(f"Comics '{comics['title']}' posted with ID :: {post_id}")
