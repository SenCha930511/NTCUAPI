from ntcu_api import Ntcu_api
from bs4 import BeautifulSoup

ntcu_api = Ntcu_api("ACS111132", "ssss")

r = ntcu_api.getAllGrd()

print(r)
