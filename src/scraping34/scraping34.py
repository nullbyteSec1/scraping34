#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from PIL import Image


class Scraping34:
    BASE_URL_IMAGE = "https://rule34.gg"
    BASE_URL_VIDEO = "https://www.hentaigem.com"
    VALID_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
    }

    def __init__(self, character: str, output_file: str, output_media: str):
        self.character = character.strip()
        self.output_file = Path(output_file)
        self.output_media = output_media
        self._validate_output_file()

    def _validate_output_file(self) -> None:
        if self.output_media == "photo":
          extension = self.output_file.suffix.lower()

          if extension not in self.VALID_EXTENSIONS:
            raise ValueError(
                "Output file must contain a valid extension.\n"
                "Examples:\n"
                "  image.jpg\n"
                "  image.png\n"
                "  image.webp"
            )

    def _fetch_image_url(self) -> str:
        params = {
            "tags": self.character,
            "sort": "date_no",
            "exclude": "",
            "page": 1,
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            )
        }

        try:
            response = httpx.get(
                f"{self.BASE_URL_IMAGE}/",
                params=params,
                headers=headers,
                timeout=15,
                follow_redirects=True,
            )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Error accessing rule34.gg: {exc}"
            ) from exc

        soup = BeautifulSoup(response.text, "html.parser")
        container = soup.find("div", class_="media")

        if not container:
            raise RuntimeError(
                "No media container found."
            )

        image = container.find("img")

        if not image:
            raise RuntimeError(
                "No image found."
            )

        image_url = image.get("src")

        if not image_url:
            raise RuntimeError(
                "Invalid image URL."
            )

        return image_url

    def _fetch_video_url(self):
        request = httpx.get(f"https://www.hentaigem.com/search/{self.character}/")

        soup = BeautifulSoup(request.text, "html.parser")
        div = soup.find("div", class_="item")
        if div:
            a_element = div.find("a")
            if a_element:
                url = a_element.get("href")
                html_pageview = httpx.get(url)

        soup_p = BeautifulSoup(html_pageview, "html.parser")
        for script in soup_p.find_all("script"):
            if script.string and "ideo_url" in script.string:
                match = re.search(r"video_url:\s*'([^']+)'", script.string)
                if match:
                    url = match.group(1)
                    return url


    def _download_video(self, video_url: str, output_file: str):
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Encoding": "identity",
                "Range": "bytes=0-"
            }
            print("downloading your video...")
            with client.stream("GET", video_url, headers=headers) as response:
                response.raise_for_status()
                with open(output_file, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                    print("[*]download successfully")

    @staticmethod
    def _download_image(image_url: str, temp_file: Path) -> None:
        try:
            with httpx.stream("GET", image_url, timeout=30, follow_redirects=True) as response:
                response.raise_for_status()
                with open(temp_file, "wb") as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Image download failed: {exc}") from exc

    @staticmethod
    def _convert_image(input_file: Path, output_file: Path) -> None:
        try:
            with Image.open(input_file) as image:
                if output_file.suffix.lower() in {".jpg", ".jpeg"}:
                    image = image.convert("RGB")
                image.save(output_file)
        except Exception as exc:
            raise RuntimeError(f"Image conversion failed: {exc}") from exc

    def run(self):
        if self.output_media == "photo":
            image_url = self._fetch_image_url()
            print("[INFO] Image found:")
            print(f"       {image_url}")
            extension = (Path(image_url).suffix.split("?")[0].lower())
            if not extension:
                extension = ".jpg"
            temp_file = Path(f"temp_image{extension}")
            try:
                self._download_image(image_url=image_url, temp_file=temp_file)
                self._convert_image(input_file=temp_file, output_file=self.output_file)
                return (
                    "[SUCCESS] Download completed:\n"
                    f"          {self.output_file}"
                )
            finally:
                if temp_file.exists():
                    temp_file.unlink()
        if self.output_media == "video":
            video_url = self._fetch_video_url()
            print(video_url)
            if video_url:
                self._download_video(video_url, self.output_file)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--character", required=True, help="Character/tag name")
    parser.add_argument("-o", "--outputfile", required=True, help="Output file path")
    parser.add_argument("-m", "--outputmedia", required=True, help="output media type")
    return parser.parse_args()

def main():
    args = parse_args()
    try:
        scraper = Scraping34(
            character=args.character,
            output_file=args.outputfile,
            output_media=args.outputmedia
        )
        result = scraper.run()
        print(result)
    except Exception as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
