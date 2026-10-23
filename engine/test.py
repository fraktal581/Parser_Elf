import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime
import os
import xlsxwriter
#import PySimpleGUI as sg
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


list = ['1', '2', '3, 2', '4']
elt =str(list[len(list)-2:-1])
print(elt)
print(elt.find('2'))


list_1 = []
print(len(list_1))


