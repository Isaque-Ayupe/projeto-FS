from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = 'segredo_ultra_confidencial'

def get_db_connection():
    return pymysql.connect(
        database="gerenciado_de_tarefas",
        user="root",
        password="1234",
        host="localhost",
        port=3306,
        cursorclass=pymysql.cursors.Cursor
    )

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        birthdate = request.form['birthdate']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, birthdate, email, phone, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, birthdate, email, phone, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Usuário criado com sucesso!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash("Erro ao criar usuário. Nome de usuário pode já existir.", "danger")
            print(e)
    return render_template('cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, username FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('calendario'))
    else:
        flash("Login inválido!", "danger")
        return redirect(url_for('index'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    if 'user_id' not in session:
        return jsonify([])

    date = request.args.get('data')
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hour, task FROM tasks WHERE id_user=%s AND date=%s", (user_id, date))
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({hora: texto for hora, texto in tarefas})

@app.route('/tarefas', methods=['POST'])
def post_tarefa():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    user_id = session['user_id']
    date = data['date']
    hour = data['hour']
    task = data['task']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (id_user, date, hour, task)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE task = VALUES(task)
    """, (user_id, date, hour, task))
    conn.commit()
    cursor.close()
    conn.close()

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
