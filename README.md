#  🕷️ scraping34 
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org)

Scraping and a reusable library for scraping hentai rule34 in Python

## install
Install via pip (recommended)
```bash
pip install scraping34
```

## how to use 
basic code
```python
from scraping34 import Scraping34

scraping = Scraping34("tsunade naruto","hentai.jpg") 
scraping.run()
```

the class Scraping34 will receive two arguments

Scraping34("character","outputfile")

the character and the character from which you want to obtain the images
outputfile and the name of the JPG file that the library will create

The .run method will query the APIs and download the data 
