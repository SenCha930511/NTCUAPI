import json
from collections import Counter

def calculate_and_print_credits(all_courses_file, cs_requirements_file, general_requirements_file, cs_courses_file):
    def load_json(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_nested_value(dictionary, keys, default=0):
        for key in keys:
            if isinstance(dictionary, dict) and key in dictionary:
                dictionary = dictionary[key]
            else:
                return default
        return dictionary

    def calculate_credits(all_courses, cs_requirements, general_requirements, cs_courses):
        credits = {
            "通識課程": {
                "語文通識": {"已修": 0, "要求": 8},
                "社會人文領域": {"核心": 0, "選修": 0, "已修": 0, "核心要求": 4, "選修要求": 4},
                "數理科技領域": {"核心": 0, "選修": 0, "已修": 0, "核心要求": 2, "選修要求": 4},
                "藝術陶冶領域": {"核心": 0, "選修": 0, "已修": 0, "核心要求": 2, "選修要求": 2},
            },
            "共同課程": {
                "共同必修課程": {"已修": 0, "要求": 2},
                "共同選修課程": {"已修": 0, "要求": 0},
            },
            "專門課程": {
                "院共同課程": {"已修": 0, "要求": get_nested_value(cs_requirements, ["院共同課程", "總計"], 9)},
                "系基礎課程": {"已修": 0, "要求": get_nested_value(cs_requirements, ["系基礎課程", "總計"], 16)},
                "系核心課程": {"已修": 0, "要求": get_nested_value(cs_requirements, ["系核心課程", "總計"], 25)},
                "系專業模組課程": {
                    "基礎程式設計模組": {"已修": 0, "要求": 6},
                    "通訊網路理論模組": {"已修": 0, "要求": 9},
                    "軟體與系統理論模組": {"已修": 0, "要求": 9},
                    "整合性實作模組": {"已修": 0, "要求": 6}
                },
            },
        }

        course_category_map = {}
        
        # 處理系上課程
        for main_category in ["院共同課程", "系基礎課程", "系核心課程"]:
            for category, courses in cs_courses.get(main_category, {}).items():
                for course in courses:
                    course_category_map[course["科目名稱"]] = ("專門課程", main_category)
        
        for module, courses in cs_courses.get("系專業模組課程", {}).items():
            for course in courses.get("選修", []):
                course_category_map[course["科目名稱"]] = ("專門課程", "系專業模組課程", module)

        # 處理通識課程
        for category in ["語文通識課程", "社會人文領域", "數理科技領域", "藝術陶冶領域"]:
            if category == "語文通識課程":
                for course in general_requirements.get("通識課程", {}).get(category, []):
                    course_category_map[course["科目名稱"]] = ("通識課程", "語文通識")
            else:
                for sub_category in ["核心課程", "選修課程"]:
                    for course in general_requirements.get("通識課程", {}).get(category, {}).get(sub_category, []):
                        course_category_map[course["科目名稱"]] = ("通識課程", category, "核心" if sub_category == "核心課程" else "選修")

        # 處理共同課程
        for category in ["必修課程", "選修課程"]:
            for course in general_requirements.get("共同課程", {}).get(category, []):
                course_category_map[course["科目名稱"]] = ("共同課程", "共同必修課程" if category == "必修課程" else "共同選修課程")

        # 計算已修學分和檢測重複課程
        course_count = Counter(all_courses["courses"])
        ignored_courses = ["英文", "中文閱讀與表達", "班會"]
        repeated_courses = [course for course, count in course_count.items() if count > 1 and course not in ignored_courses]
        
        total_credits = 0
        for course, count in course_count.items():
            if course in course_category_map:
                category = course_category_map[course]
                if category[0] == "通識課程":
                    if category[1] == "語文通識":
                        credits["通識課程"]["語文通識"]["已修"] += 4  # 假設每門語文課 4 學分
                        total_credits += 4
                    else:
                        if category[2] == "核心":
                            credits["通識課程"][category[1]]["核心"] += 2  # 假設每門通識課 2 學分
                        else:
                            credits["通識課程"][category[1]]["選修"] += 2
                        credits["通識課程"][category[1]]["已修"] += 2
                        total_credits += 2
                elif category[0] == "專門課程":
                    if category[1] == "系專業模組課程":
                        credits["專門課程"]["系專業模組課程"][category[2]]["已修"] += 3  # 假設每門專業模組課程 3 學分
                        total_credits += 3
                    else:
                        credits["專門課程"][category[1]]["已修"] += 3  # 假設每門系上課程 3 學分
                        total_credits += 3
                elif category[0] == "共同課程":
                    credits["共同課程"][category[1]]["已修"] += 0.5  # 假設每門共同課程 0.5 學分
                    total_credits += 0.5
            else:
                # 如果課程不在任何類別中，仍然計入總學分
                total_credits += 3  # 假設每門未分類課程 3 學分

        # 處理通識課程核心多修學分抵免選修學分
        for category in ["社會人文領域", "數理科技領域", "藝術陶冶領域"]:
            core_excess = max(0, credits["通識課程"][category]["核心"] - credits["通識課程"][category]["核心要求"])
            credits["通識課程"][category]["選修"] += core_excess
            credits["通識課程"][category]["核心"] = min(credits["通識課程"][category]["核心"], credits["通識課程"][category]["核心要求"])

        return credits, repeated_courses, total_credits

    def format_credit_info(credits, required, category_type):
        total = credits
        diff = credits - required
        if diff > 0:
            return f"總修習學分: {total} 學分 (多修 {category_type} {diff} 學分)"
        elif diff < 0:
            return f"總修習學分: {total} 學分 (缺少 {category_type} {-diff} 學分)"
        else:
            return f"總修習學分: {total} 學分 (已達到要求)"

    def print_credits(credits, repeated_courses, total_credits):
        output = f"目前總學分數：{total_credits}\n\n修課進度：\n\n"
        
        output += "通識課程:\n"
        for category, data in credits["通識課程"].items():
            if category == "語文通識":
                output += f"    {category}: {format_credit_info(data['已修'], data['要求'], '必修')}\n"
            else:
                total_required = data['核心要求'] + data['選修要求']
                if data['已修'] >= total_required:
                    output += f"    {category}: 總修習學分: {data['已修']} 學分 (已達到要求)\n"
                else:
                    core_diff = data['核心'] - data['核心要求']
                    elective_diff = data['選修'] - data['選修要求']
                    output += f"    {category}: 總修習學分: {data['已修']} 學分 "
                    if core_diff != 0:
                        output += f"({'多修' if core_diff > 0 else '缺少'} 核心 {abs(core_diff)} 學分) "
                    if elective_diff != 0:
                        output += f"({'多修' if elective_diff > 0 else '缺少'} 選修 {abs(elective_diff)} 學分)"
                    output += "\n"

        output += "\n共同課程:\n"
        for category, data in credits["共同課程"].items():
            output += f"    {category}: {format_credit_info(data['已修'], data['要求'], '必修' if '必修' in category else '選修')}\n"

        output += "\n專門課程:\n"
        for category, data in credits["專門課程"].items():
            if category != "系專業模組課程":
                output += f"    {category}: {format_credit_info(data['已修'], data['要求'], '必修')}\n"
            else:
                output += "    系專業模組課程:\n"
                for module, module_data in data.items():
                    output += f"        {module}: {format_credit_info(module_data['已修'], module_data['要求'], '選修')}\n"

        if repeated_courses:
            output += "\n重複修習的課程:\n"
            for course in repeated_courses:
                output += f"    {course}\n"

        output += "\n目前可參考選擇課程：\n"
    
        # 系課程
        for category, data in credits["專門課程"].items():
            if category != "系專業模組課程":
                missing_credits = data["要求"] - data["已修"]
                if missing_credits > 0:
                    output += f"\n{category}(缺少 {missing_credits} 學分)\n"
                    output += "可修習課程為:\n"
                    for course in cs_courses.get(category, {}).get("必修", []):
                        if course["科目名稱"] not in all_courses["courses"]:
                            output += f"* {course['科目名稱']} (必修)\n"
            else:
                for module, module_data in data.items():
                    missing_credits = module_data["要求"] - module_data["已修"]
                    if missing_credits > 0:
                        output += f"\n{module}(缺少 {missing_credits} 學分)\n"
                        output += "可修習課程為:\n"
                        for course in cs_courses["系專業模組課程"][module].get("選修", []):
                            if course["科目名稱"] not in all_courses["courses"]:
                                output += f"* {course['科目名稱']} (選修)\n"
        
        # 通識課程
        for category, data in credits["通識課程"].items():
            if category == "語文通識":
                missing_credits = data["要求"] - data["已修"]
                if missing_credits > 0:
                    output += f"\n{category}(缺少 {missing_credits} 學分)\n"
                    output += "可修習課程為:\n"
                    for course in general_requirements["通識課程"]["語文通識課程"]:
                        if course["科目名稱"] not in all_courses["courses"]:
                            output += f"* {course['科目名稱']} (必修)\n"
            else:
                total_missing = (data["核心要求"] - data["核心"]) + (data["選修要求"] - data["選修"])
                if total_missing > 0:
                    output += f"\n{category}(缺少 {total_missing} 學分)\n"
                    output += "可修習課程為:\n"
                    for sub_category in ["核心課程", "選修課程"]:
                        for course in general_requirements["通識課程"][category][sub_category]:
                            if course["科目名稱"] not in all_courses["courses"]:
                                output += f"* {course['科目名稱']} ({'核心' if sub_category == '核心課程' else '選修'})\n"

        # 处理共同课程
        for category, data in credits["共同課程"].items():
            missing_credits = data["要求"] - data["已修"]
            if missing_credits > 0:
                output += f"\n{category}(缺少 {missing_credits} 學分)\n"
                output += "可修習課程為:\n"
                for course in general_requirements["共同課程"][category]:
                    if course["科目名稱"] not in all_courses["courses"]:
                        output += f"* {course['科目名稱']} ({'必修' if '必修' in category else '選修'})\n"

        return output

    try:
        all_courses = load_json(all_courses_file)
        cs_requirements = load_json(cs_requirements_file)
        general_requirements = load_json(general_requirements_file)
        cs_courses = load_json(cs_courses_file)

        credits, repeated_courses, total_credits = calculate_credits(all_courses, cs_requirements, general_requirements, cs_courses)
        return print_credits(credits, repeated_courses, total_credits)
    except FileNotFoundError as e:
        return f"錯誤：找不到檔案 - {e}"
    except json.JSONDecodeError as e:
        return f"錯誤：JSON 解析失敗 - {e}"
    except KeyError as e:
        return f"錯誤：找不到必要的鍵 - {e}"
    except Exception as e:
        return f"發生未預期的錯誤：{e}"

# 使用範例
# result = calculate_and_print_credits("all_courses.json", "111_cs.json", "111.json", "111_cs_num.json")
# print(result)