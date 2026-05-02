#!/usr/bin/env python3

'''
src/scraping34.py

Core module for scraping images from rule34.gg.

Created by: nullbyteSec1
License: MIT
Github: https://github.com/nullbyteSec1/scraping34
'''

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from PIL import Image


class DependencyError(Exception):
    """Raised when a required dependency is missing."""


class DependencyInstaller:
    """
    Handles dependency detection and installation.
    """

    # =========================================================
    # UTILS
    # =========================================================

    @staticmethod
    def command_exists(command: str) -> bool:
        return shutil.which(command) is not None

    @staticmethod
    def is_termux() -> bool:
        """
        Detects Termux environment.
        """

        return (
            "com.termux" in os.environ.get("PREFIX", "")
            or Path("/data/data/com.termux").exists()
        )

    @staticmethod
    def ensure_pillow() -> None:
        """
        Ensures Pillow is installed.
        """

        try:
            import PIL  # noqa: F401

        except ImportError:
            raise DependencyError(
                "Pillow is not installed.\n"
                "Install using:\n"
                "  pip install pillow"
            )

    # =========================================================
    # OPTIONAL FFMPEG DETECTION
    # =========================================================

    @staticmethod
    def find_ffmpeg() -> str | None:
        """
        Attempts to locate ffmpeg executable.
        """

        ffmpeg = shutil.which("ffmpeg")

        if ffmpeg:
            return ffmpeg

        common_paths = []

        system = platform.system().lower()

        if system == "windows":
            common_paths.extend([
                Path(r"C:\Program Files\ffmpeg"),
                Path(r"C:\ffmpeg"),
                Path.home() / "scoop" / "apps",
            ])

        elif system == "linux":

            if DependencyInstaller.is_termux():
                common_paths.extend([
                    Path("/data/data/com.termux/files/usr/bin"),
                ])

            else:
                common_paths.extend([
                    Path("/usr/bin"),
                    Path("/usr/local/bin"),
                ])

        elif system == "darwin":
            common_paths.extend([
                Path("/opt/homebrew/bin"),
                Path("/usr/local/bin"),
            ])

        executable_name = (
            "ffmpeg.exe"
            if system == "windows"
            else "ffmpeg"
        )

        for base in common_paths:
            if not base.exists():
                continue

            executable = next(
                base.rglob(executable_name),
                None,
            )

            if executable:
                os.environ["PATH"] += (
                    os.pathsep + str(executable.parent)
                )

                return str(executable)

        return None


class Scraping34:
    BASE_URL = "https://rule34.gg"

    VALID_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
    }

    def __init__(
        self,
        character: str,
        output_file: str,
    ):
        self.character = character.strip()
        self.output_file = Path(output_file)

        self._validate_output_file()

        DependencyInstaller.ensure_pillow()

    # =========================================================
    # VALIDATION
    # =========================================================

    def _validate_output_file(self) -> None:
        """
        Ensures output file has a valid extension.
        """

        extension = self.output_file.suffix.lower()

        if extension not in self.VALID_EXTENSIONS:
            raise ValueError(
                "Output file must contain a valid extension.\n"
                "Examples:\n"
                "  image.jpg\n"
                "  image.png\n"
                "  image.webp"
            )

    # =========================================================
    # SCRAPING
    # =========================================================

    def _fetch_image_url(self) -> str:
        """
        Fetches first image URL.
        """

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
                f"{self.BASE_URL}/",
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

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        container = soup.find(
            "div",
            class_="media",
        )

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

    # =========================================================
    # DOWNLOAD
    # =========================================================

    @staticmethod
    def _download_image(
        image_url: str,
        temp_file: Path,
    ) -> None:
        """
        Downloads temporary image.
        """

        try:
            with httpx.stream(
                "GET",
                image_url,
                timeout=30,
                follow_redirects=True,
            ) as response:

                response.raise_for_status()

                with open(temp_file, "wb") as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Image download failed: {exc}"
            ) from exc

    # =========================================================
    # IMAGE CONVERSION
    # =========================================================

    @staticmethod
    def _convert_image(
        input_file: Path,
        output_file: Path,
    ) -> None:
        """
        Converts image using Pillow.
        """

        try:
            with Image.open(input_file) as image:

                # Pillow cannot save RGBA as JPEG directly
                if output_file.suffix.lower() in {
                    ".jpg",
                    ".jpeg",
                }:
                    image = image.convert("RGB")

                image.save(output_file)

        except Exception as exc:
            raise RuntimeError(
                f"Image conversion failed: {exc}"
            ) from exc

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def run(self) -> str:
        """
        Executes scraping pipeline.
        """

        image_url = self._fetch_image_url()

        print("[INFO] Image found:")
        print(f"       {image_url}")

        extension = (
            Path(image_url)
            .suffix
            .split("?")[0]
            .lower()
        )

        if not extension:
            extension = ".jpg"

        temp_file = Path(f"temp_image{extension}")

        try:
            self._download_image(
                image_url=image_url,
                temp_file=temp_file,
            )

            self._convert_image(
                input_file=temp_file,
                output_file=self.output_file,
            )

            return (
                "[SUCCESS] Download completed:\n"
                f"          {self.output_file}"
            )

        finally:
            if temp_file.exists():
                temp_file.unlink()

    # =========================================================
    # OPTIONAL FFMPEG INFO
    # =========================================================

    @staticmethod
    def show_ffmpeg_info() -> None:
        """
        Shows optional ffmpeg detection.
        """

        ffmpeg = DependencyInstaller.find_ffmpeg()

        if ffmpeg:
            print("[INFO] ffmpeg found:")
            print(f"       {ffmpeg}")

        else:
            print("[INFO] ffmpeg not found.")
            print("[INFO] Using Pillow backend.")


# =============================================================
# CLI
# =============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Downloads images from rule34.gg "
            "and converts using Pillow."
        )
    )

    parser.add_argument(
        "-c",
        "--character",
        required=True,
        help="Character/tag name",
    )

    parser.add_argument(
        "-o",
        "--outputfile",
        required=True,
        help="Output file path",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        Scraping34.show_ffmpeg_info()

        scraper = Scraping34(
            character=args.character,
            output_file=args.outputfile,
        )

        result = scraper.run()

        print(result)

    except DependencyError as exc:
        print(f"\n[DEPENDENCY ERROR]")
        print(exc)

        sys.exit(1)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

        sys.exit(0)

    except Exception as exc:
        print(f"\n[ERROR] {exc}")

        sys.exit(1)


if __name__ == "__main__":
    main()