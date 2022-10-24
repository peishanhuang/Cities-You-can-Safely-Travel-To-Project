****Instruction for Final.py****

This program will have two mode:
1. Run without arguments
	This will scrape all data
	and print all DataFrames

2. Run with '--static'
	This will read data (csv files)
	and print all DataFrames

The program will use these libraries:
import sys
import time
import json
import requests
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup

Notes:
1. Please install all libraries before run 
this program
2. While running static mode, please make
sure: a folder contain correct csv files 
exists (folder name can change, csv cannot)
3. Weather API has 2000 visits limit per day