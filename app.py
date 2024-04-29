from flask import Flask, flash, render_template, request, redirect, session
from datetime import date, datetime
from cs50 import SQL
from flask_session import Session
from helpers import zar, login_required
from werkzeug.utils import secure_filename
import os

from werkzeug.security import check_password_hash, generate_password_hash

# Configure app
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["zar"] = zar

# Set upload path
UPLOAD_FOLDER = '/workspaces/14761904/project/static/product_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the to use the upload path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gospice.db")

@app.route("/")
def index():
    products = db.execute("SELECT * FROM products")
    # item_found = False

    items = []
    for product in products:
        items_dict = {}
        items_dict["id"] = product["id"]
        items_dict["photo"] = product["photo"]
        items_dict["description"] = product["description"]
        items_dict["price"] = zar(product["price"])
        items_dict["qty_left"] = product["qty_on_hand"]

        if "cart" in session:
            for item in session["cart"]:
                if item["id"] == product["id"]:
                    items_dict["qty_left"] = product["qty_on_hand"] - item["qty"]
                    break
                else:
                    continue

        items.append(items_dict)

    return render_template("index.html", products=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    user = db.execute("SELECT username FROM users")
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Ensure username was entered
        if not name:
            return render_template("apology.html", message="Please enter a valid email address")
        # Ensure password was entered
        elif not password:
            return render_template("apology.html", message="must provide password")
        elif not confirm_password:
            return render_template("apology.html",message="must provide confirm password")

        if password != confirm_password:
            return render_template("apology.html", message="passwords do not match")

        if any(d.get('username') == name for d in user):
            return render_template("apology.html",message="username already exists")
        else:
            db.execute("INSERT INTO users (username, hash,account_type) VALUES(?, ?, ?)",name,generate_password_hash(password),0)
            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html",message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html",message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html",message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["account"] = rows[0]["account_type"]
        session["cart"] = []

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/products", methods=["GET", "POST"])
@login_required
def add_product():
    """Add products to inventory"""

    if request.method == "POST":
        description = request.form.get("description")
        quantity = request.form.get("quantity")
        price = request.form.get("price")

        # check if the post request has the file part
        if 'picture' not in request.files:
            flash('No file part')
            return render_template("apology.html",message="Error uploading picture, please try again")
        file = request.files['picture']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template("apology.html",message="No image selected")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = ("/static/product_images/"+filename)

            # Save the image to the "UPLOAD_FOLDER" path on the server
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save entry to the database
        # db.execute("INSERT INTO users (username, hash,account_type) VALUES(?, ?, ?)",name,generate_password_hash(password),0)
        db.execute("INSERT INTO products (description, qty_on_hand, photo, price) VALUES(?, ?, ?, ?)",description, int(quantity), image_path, float(price))

        return render_template("apology.html", message="Product added successfully")

    else:
        return render_template("products.html")

@app.route("/product_list")
@login_required
def view_products():

    products = db.execute("SELECT * FROM products")
    items = []
    for product in products:

        items_dict = {}
        items_dict["id"] = product["id"]
        items_dict["photo"] = product["photo"]
        items_dict["description"] = product["description"]
        items_dict["qty_on_hand"] = product["qty_on_hand"]
        items_dict["price"] = zar(product["price"])

        items.append(items_dict)

    return render_template("product_list.html",products=items)

@app.route("/cart/<int:product_id>")
@login_required
def add_to_cart(product_id: int):
    item_found = False
    if "cart" not in session:
        session["cart"] = []

    # Create product dictionary to add to cart list
    #TODO
    product_dict = {}
    product_dict["id"] = product_id
    product_dict["qty"] = 1

    for item in session["cart"]:
        if product_id == item["id"]:
            item_found = True
            item["qty"] = item["qty"] + 1
            break;
        else:
            item_found = False

    if item_found == False:
        session["cart"].append(product_dict)

    # print(session["cart"])

    return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id, cart, and account type
    session.clear()

    return redirect("/")


@app.route("/view_cart", methods=["GET", "POST"])
@login_required
def view_cart():
    user_exists = False

    if "cart" not in session:
        session["cart"] = []

    clients_info = db.execute("SELECT * FROM client_info")
    for client in clients_info:
        if session["user_id"] == client["user_id"]:
            user_exists = True

    cart_items = []
    total_due = 0;
    if request.method == "POST":
        if session["cart"] == []:
            return render_template("apology.html", message="No items in cart")
        elif user_exists == False:
            return redirect("/update_profile")
        else:
            order_number = int(generate_order_number())
            order_date = date.today()
            user = session["user_id"]
            status = "Received"

            for item in session["cart"]:
                product_id = item["id"]
                order_qty = item["qty"]

                try:
                    # Create new order
                    db.execute("INSERT INTO orders (order_no, product_id, quantity) VALUES(?, ?, ?)", order_number, product_id, order_qty)

                    # Update products list quantities
                    product = db.execute("SELECT qty_on_hand FROM products WHERE id=?", product_id)
                    current_qty = product[0]["qty_on_hand"]
                    new_qty = current_qty - order_qty
                    # Update products table
                    db.execute("UPDATE products SET qty_on_hand = ? WHERE id = ?", new_qty, product_id)
                except Exception:
                    return render_template("apology.html", message="Could not place order")

            db.execute("INSERT INTO user_orders (order_no, user_id, status, date) VALUES(?, ?, ?, ?)", order_number, user, status, order_date)
            # Clear cart
            session["cart"] = []
            # Render orders
            return render_template("apology.html", message="Order Placed Successfully")

    else:
        # Display all the items from the cart

        # print(session["cart"])
        # Query database for the cart items
        for item in session["cart"]:
            id = item["id"]
            quantity = item["qty"]

            products = db.execute("SELECT id, description, qty_on_hand, photo, price FROM products WHERE id = ?", id)
            # print(products)

            if products[0]["qty_on_hand"] < quantity:
                for item in session["cart"].copy():
                    if id == products[0]["id"]:
                        session["cart"].remove(item)
                        break
                continue

            item_dict = {}
            price = products[0]["price"]

            item_dict["id"] = products[0]["id"]
            item_dict["photo"] = products[0]["photo"]
            item_dict["quantity"] = quantity
            item_dict["description"] = products[0]["description"]
            item_dict["price"] = zar(price)
            item_dict["item_total"] = zar(quantity * price)
            total_due = total_due + (quantity * price)

            cart_items.append(item_dict)

        # print(cart_items)
        return render_template("cart.html", cart_items=cart_items, total_due=zar(total_due))


@app.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id: int):

    for item in session["cart"].copy():
        if item["id"] == product_id:
            session["cart"].remove(item)
            break

    return view_cart()


