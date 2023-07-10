from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'products'
app.config['MYSQL_PORT'] = 3307

app.secret_key = 'trabajoFinal'

mysql = MySQL(app)

@app.route('/home')
def home():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return render_template('home.html', products=products)

#Administrar productos
@app.route('/admin')
def admin():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, image) VALUES (%s, %s, %s)", (name, price, image))
        conn.commit()
        cursor.close()
        return redirect('/admin')
    return render_template('add_product.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = %s, price = %s, image = %s WHERE id = %s",(name, price, image, id))
        conn.commit()
        cursor.close()
        return redirect('/admin')
    return render_template('edit_product.html', product=product)

@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete_product(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    return redirect('/admin')

#Carrito de compra
carrito = []
@app.route('/carrito')
def mostrar_carrito():
    total_carrito = sum(item['product']['price'] * item['cantidad'] for item in carrito)

    return render_template('carrito.html', carrito=carrito, total_carrito=total_carrito)

@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    product_id = request.form['product_id']
    cantidad = int(request.form['cantidad'])
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()

    producto = {
        'id': product[0],
        'name': product[1],
        'price': float(product[2]),
        'image': product[3]
    }

    global carrito
    for item in carrito:
        if item['product']['id'] == product_id:
            item['cantidad'] += cantidad
            break
    else:
        carrito.append({'product': producto, 'cantidad': cantidad})

    return redirect('/carrito')

@app.route('/eliminar_del_carrito', methods=['POST'])
def eliminar_del_carrito():
    product_id = str(request.form['product_id'])

    global carrito
    carrito = [item for item in carrito if str(item['product']['id']) != product_id]

    total_carrito = sum(item['product']['price'] * item['cantidad'] for item in carrito)

    return render_template('carrito.html', carrito=carrito, total_carrito=total_carrito)

@app.route('/borrar_carrito', methods=['POST'])
def borrar_carrito():
    carrito.clear()
    return redirect('/carrito')

if __name__ == '__main__':
    app.run(debug=True)