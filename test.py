from ntcu_api import Ntcu_api
from bs4 import BeautifulSoup

ntcu_api = Ntcu_api("ACS111132", "tim-930511")

r = ntcu_api.getAllCourses()

print(r)