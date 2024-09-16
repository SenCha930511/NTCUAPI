import requests
import random
import recaptchaByPass
from bs4 import BeautifulSoup

class Ntcu_api():

    def __init__(self, account, password):
        self.domain = random.choice(["https://ecsa.ntcu.edu.tw", "https://ecsa.ntcu.edu.tw"])
        self.session = self.__getSession(account, password)  

    def __getSession(self, account, password):
        session, form_data = self.__getCrsf()
        session, form_data = self.__getCheckCodeData(session, form_data)
        session = self.__login(session, form_data, account, password)
        return session    
    
    def __getCrsf(self):
        session = requests.Session()
        page_response = session.get(self.domain, verify = False)

        soup = BeautifulSoup(page_response.text, "html.parser")

        csrf_token = soup.find("input", {"id": "csrf_token"})["value"]
        form_data = {
            "csrf_token": csrf_token
        }

        return session, form_data

    def __getCheckCodeData(self, session, form_data):
        check_url = self.domain + "/HttpRequest/Get_Check_Code.ashx"
        check_code_data = session.post(check_url, data = form_data, verify = False).json()

        code_image = check_code_data[0]["Code_Image"]
        form_data["Check_Code"] = recaptchaByPass.recaptchaByPass(code_image)
        form_data["MD5_EnCode"] = check_code_data[0]["MD5_EnCode"]
        form_data["SHA1_EnCode"] = check_code_data[0]["SHA1_EnCode"]

        return session, form_data

    def __login(self, session, form_data, account, password):
        form_data["Model"] = "Do_Login"
        form_data["Type"] = "0"
        form_data["User_Account"] = account
        form_data["User_Password"] = password

        login_url = self.domain + "/login.aspx"
        login_response = session.post(login_url, data = form_data, verify = False).json()

        return session
    
    def __getClassOf(self):
        result_url = self.domain + "/STDWEB/Sel_Student.aspx"
        result_response = self.session.get(result_url, verify = False).text
        soup = BeautifulSoup(result_response, "html.parser")
        years_element = soup.find("select", id = "ThisYear")
        options_element = years_element.find_all("option")
        first_year = int(options_element[0].get("value"))
        last_year = int(options_element[-1].get("value"))

        return first_year, last_year
    
    def getThisSemCourses(self):
        result_url = self.domain + "/STDWEB/Sel_Student.aspx"
        result_response = self.session.get(result_url, verify = False).text
        soup = BeautifulSoup(result_response, "html.parser")
        a_tags = soup.find_all("a")
        courses = []
        for a in a_tags:
            if "ConnectCos_Short" in a.get("href"):
                courses.append(a.get_text())

        return list(dict.fromkeys(courses))
    
    def getSpeSemCourses(self, year, semester):
        result_url = self.domain + "/STDWEB/Sel_Student.aspx"
        form_data = {}
        form_data["ThisYear"] = year
        form_data["ThisTeam"] = semester
        result_response = self.session.post(result_url, data = form_data, verify = False).text
        soup = BeautifulSoup(result_response, "html.parser")
        a_tags = soup.find_all("a")
        courses = []
        for a in a_tags:
            if "ConnectCos_Short" in a.get("href"):
                courses.append(a.get_text())

        return list(dict.fromkeys(courses))
    
    def getAllCourses(self):
        courses = []
        first_year, last_year = self.__getClassOf()
        for year in range(first_year, last_year + 1):
            for semester in range(1, 3):
                courses += self.getSpeSemCourses(year, semester)
        return courses