from __future__ import annotations

import aiohttp

DISK_API = "https://cloud-api.yandex.net/v1/disk/resources"


async def get_upload_link(session: aiohttp.ClientSession, token: str, path: str) -> str:
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": path, "overwrite": "true"}

    async with session.get(f"{DISK_API}/upload", headers=headers, params=params) as resp:
        data = await resp.json(content_type=None)
        if resp.status >= 400:
            raise RuntimeError(f"YaDisk upload-link error {resp.status}: {data}")
        return data["href"]

async def ensure_dir(session: aiohttp.ClientSession, token: str, path: str) -> None:
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": path}

    async with session.put(DISK_API, headers=headers, params=params) as resp:
        if resp.status in (201, 409):
            return
        data = await resp.text()
        raise RuntimeError(f"YaDisk mkdir error {resp.status}: {data}")


async def upload(session: aiohttp.ClientSession, href: str, file_bytes: bytes) -> None:
    async with session.put(href, data=file_bytes) as resp:
        if resp.status >= 400:
            text = await resp.text()
            raise RuntimeError(f"YaDisk upload error {resp.status}: {text}")


async def get_download_link(session: aiohttp.ClientSession, token: str, path: str) -> str:
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": path}

    async with session.get(f"{DISK_API}/download", headers=headers, params=params) as resp:
        data = await resp.json(content_type=None)
        if resp.status >= 400:
            raise RuntimeError(f"YaDisk download-link error {resp.status}: {data}")
        return data["href"]