# -*- coding: utf-8 -*-
from flask import *
from werkzeug.utils import secure_filename

from flask_bootstrap import Bootstrap
from urllib.parse import *
import pymysql, hashlib, os, time, random

app = Flask(__name__)
app.secret_key = 'dev'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])

Bootstrap(app)

def getLoginDetails():
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = %s", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = %s", (userId, ))
            noOfItems = cur.fetchone()[0]
    return (loggedIn, firstName, noOfItems)

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

def is_valid(email, password):
    con = pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5)
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    con.close()
    return False

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def random_color():
    colorArr = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color

@app.route('/init')
def init():
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        # Create table
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE users (userId INTEGER AUTO_INCREMENT PRIMARY KEY, password TEXT, email TEXT, firstName TEXT, lastName TEXT, phone TEXT)")
            cur.execute("CREATE TABLE categories (categoryId INTEGER PRIMARY KEY, name TEXT)")
            cur.execute("CREATE TABLE orders (orderId INTEGER PRIMARY KEY, userId INTEGER, productId INTEGER, num INTEGER)")
            cur.execute("CREATE TABLE products (productId INTEGER AUTO_INCREMENT PRIMARY KEY, name TEXT, price REAL, description TEXT, image TEXT, stock INTEGER, categoryId INTEGER, FOREIGN KEY(categoryId) REFERENCES categories(categoryId))")
            cur.execute("CREATE TABLE kart (userId INTEGER, productId INTEGER, num INTEGER, FOREIGN KEY(userId) REFERENCES users(userId), FOREIGN KEY(productId) REFERENCES products(productId))")
            
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (1, 'Men\'s'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (2, 'Women\'s'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (3, 'HeadPhones'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (4, 'Computers'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (5, 'CellPhones'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (6, 'Snacks'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (7, 'Drinks'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (8, 'CookedFoods'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (9, 'Basketball'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (10, 'Tennis'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (11, 'Golf'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (12, 'Clothing'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (13, 'Camping'))
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (%s, %s)", (14, 'Cycling'))

            password = '12345678'
            email = '11111@qq.com'
            firstName = 'Admin'
            lastName = 'Tony'
            phone = '10101010'
            cur.execute("INSERT INTO users (userId, password, email, firstName, lastName, phone) VALUES (%s, %s, %s, %s, %s, %s)", ("1", hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, phone))
            password = '12345678'
            email = '22222@qq.com'
            firstName = 'Admin2'
            lastName = 'Ben'
            phone = '1010101'
            cur.execute("INSERT INTO users (userId, password, email, firstName, lastName, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                        ("2", hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, phone))
            
            cur.execute("INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)",
                        ("Basketball", "120", "A nice basketball!", "basketball_1.jpg", "101", "9"))
            cur.execute("INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)",
                        ("Beats EP", "2000", "A nice earphone!", "beats_ep.png", "16", "3"))
            cur.execute("INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)",
                        ("Beats studio3", "3000", "Another nice earphone!", "beats_studio3.png", "5", "3"))

            conn.commit()
            flash("initialize database successfully")

        except Exception as e:
            conn.rollback()
            flash(str(e))

    return redirect(url_for('root'))


@app.route('/')
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
            if len(itemData) > 9:
                itemData = itemData[0:9]
        except Exception as e:
            return render_template('error.html')
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

@app.route("/add")
def admin():
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT categoryId, name FROM categories")
            categories = cur.fetchall()
        except Exception as e:
            flash(str(e))
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
        imagename = filename
        with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)", (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except Exception as e:
                msg="error occured"
                conn.rollback()
                flash(str(e))
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = %s', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except Exception as e:
            conn.rollback()
            msg = "Error occured"
            flash(str(e))
    print(msg)
    return redirect(url_for('root'))

@app.route('/displayCategory/<int:categoryId>')
def displayCategory(categoryId):
    loggedIn, firstName, noOfItems = getLoginDetails()
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.description, products.image, products.stock, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = %s",
            (categoryId,))
        itemData = cur.fetchall()
        curr = conn.cursor()
        curr.execute("SELECT categories.name from categories WHERE categories.categoryId = %s", (categoryId,))
        categoryName = curr.fetchone()[0]
    existItem = True
    if len(itemData) == 0:
        existItem = False
    return render_template('display.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, existItem=existItem, categoryName=categoryName)

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    error=''
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
    return render_template('login.html', error=error)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        phone = request.form['phone']

        with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, phone) VALUES (%s, %s, %s, %s, %s)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, phone))
                con.commit()
                flash("Registered Successfully")
            except:
                con.rollback()
                flash("Error occured")
        return redirect(url_for('root'))

@app.route("/profile")
def profileForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, phone FROM users WHERE email = %s", (session['email'], ))
        profileData = cur.fetchone()
    return render_template("profile.html", profileData=profileData)

@app.route("/editProfile", methods = ['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        phone = request.form['phone']
        with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as con:
            try:
                cur = con.cursor()
                cur.execute('UPDATE users SET firstName = %s, lastName = %s, phone = %s WHERE email = %s', (firstName, lastName, phone, email))
                con.commit()
                flash("Saved Successfully")
            except:
                con.rollback()
                flash("Error occured")
        return redirect(url_for('root'))

@app.route("/password")
def passwordForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        return render_template("password.html", msg='')

@app.route("/changePassword", methods = ['GET', 'POST'])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = %s", (session['email'],))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = %s WHERE userId = %s", (newPassword, userId))
                    conn.commit()
                    flash("Changed successfully")
                except:
                    conn.rollback()
                    flash("Failed")
                return redirect(url_for('root'))
            else:
                msg = "Wrong password"
        return render_template("password.html", msg=msg)
    else:
        return render_template("password.html", msg='')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    productId = int(request.args.get('productId'))
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
        num = cur.fetchall()
        print(num)
        try:
            if len(num) > 0:
                new_num = num[0][0] + 1
                cur.execute("UPDATE kart SET num = %s WHERE userId = %s AND productId = %s", (new_num, userId, productId))
            else:
                cur.execute("INSERT INTO kart (userId, productId, num) VALUES (%s, %s, %s)", (userId, productId, 1))
            conn.commit()
            flash("Added successfully")
        except Exception as e:
            print(e)
            conn.rollback()
            flash("Error occured")
    return redirect_back()

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image, kart.num FROM products, kart WHERE products.productId = kart.productId AND kart.userId = %s", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    productList = []
    for i,row in enumerate(products):
        partialPrice = row[2] * row[4]
        productList.append([row[0], row[1], row[2], row[3], row[4], partialPrice])
        totalPrice += partialPrice
    existItem = False
    if noOfItems > 0:
        existItem = True
    return render_template("cart.html", products = productList, totalPrice=totalPrice, existItem=existItem, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
        num = cur.fetchall()
        try:
            if num[0][0] > 1:
                new_num = num[0][0] - 1
                cur.execute("UPDATE kart SET num = %s WHERE userId = %s AND productId = %s",
                            (new_num, userId, productId))
            else:
                cur.execute("DELETE FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
            conn.commit()
            flash("removed successfully")
        except Exception as e:
            print(e)
            conn.rollback()
            flash("error occured")
    return redirect_back()

@app.route("/newOrder")
def newOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    productId = int(request.args.get('productId'))
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
        num = cur.fetchone()[0]
        orderId = int(time.time()) + productId
        print(userId, " ", num, " ", orderId)
        try:
            cur.execute("INSERT INTO orders (orderId, userId, productId, num) VALUES (%s, %s, %s, %s)", (orderId, userId, productId, num))
            cur.execute("DELETE FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
            conn.commit()
            flash("Trade successfully")
        except Exception as e:
            print(e)
            conn.rollback()
            flash("Trade failed")
    return redirect(url_for('orders'))

@app.route("/newAllOrder")
def newAllOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num, productId FROM kart WHERE userId = %s", (userId, ))
        orders = cur.fetchall()
        if len(orders)==0:
            flash("No Trade")
            return redirect(url_for('cart'))
        try:
            for order in orders:
                num = order[0]
                productId = order[1]
                orderId = int(time.time()) + productId
                cur.execute("INSERT INTO orders (orderId, userId, productId, num) VALUES (%s, %s, %s, %s)", (orderId, userId, productId, num))
                cur.execute("DELETE FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
            conn.commit()
            flash("Trade successfully")
        except:
            conn.rollback()
            flash("Trade failed")
    return redirect(url_for('orders'))

@app.route("/orders")
def orders():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with pymysql.connect(host=os.environ['MYSQL_ENDPOINT'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'],
            passwd=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'], connect_timeout=5) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT orders.num, orders.orderId, products.name, products.price FROM products, orders WHERE products.productId = orders.productId AND orders.userId = %s", (userId, ))
        orders = cur.fetchall()
    orderList=[]
    for i,row in enumerate(orders):
        partialPrice = row[0] * row[3]
        time_stamp = int(row[1] / 1000000)
        time_array = time.localtime(time_stamp)
        str_date = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        color = random_color()
        orderList.append([row[0], row[1], row[2], row[3], partialPrice, str_date, color])
    existOrder = False
    if len(orders) > 0:
        existOrder = True
    return render_template("order.html", orders=orderList, existOrder=existOrder, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

if __name__=="__main__":
    app.run(debug=True)