# NTCU API

NTCU API 提供與學校網站進行互動的接口，用於獲取課程、成績等資料。

## 簡介

此項目是用於與國立臺中教育大學 (NTCU) 的網站進行互動的 Python API，能夠獲取學生的課程和成績等資訊。

## 安裝

```bash
pip install requests beautifulsoup4 ddddocr
```

## 使用方法

1. 初始化 API：
    ```python
    from ntcu_api import Ntcu_api

    ntcu = Ntcu_api(account='你的帳號', password='你的密碼')
    ```

2. 獲取當前學期的課程：
    ```python
    courses = ntcu.getThisSemCourses()
    print(courses)
    ```

3. 獲取所有學期的成績：
    ```python
    grades = ntcu.getAllGrd()
    print(grades)
    ```

## 功能

- 獲取當前學期的所有課程
- 獲取指定學年和學期的課程
- 獲取所有學期的成績資料
- 獲取每個學期的平均成績資料

## 許可證

本項目使用 MIT 許可證。詳細內容請參閱 [LICENSE](LICENSE) 檔案。
