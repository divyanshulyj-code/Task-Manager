from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # change to a secure random string

# ===== Flask-Login Setup =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ===== User Class for Flask-Login =====
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None

# ===== Routes =====
@app.route('/')
def home():
    if current_user.is_authenticated:
        # Agar user logged in hai, to seedha tasks page par le jao
        return redirect(url_for('tasks'))
    else:
        # Agar logged in nahi hai, to landing page dikhao
        return render_template('index.html')

@app.route('/tasks')
@login_required
def tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE user_id=%s ORDER BY deadline", (current_user.id,))
    tasks = cursor.fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username,email,password_hash) VALUES (%s,%s,%s)", 
                       (username, email, hashed))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['email'])
            login_user(user_obj)
            return redirect(url_for('tasks'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/add', methods=['GET','POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title,description,deadline,user_id) VALUES (%s,%s,%s,%s)",
                       (title, description, deadline, current_user.id))
        conn.commit()
        conn.close()
        return redirect(url_for('tasks'))
    return render_template('add_task.html')

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (id,current_user.id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_status(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM tasks WHERE id=%s AND user_id=%s", (id,current_user.id))
    task = cursor.fetchone()
    if not task:
        conn.close()
        return jsonify({'success': False})
    new_status = 'Completed' if task['status'] == 'Pending' else 'Pending'
    cursor.execute("UPDATE tasks SET status=%s WHERE id=%s AND user_id=%s", (new_status,id,current_user.id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'status': new_status})

if __name__ == '__main__':
    app.run(debug=True)
    # app.py file mein yeh naya route add karo

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Task ko fetch karo
    cursor.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (id, current_user.id))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return redirect(url_for('tasks'))
        
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        
        # Task ko update karo
        cursor.execute("UPDATE tasks SET title=%s, description=%s, deadline=%s WHERE id=%s AND user_id=%s",
                       (title, description, deadline, id, current_user.id))
        conn.commit()
        conn.close()
        return redirect(url_for('tasks'))
        
    conn.close()
    return render_template('edit_task.html', task=task)