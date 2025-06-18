from flask import Flask, render_template, request, redirect, session,flash, jsonify
import pyodbc
from datetime import datetime
import api
app = Flask(__name__)
app.secret_key = 'my_secret_key'
# def connect_to_db():
#     # 连接数据库
#     try:
#         server = 'localhost'  # 服务器名称或IP地址
#         database = 'test'  # 数据库名称
#         username = 'SA'  # 用户名
#         password = 'Vv117889'  # 密码
#         cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=test;UID=SA;PWD=Vv117889')
#         print("数据库连接成功")
#         return cnxn
#     except pyodbc.Error as e:
#         print(f"数据库连接失败: {e}")
#         return None
#Linux数据库连接
def connect_to_db():
    # 连接数据库
    try:
        server = 'localhost'  
        database = 'test'  
        username = 'SA'  
        password = 'Vv117889'
        # 构建连接字符串
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        # 连接数据库
        cnxn = pyodbc.connect(conn_str)
        print("数据库连接成功")
        return cnxn
    except pyodbc.Error as e:
        print(f"数据库连接失败: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', name='name')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/database_class')
def database_class():
    return render_template('database_class.html')

@app.route('/resources')
def resources():
    if 'username' in session:
        cnxn = connect_to_db()
        cursor = cnxn.cursor()
        username = session['username']
        cursor.execute("SELECT * FROM tutoring WHERE username='{}'".format(username))  # 假设表名为 appointments
        appointments = cursor.fetchall()
        return render_template('resources.html', appointments=appointments)
    else:
        return render_template('resources.html')

@app.route('/tutoring', methods=['GET', 'POST'])
def tutoring():
    if request.method == 'POST':
        if 'username' in session:
            username=session['username']
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            choice = request.form['choice']
            message = request.form['message']
            time = datetime.now()
            time = time.strftime("%Y-%m-%d %H:%M:%S")
            status = '等待审核'
            cnxn = connect_to_db()
            cursor = cnxn.cursor()
            query = "INSERT INTO tutoring (username,name,email,phone,choice,message,time,status) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".format(username,name,email,phone,choice,message,time,status)
            cursor.execute(query)
            cnxn.commit()
            return '预约成功'
        else:
            return redirect('/login')
    else:
        return render_template('tutoring.html')

@app.route('/delete-appointment', methods=['POST'])
def delete_appointment():
    # # 获取要删除的预约 ID
    time = request.form.get('time')
    # 连接数据库并删除记录
    cnxn = connect_to_db()
    cursor = cnxn.cursor()
    cursor.execute("DELETE FROM tutoring WHERE time = '{}'".format(time))
    cnxn.commit()
    cursor.close()
    cnxn.close()

    # 提示用户删除成功
    flash('预约记录已删除。', 'success')
    return render_template('resources.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' not in session:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            cnxn = connect_to_db()
            cursor = cnxn.cursor()
            query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password)
            cursor.execute(query)
            user = cursor.fetchone()
            if user:
                session['username'] = user[0]       #这里由1修改为0，显示username。如果是1，则为username=password，错误
                return redirect('/login_success')
            else:
                return '登录失败，请检查用户名和密码是否正确！'
        else:
            return render_template('login.html')
    else :
        return redirect('/login_success')
@app.route('/login_success')
def login_success():
    if 'username' in session:
        username = session['username']
        return render_template('login_success.html', username=username)
    else:
        return redirect('/login')
@app.route('/register', methods=['GET', 'POST'])
def register():
    render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username:
            password_confirm = request.form.get('password_confirm')
            cnxn = connect_to_db()
            cursor = cnxn.cursor()
            query = "SELECT * FROM users WHERE username = '{}' ".format(username)
            cursor.execute(query)
            user = cursor.fetchone()
            if password != password_confirm:
                return '两次输入的密码不一致，请重新输入！'          #yes
            elif user:
                return '已有此账号请重新填写'
            else:       #elif password_confirm==password:
                query = "INSERT INTO users (username, password) VALUES ('{}', '{}')".format(username, password)     #向数据库中插入新数据，也就是注册过程
                cursor.execute(query)
                cnxn.commit()
                return redirect('/register_success')
        else :
            return '未输入用户名'
    else:
        return render_template('register.html')
@app.route('/register_success')
#########################################################################
def register_success():
    return render_template('register_success.html')     #这里由register_success.html改为register.html就可以跳转到注册页面，可以完成注册操作，对应SqlServer的表中的内容会增加一行，但是这个界面的登陆按钮无效
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/search', methods=['POST'])
def search():
    Query = request.json.get('query')
    if not Query:
        return jsonify([])

    cnxn = connect_to_db()
    cursor = cnxn.cursor()
    query = "SELECT name , url FROM courses WHERE name LIKE '%{}%' ".format(Query)
    cursor.execute(query)
    courses = cursor.fetchall()
    # courses = Course.query.filter(Course.name.like(f'%{query}%')).all()
    results=[]
    for course in courses:
        # 假设每个course是一个包含单个元素的元组，我们将其转换为字典
        results.append({"name" : course[0], "url" : course[1]})
    return jsonify(results)


@app.route('/aichat', methods=['GET','POST'])
def aichat():
    #获取前端发送的 JSON 数据

    if request.method == 'POST':
        data = request.json
        user_message = data.get('message', '')
        if user_message == 'welcome':
            response_message = "欢迎使用本网站，本网站旨在开发一个大语言模型的教学辅导网站"
            return(jsonify({"response": response_message}))
        #调用api接口
        response_message=api.api(user_message)
        # 返回 JSON 格式的回复
        return jsonify({"response": response_message})
    else:
        return render_template('aichat.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

