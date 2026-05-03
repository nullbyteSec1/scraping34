# 🕷️ scraping34

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/badge/pypi-1.0.1-blue.svg)](https://pypi.org)

A lightweight and reusable Python library + CLI tool for scraping images from rule34.gg.

---

# ✨ Features

- 📦 Simple Python API
- 💻 Full CLI support
- 🖼️ Automatic image conversion
- ⚡ Fast hentai downloads  (videos and photos)
- 🧩 Built with clean and modular architecture
- 🌍 Cross-platform support:
  - Windows
  - Linux
  - macOS
  - Android (Termux)

---

# 📥 Installation

## Install from PyPI

```bash
pip install scraping34
```

---

# 🚀 CLI Usage

Basic usage:

```bash
scraping34 -c tsunade -o hentai.jpg -m photo
```

or:

```bash
python -m scraping34 -c hinata -o hinata.png -m photo
```

---

# 🐍 Python Library Usage

Basic example:

```python
from scraping34 import Scraping34

scraper = Scraping34(
    character="tsunade naruto",
    output_file="hentai.jpg",
    output_media="photo"
)

result = scraper.run()

print(result)
```

---

# 📘 API Reference

## `Scraping34(character, output_file)`

Creates a new scraper instance.

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `character` | `str` | Character/tag to search |
| `output_file` | `str` | Output image filename |
| `output_media` | `str` | output media format (video or photo) |
---

# ▶️ `.run()`

Executes the scraping pipeline:

### Returns

```python
str
```

Example:

```python
"[SUCCESS] Download completed: hentai.jpg"
```

---

# 🖼️ Supported Output Formats

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.gif`
- `.bmp`

Example:

```bash
scraping34 -c "rem" -o rem.webp
```

---

# 📱 Android / Termux Support

scraping34 works on Android using Termux.

## Install dependencies

```bash
pkg update
pkg install python
pip install scraping34
```

## Usage

```bash
scraping34 -c "mikasa" -o mikasa.jpg
```

---

# 🧪 Development Installation

Clone repository:

```bash
git clone https://github.com/nullbyteSec1/scraping34
```

Enter project folder:

```bash
cd scraping34
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
python scraping34.py -c "rem" -o rem.jpg
```

---

# 📦 Dependencies

- `httpx`
- `beautifulsoup4`
- `pillow`

---

# ⚠️ Disclaimer

This project is intended for educational and research purposes only.

Users are responsible for complying with local laws and the terms of service of accessed websites.

---

# 📄 License

MIT License © nullbyteSec1

---

# ⭐ Contributing

Pull requests, issues and suggestions are welcome.

If you like the project, consider leaving a star ⭐
