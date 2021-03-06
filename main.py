import logging
import os
import random
from pathlib import Path
from typing import List
from urllib.parse import unquote, urlparse

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(name)10s :: %(message)s",
)
log = logging.getLogger("comics")


VK_API_URL = "https://api.vk.com/method"


def get_ranadom_comics_id() -> int:
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
    file_path = filename

    response = requests.get(img_url)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def check_vk_response(response_data: dict):
    if "error" in response_data:
        raise requests.HTTPError(response_data["error"])


def get_vk_upload_url(
    access_token: str, group_id: str, api_version: str = "5.131"
) -> str:
    url = f"{VK_API_URL}/photos.getWallUploadServer"
    params = {
        "access_token": access_token,
        "group_id": group_id,
        "v": api_version,
    }
    response = requests.get(url, params=params)
    vk_img_upload_data = response.json()
    check_vk_response(vk_img_upload_data)
    return response.json()["response"]["upload_url"]


def send_vk_img(vk_url: str, file_path: str) -> dict:
    with open(file_path, "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(vk_url, files=files)
    response.raise_for_status()
    return response.json()


def save_vk_img(
    server, photo, vk_hash, access_token: str, group_id: str, api_version: str = "5.131"
) -> List:
    url = f"{VK_API_URL}/photos.saveWallPhoto"
    params = {
        "server": server,
        "photo": photo,
        "hash": vk_hash
    }
    params.update(
        {
            "access_token": access_token,
            "group_id": group_id,
            "v": api_version,
        }
    )
    response = requests.get(url, params=params)
    vk_img_data = response.json()
    check_vk_response(vk_img_data)
    return vk_img_data["response"]


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

    comics_id = get_ranadom_comics_id()
    comics = get_comics(comics_id)
    file_path = save_comics(comics["img"])
    try:
        url_for_img = get_vk_upload_url(vk_access_token, vk_group_id)
        img_data = send_vk_img(url_for_img, file_path)
        img_saved = save_vk_img(img_data["server"], img_data["photo"], img_data["hash"], vk_access_token, vk_group_id)
        post_id = post_comics_vk(comics["alt"], img_saved, vk_access_token, vk_group_id)
        log.info(f"Comics '{comics['title']}' posted with ID :: {post_id}")
    except (ValueError, requests.exceptions.HTTPError) as e:
        log.error(e)
    finally:
        Path(file_path).unlink(missing_ok=True)