@app.route("/myorders")
@login_required
def client_orders():
    # Display all the orders for the spesific client
    user = session["user_id"]

    orders = db.execute("SELECT order_no, status, date FROM user_orders WHERE user_id = ? ORDER BY date DESC", user)

    return render_template("client_orders.html", orders=orders)

@app.route("/view_order/<int:order_no>", methods=["GET", "POST"])
@login_required
def view_order(order_no: int):
    # View order details

    if request.method == "POST":
        status = request.form.get("status")
        db.execute("UPDATE user_orders SET status = ? WHERE order_no = ?", status, order_no)

        return redirect("/orders")
    else:
        ordered_items = []
        order_total = 0

        user_order = db.execute("SELECT user_id, status FROM user_orders WHERE order_no = ?", order_no)
        get_status = user_order[0]["status"]
        get_user_id = user_order[0]["user_id"]
        user_info = db.execute("SELECT * FROM client_info WHERE user_id = ?", get_user_id)
        print(user_info)
        orders = db.execute("SELECT product_id, quantity FROM orders WHERE order_no = ?", order_no)

        order_count = 0;
        for order in orders:
            products = db.execute("SELECT description, photo, price FROM products WHERE id = ?", order["product_id"])
            item_price = products[0]["price"]
            quantity = orders[order_count]["quantity"]
            item_total = item_price * quantity

            ordered_dict = {}
            ordered_dict["photo"] = products[0]["photo"]
            ordered_dict["description"] = products[0]["description"]
            ordered_dict["quantity"] = quantity
            ordered_dict["price"] = zar(products[0]["price"])
            ordered_dict["total"] = zar(item_total)
            order_total = order_total + (item_total)
            order_count = order_count + 1;

            ordered_items.append(ordered_dict)


        return render_template("view_order.html", ordered_items=ordered_items, order_no=order_no, order_total=zar(order_total), get_status=get_status, user_info=user_info)

@app.route("/orders")
@login_required
def all_orders():
    # Display all the orders for all clients

    orders = db.execute("SELECT order_no, status, date FROM user_orders ORDER BY date DESC")

    return render_template("all_orders.html", orders=orders)


@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id: int):

    if request.method == "POST":
        description = request.form.get("description")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        current_photo = db.execute("SELECT photo FROM products WHERE id= ?", product_id)

        # check if the post request has the file part
        if 'picture' not in request.files:
            flash('No file part')
            return render_template("apology.html",message="Error uploading picture, please try again")
        file = request.files['picture']
        # if user does not select file, browser also
        # submit an empty part without filename
        # if file.filename == '':
            # Delete current photo

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = ("/static/product_images/"+filename)

            # Save the image to the "UPLOAD_FOLDER" path on the server
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Delete current photo
        else:
            image_path = current_photo[0]["photo"]

        # Save entry to the database
        # db.execute("INSERT INTO users (username, hash,account_type) VALUES(?, ?, ?)",name,generate_password_hash(password),0)
        db.execute("UPDATE products SET description = ?, qty_on_hand = ?, photo = ?, price = ? WHERE id = ?", description, int(quantity), image_path, float(price), product_id)

        return redirect("/product_list")
    else:
        product = db.execute("SELECT description, qty_on_hand, photo, price FROM products WHERE id = ?", product_id)
        description = product[0]["description"]
        qty_on_hand = product[0]["qty_on_hand"]
        photo = product[0]["photo"]
        price = product[0]["price"]

        return render_template("update_product.html", description=description, qty_on_hand=qty_on_hand, photo=photo, price=price, product_id=product_id)


