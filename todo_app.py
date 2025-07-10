from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
DATABASE="flasktodo.db"

app = Flask(__name__)

@app.route("/")
def top():
    sort_order = request.args.get("sort", "asc") #デフォルトは昇順
    todo_list = get_sorted_todos(sort_order)
    return render_template("index.html", todo_list=todo_list, sort_order=sort_order)

@app.route("/todo_regist",methods=['GET','POST'])
def regist():
    if request.method == 'POST':
        #画面からの登録情報の取得
        title = request.form.get('title')
        detail = request.form.get('detail')
        deadline = request.form.get('deadline')
        status = request.form.get('status')
        category = request.form.get('category')
        db = get_db()
        db.execute("insert into todo (title,detail,deadline,status,category) values(?,?,?,?,?)",[title,detail,deadline,status,category])
        db.commit()
        return redirect('/')
    return render_template('todo_regist.html')

@app.route("/<int:id>/todo_edit", methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title')
        detail = request.form.get('detail')
        deadline = request.form.get('deadline')
        status = request.form.get('status')
        category = request.form.get('category')
        db.execute("UPDATE todo SET title = ?, detail = ?, deadline = ?, status = ?, category = ? WHERE id = ?", (title, detail, deadline, status, category, id))
        db.commit()
        return redirect('/')
    post = db.execute("SELECT id, title, detail, deadline, status, category FROM todo WHERE id = ?", (id,)).fetchone()
    return render_template('todo_edit.html', post=post)

@app.route("/todo_complete", methods=['GET'])
def complete():
    db = get_db()
    complete_list = db.execute("SELECT id, title, detail, deadline, status, category FROM todo WHERE status = ? AND is_deleted = 0", ('完了',)).fetchall()
    return render_template("todo_complete.html", complete_list=complete_list)

@app.route('/todo_complete_update', methods=['POST'])
def todo_complete_update():
    todo_id = request.form.get('id')
    db = get_db()
    db.execute("UPDATE todo SET status = ? WHERE id = ?", ('完了' , todo_id) )
    db.commit()
    return redirect("/")

@app.route('/back', methods=['POST'])
def back():
    todo_id = request.form.get('id')
    db = get_db()
    db.execute("UPDATE todo SET status = '進行中' WHERE id = ?", (todo_id,))
    db.commit()
    return redirect("/todo_complete")

@app.route('/trash')
def trash():
    db = get_db()
    trash_list = db.execute("SELECT * FROM todo WHERE is_deleted = 1").fetchall()
    return render_template('trash.html', trash_list=trash_list)

@app.route('/todo_move_trash', methods=['POST'])
def todo_move_trash():
    todo_id = request.form.get('id')
    db = get_db()
    db.execute("UPDATE todo SET is_deleted = 1 WHERE id = ?", (todo_id,))
    db.commit()
    return redirect('/')

@app.route('/restore', methods=['POST'])
def todo_restore_from_trash():
    todo_id = request.form.get('id')
    db = get_db()
    db.execute("UPDATE todo SET is_deleted = 0 WHERE id = ?", (todo_id,))
    db.commit()
    return redirect('/trash')

if __name__ == '__main__':
    app.run()

#DATABASE
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
def get_sorted_todos(order="asc"):
    db = get_db()
    if order == "desc":
        cur = db.execute("SELECT * FROM todo WHERE status = '進行中' AND is_deleted = 0 ORDER BY deadline DESC")
    else:
        cur = db.execute("SELECT * FROM todo WHERE status = '進行中' AND is_deleted = 0 ORDER BY deadline ASC")
    rows = cur.fetchall()
    return rows