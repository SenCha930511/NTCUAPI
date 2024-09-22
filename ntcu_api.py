import requests
import random
import recaptchaByPass
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict

class Ntcu_api():
    """
    NTCU API 提供與學校網站進行互動的接口，用於獲取課程、成績等資料。
    
    初始化方法:
    :param account: str - 使用者帳號
    :param password: str - 使用者密碼
    """

    def __init__(self, account: str, password: str):
        """
        初始化 NTCU API 並建立使用者會話。
        :param account: str - 使用者帳號
        :param password: str - 使用者密碼
        """
        self.__account: str = account
        # 隨機選擇學校伺服器域名
        self.__domain: str = random.choice(["https://ecsa.ntcu.edu.tw", "https://ecsb.ntcu.edu.tw"])
        # 登入並建立會話
        self.__session: requests.Session = self.__getSession(account, password)  


    def __getSession(self, account: str, password: str) -> requests.Session:
        """
        建立與學校伺服器的會話，並完成登入。
        :param account: str - 使用者帳號
        :param password: str - 使用者密碼
        :return: requests.Session - 已登入的會話對象
        """
        # 取得 CSRF token 和驗證碼資料，進行登入
        session, form_data = self.__getCrsf()
        session, form_data = self.__getCheckCodeData(session, form_data)
        session = self.__login(session, form_data, account, password)
        return session    
    

    def __getCrsf(self) -> Tuple[requests.Session, Dict[str, str]]:
        """
        從學校網站獲取 CSRF token。
        :return: Tuple[requests.Session, Dict[str, str]] - 會話對象和表單資料
        """
        session = requests.Session()
        # 請求登入頁面以獲取 CSRF token
        page_response = session.get(self.__domain, verify=False)

        # 使用 BeautifulSoup 分析 HTML，提取 CSRF token
        soup = BeautifulSoup(page_response.text, "html.parser")
        csrf_token: str = soup.find("input", {"id": "csrf_token"})["value"]

        # 包含 CSRF token 的表單資料
        form_data: Dict[str, str] = {
            "csrf_token": csrf_token
        }

        return session, form_data


    def __getCheckCodeData(self, session: requests.Session, form_data: Dict[str, str]) -> Tuple[requests.Session, Dict[str, str]]:
        """
        獲取驗證碼圖片並通過 recaptchaByPass 驗證。
        :param session: requests.Session - 會話對象
        :param form_data: Dict[str, str] - 表單資料
        :return: Tuple[requests.Session, Dict[str, str]] - 更新的會話對象和表單資料
        """
        check_url: str = self.__domain + "/HttpRequest/Get_Check_Code.ashx"
        # 向伺服器請求驗證碼資料
        check_code_data: Dict = session.post(check_url, data=form_data, verify=False).json()

        # 使用 recaptchaByPass 模組破解驗證碼圖片
        code_image: str = check_code_data[0]["Code_Image"]
        form_data["Check_Code"] = recaptchaByPass.recaptchaByPass(code_image)
        form_data["MD5_EnCode"] = check_code_data[0]["MD5_EnCode"]
        form_data["SHA1_EnCode"] = check_code_data[0]["SHA1_EnCode"]

        return session, form_data


    def __login(self, session: requests.Session, form_data: Dict[str, str], account: str, password: str) -> requests.Session:
        """
        執行學校網站的登入操作。
        :param session: requests.Session - 會話對象
        :param form_data: Dict[str, str] - 包含登入資訊的表單資料
        :param account: str - 使用者帳號
        :param password: str - 使用者密碼
        :return: requests.Session - 已登入的會話對象
        """
        # 準備登入所需的表單資料
        form_data["Model"] = "Do_Login"
        form_data["Type"] = "0"
        form_data["User_Account"] = account
        form_data["User_Password"] = password

        # 發送登入請求
        login_url: str = self.__domain + "/login.aspx"
        login_response: Dict = session.post(login_url, data=form_data, verify=False).json()

        return session
    

    def __getClassOf(self) -> Tuple[int, int]:
        """
        獲取學生的學年範圍（如 111 到 113）。
        :return: Tuple[int, int] - 第一學年和最後學年
        """
        url: str = self.__domain + "/STDWEB/Sel_Student.aspx"
        response: str = self.__session.get(url, verify=False).text
        soup = BeautifulSoup(response, "html.parser")
        
        # 解析學年選擇框中的年份資料
        years_element = soup.find("select", id="ThisYear")
        options_element = years_element.find_all("option")
        first_year: int = int(options_element[0].get("value"))
        last_year: int = int(options_element[-1].get("value"))

        return first_year, last_year


    def __getRawGrd(self, avg: bool = False) -> str:
        """
        取得原始的成績資料。

        :param avg: bool - 如果為 True，則取得平均成績資料；否則取得所有單科成績資料。
        :return: str - 以 XML 格式返回的成績資料。
        """
        url: str = self.__domain + "/HttpRequest/STDWCore.aspx"
        form_data: Dict[str, str] = (
            {"ModuleName": "GetStdYearAvg", "StdNo": self.__account, "responseXML": "true"}
            if avg
            else {"ModuleName": "GetStdYearScore", "StdNo": self.__account, "responseXML": "true", "Avg": "true"}
        )
        response: requests.Response = self.__session.post(url, data=form_data, verify=False)

        return response.text

    def getSpeSemCourses(self, year: int, semester: int) -> List[str]:
        """
        獲取指定學年和學期的課程。
        :param year: int - 學年
        :param semester: int - 學期 (1, 2, 3, 或 4)
        :return: List[str] - 指定學期課程列表
        """
        url: str = self.__domain + "/STDWEB/Sel_Student.aspx"
        form_data: Dict[str, int] = {
            "ThisYear": year,
            "ThisTeam": semester
        }
        response: str = self.__session.post(url, data=form_data, verify=False).text
        soup = BeautifulSoup(response, "html.parser")

        # 提取課程名稱
        a_tags = soup.find_all("a")
        courses: List[str] = []
        for a in a_tags:
            if "ConnectCos_Short" in a.get("href"):
                courses.append(a.get_text())

        # 移除重複的課程
        return list(dict.fromkeys(courses))


    def getAllCourses(self) -> List[str]:
        """
        獲取所有學年和學期的課程。
        :return: List[str] - 所有課程列表
        """
        courses: List[str] = []
        first_year, last_year = self.__getClassOf()

        # 遍歷每個學期並獲取課程
        from itertools import chain

        courses = list(chain.from_iterable(self.getSpeSemCourses(year, semester) 
                                            for year in range(first_year, last_year + 1) 
                                            for semester in range(1, 3) 
                                            if self.getSpeSemCourses(year, semester)))

        return courses
    

    def getAllGrd(self) -> List[Dict[str, str]]:
        """
        獲取所有學期的成績資料。
        :return: List[Dict[str, str]] - 成績資料列表，每筆資料包含課程名稱、選修類型、成績
        """
        raw_data: str = self.__getRawGrd(avg = False)
        root = ET.fromstring(raw_data)

        # 解析成績資料
        grds: List[Dict[str, str]] = []
        grds.extend({
            "course_name": item.find("Cos_Name").text,
            "selkind": item.find("SelKind_Name").text,
            "score": item.find("Score").text,
            "credit": item.find("Credit").text
        } for item in root.findall("DataItem"))

        return grds
    

    def getAvgGrd(self) -> List[Dict[str, str]]:
        """
        獲取每個學期平均的成績資料。
        :return: List[Dict[str, str]] - 成績資料列表，每筆資料包含年分、學期、平均成績、總學分
        """
        raw_data: str = self.__getRawGrd(avg = True)
        root = ET.fromstring(raw_data)

        # 解析成績資料
        avg_grds: List[Dict[str, str]] = []
        avg_grds.extend({
            "years": item.find("years").text,
            "term": item.find("term").text,
            "avg": item.find("Grd_Avg").text,
            "all_credit": item.find("All_Credit").text
        } for item in root.findall("DataItem"))

        return avg_grds
