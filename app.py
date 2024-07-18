from flask import Flask, render_template, request, redirect, url_for,session
import sqlite3
app = Flask(__name__)

#=============homepage modules start =====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logout')
def logout():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    msg = ""
    if request.method == 'POST':
        try:
            name = request.form['name']
            loginid = request.form['loginid']
            email = request.form['email']
            password = request.form['password']
            branch = request.form['branch']
            collagename = request.form['collagename']
            phone = request.form['phone']
            locality = request.form['locality']
            state = request.form['state']                    
            
            status = 'waiting'             
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name, loginid, email, password, branch, collagename, phone, locality, state, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, loginid, email, password, branch, collagename, phone, locality, state, status))
                con.commit()
                msg = "Record successfully added to database"
        except Exception as e:
            con.rollback()
            msg = f"Error in the INSERT: {e}"
        finally:
            con.close()
            return render_template('register.html', msg=msg)
    return render_template('register.html')



@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    error = None
    if request.method == 'POST':
        loginid = request.form['loginid']
        password = request.form['password']
        if loginid == 'admin' and password == 'admin':
            return render_template('admins/adminhome.html')            
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('adminlogin.html',error=error)

@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    error = None
    if request.method == 'POST':
        loginid = request.form['loginid']
        password = request.form['password']        
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row  
            cur = con.cursor()
            cur.execute("SELECT * FROM students WHERE name = ? AND password = ?", (loginid, password))
            user = cur.fetchone()            
            if user:
                if user['status'] == 'waiting':
                    error = "Your account is not activated yet. Please contact admin."
                else:                    
                    return render_template('users/userhome.html')                    
            else:
                error = "Invalid credentials. Please try again."
    return render_template('userlogin.html', error=error)

#=============homepage modules ending =====================

#===================admin panel start here ================= 


@app.route('/adminhome')
def adminhome():
    return render_template('admins/adminhome.html')


@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")
    rows = cur.fetchall()
    con.close()    
    return render_template('admins/userlist.html',rows=rows)


@app.route('/delete_user/<int:uid>', methods=['GET'])
def delete_user(uid):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM students WHERE rowid = ?", (uid,))
        con.commit()
    return redirect(url_for('list'))


    
@app.route('/activate_user/<int:uid>')
def activate_user(uid):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE students SET status = 'activated' WHERE rowid = ?", (uid,))
        con.commit()
    return redirect(url_for('list'))


@app.route('/edit_user/<int:uid>', methods=['GET', 'POST'])
def edit_user(uid):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        status = request.form['status']        
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE students SET name = ?, email = ?, password = ?, status = ? WHERE rowid = ?", (name, email, password, status, uid))
            con.commit()
        return redirect(url_for('list'))

    else:
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM students WHERE rowid = ?", (uid,))
            user = cur.fetchone()
        return render_template('admins/edit_user.html', user=user, uid=uid)


#===================admin panel end =================


#===================user panel start =================
@app.route('/userhome')
def userhome():
    return render_template('users/userhome.html')

#===================user panel start =================





if __name__ == '__main__':
    app.run(debug=True)
