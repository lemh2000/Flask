from flask import Flask, render_template, request, redirect, session, url_for
import pymysql
from pymysql.constants import CLIENT

app = Flask(__name__)

app.secret_key = "asdfasdfasdf"

db = pymysql.connect(host="localhost", user="root", passwd="1234", db="server", charset="utf8", client_flag=CLIENT.MULTI_STATEMENTS)

cur = db.cursor()


@app.route("/")
def main():
    sql = "SELECT * FROM board"
    cur.execute(sql)
    data_list = cur.fetchall()
    if 'username' in session:
        username = session['username']
        return render_template('index.html', data_list=data_list, username=username)
    return render_template('index.html', data_list=data_list)

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        register_info = request.form

        username = register_info['username']
        password = register_info['password']

        sql = """
            INSERT INTO userinfo (username, password)
            VALUES (%s, %s);
        """
        
        
        try:
            cur.execute(sql, (username, password))
        except:
            return """
                <script>
                    alert("이미 존재하는 계정입니다.")
                    location.href="/register"
                </script>
            """
        

        db.commit()
        
        return redirect(url_for('main'))
    return render_template('register.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        login_info = request.form

        username = login_info['username']
        password = login_info['password']

        sql = "SELECT * FROM userinfo WHERE username=%s"
        rows_count = cur.execute(sql, username)

        if rows_count > 0:
            user_info = cur.fetchone()
            is_pw_correct = password == user_info[1]
            if is_pw_correct:
                session['username'] = username
                return redirect(url_for('main'))
            else:
                return '''
                            <script>
                                alert("비밀번호가 올바르지 않습니다")
                                location.href="/login"
                            </script>
                          '''
        else:
            return '''
                        <script>
                            alert("사용자 계정이 존재하지 않습니다")
                            location.href="/login"
                        </script>
                      '''
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main'))

@app.route("/write")
def write():
    return render_template('write.html')

@app.route("/write_action", methods=['POST'])
def write_action():

    write_info = request.form

    title = write_info['title']
    writer = session['username']
    content = write_info['content']

    sql = """
            INSERT INTO board (title, writer ,content)
            VALUES (%s, %s, %s)
        """
    cur.execute(sql, (title, writer, content))

    db.commit()
    return main()

@app.route("/view/<num>")
def view(num):
    sql = "SELECT * FROM board where num = %s"
    cur.execute(sql, num)
    data = cur.fetchone()
    writer = data[2]
    title =  data[1]
    content = data[3]
    return render_template('view.html', writer=writer, title=title, content=content, num=num)

@app.route('/delete/<num>', methods=['GET'])
def delete(num):
    if 'username' in session: 
        sql = "SELECT * FROM board where num = %s"
        cur.execute(sql, num)
        data = cur.fetchone()
        if session['username'] == data[2] or session['username'] == 'admin':
            print('2')
            sql = """   
                delete from board where num = %s;
                SET @CNT = 0;
                UPDATE board SET board.num =  @CNT:=@CNT+1;
                Alter Table board Auto_increment=1;
            """
            cur.execute(sql, num)
            db.commit()
            return """
                <script>
                    alert("글이 삭제 되었습니다")
                    location.href="/"
                </script>
            """
    return """
        <script>
            alert("삭제 권한이 없습니다.")
            location.href="/"
        </script>
    """

@app.route('/edit/<num>', methods=['GET','POST'])
def edit(num):
    if request.method == 'POST':
        edit_info = request.form

        title = edit_info['title']
        content = edit_info['content']
        num = edit_info['num']
        sql = "update board set title = %s, content = %s WHERE num = %s;"
        cur.execute(sql, (title, content, num))
        db.commit()

        return redirect(url_for('view', num=num))
    if 'username' in session:
        sql = "SELECT * FROM board where num = %s"
        cur.execute(sql, num)
        data = cur.fetchone()
        if session['username'] == data[2] or session['username'] == 'admin':
            return render_template('edit.html', data=data)
    return """
        <script> 
            alert("수정 권한이 없습니다.")
            location.href="/"
        </script>
        """
    
if __name__ == "__main__":
    app.run()