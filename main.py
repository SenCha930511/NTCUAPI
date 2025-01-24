from flask import Flask, render_template, request, session, redirect, url_for, flash
from ntcu_api import Ntcu_api
import json
from datetime import datetime
from check import calculate_and_print_credits
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於 session 加密

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password
        return redirect(url_for('result'))
    return render_template('login.html')

@app.route('/result')
def result():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    password = session['password']
    
    try:
        courses_result = get_all_semesters_courses(username, password)
        credits_result = calculate_and_print_credits("all_courses.json", "111_cs.json", "111.json", "111_cs_num.json")
        return render_template('result.html', courses=courses_result, credits=credits_result)
    except Exception as e:
        flash(f"發生錯誤：{str(e)}", 'error')
        return redirect(url_for('login'))

def get_all_semesters_courses(username, password):
    api = Ntcu_api(username, password)
    all_courses = api.getAllCourses()
    result = {
        "total_courses": len(all_courses),
        "courses": all_courses,
        "timestamp": datetime.now().isoformat()
    }
    with open("all_courses.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result

if __name__ == '__main__':
    app.run(debug=True)