@app.route("/delete_product/<int:product_id>")
@login_required
def delete_product(product_id: int):

    db.execute("DELETE FROM products WHERE id=?", product_id)

    return redirect("/product_list")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = session["user_id"]
    user_exists = False

    if request.method == "POST":
        user_password = db.execute("SELECT hash FROM users WHERE id = ?", user)

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")

        # Ensure old password was entered
        if not old_password:
            return render_template("apology.html", message="Please enter your old password")
        # Ensure password was entered
        elif not new_password:
            return render_template("apology.html", message="must provide new password")
        elif not confirm_new_password:
            return render_template("apology.html",message="must provide confirm new password")

        if new_password != confirm_new_password:
            return render_template("apology.html", message="passwords do not match")
        elif not check_password_hash(user_password[0]["hash"], old_password):
            return render_template("apology.html", message="You entered an incorrect old password")
        else:
            db.execute("UPDATE users SET hash = ? WHERE id= ?", generate_password_hash(new_password), user)

        return redirect("/profile")

    else:
        clients_info = db.execute("SELECT * FROM client_info")
        # print(clients_info)

        for client in clients_info:
            if user == client["user_id"]:
                user_exists = True

        if user_exists:
            user_id = db.execute("SELECT username FROM users WHERE id=?", user)
            print(user_id)
            user_details = db.execute("SELECT fullname, building_no, street_address, city, province, postal_code, phone_number FROM client_info WHERE user_id=?", user)
            print(user_details)

            fullname = user_details[0]["fullname"]
            building_no = user_details[0]["building_no"]
            street_address = user_details[0]["street_address"]
            city =  user_details[0]["city"]
            province = user_details[0]["province"]
            postal_code = user_details[0]["postal_code"]
            phone_number = user_details[0]["phone_number"]
        else:
            # Redirect to update profile page
            return redirect("/update_profile")

        return render_template("profile.html", username = user_id[0]["username"], fullname=fullname, building_no=building_no, street_address=street_address, city=city, province=province, postal_code=postal_code, phone_number=phone_number)

@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    user = session["user_id"]
    has_details = False

    clients_info = db.execute("SELECT * FROM client_info")
    for client in clients_info:
        if user == client["user_id"]:
            has_details = True

    if request.method == "POST":
        get_fullname = request.form.get("fullname")
        get_building = request.form.get("building")
        get_street_address = request.form.get("street")
        get_city = request.form.get("city")
        get_province = request.form.get("province")
        get_postal_code = request.form.get("postal")
        get_phone_number = request.form.get("phone")

        if has_details:
            db.execute("UPDATE client_info SET user_id = ?, fullname = ?, building_no = ?, street_address = ?, city = ?, province = ?, postal_code = ?, phone_number = ? WHERE user_id = ? ",
                    user, get_fullname, get_building, get_street_address, get_city, get_province, get_postal_code, get_phone_number, user)
        else:
            # db.execute("INSERT INTO products (description, qty_on_hand, photo, price) VALUES(?, ?, ?, ?)",description, int(quantity), image_path, float(price))
            db.execute("INSERT INTO client_info (user_id, fullname, building_no, street_address, city, province, postal_code, phone_number) VALUES(?,?,?,?,?,?,?,?)",
                        user, get_fullname, get_building, get_street_address, get_city, get_province, get_postal_code, get_phone_number)

        return redirect("/profile")

    else:

        if has_details:
            user_details = db.execute("SELECT * FROM client_info WHERE user_id=?", user)

            fullname = user_details[0]["fullname"]
            building_no = user_details[0]["building_no"]
            street_address = user_details[0]["street_address"]
            city =  user_details[0]["city"]
            province = user_details[0]["province"]
            postal_code = user_details[0]["postal_code"]
            phone_number = user_details[0]["phone_number"]
        else:
            fullname = ""
            building_no = ""
            street_address = ""
            city =  ""
            province = ""
            postal_code = ""
            phone_number = ""

        return render_template("update_profile.html", fullname=fullname, building_no=building_no, street_address=street_address, city=city, province=province, postal_code=postal_code, phone_number=phone_number)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_order_number():
    # Generate a unique order number using the date time and weekday
    today = datetime.today()
    order_number = str(today.second) + str(today.minute) + str(today.month) + str(today.day)  + str(today.year) + str(today.weekday()) + str(today.hour)

    return order_number


