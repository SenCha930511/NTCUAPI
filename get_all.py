from ntcu_api import Ntcu_api
import json
from datetime import datetime
from check import calculate_and_print_credits

def get_all_semesters_courses(username, password):
    # 創建 Ntcu_api 實例
    api = Ntcu_api(username, password)

    # 獲取所有課程
    all_courses = api.getAllCourses()

    # 創建一個字典來存儲結果
    result = {
        "total_courses": len(all_courses),
        "courses": all_courses,
        "timestamp": datetime.now().isoformat()
    }

    # 將結果保存為 JSON 文件
    with open("all_courses.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

if __name__ == "__main__":
    # 請替換為您的實際用戶名和密碼
    username = "ACS111131"
    password = "!acs111131"

    result = get_all_semesters_courses(username, password)
    print(f"總共獲取到 {result['total_courses']} 門課程")
    print(f"結果已保存到 all_courses.json 文件中")
    check = calculate_and_print_credits("all_courses.json", "111_cs.json", "111.json", "111_cs_num.json")
    print("已計算並打印學分要求")
    print(check)