from flask import Flask, render_template, request, redirect, url_for, Response
import mysql.connector
import matplotlib.pyplot as plt
import io
import colorsys
import base64

app = Flask(__name__, template_folder='templates')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="aset_rs"
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/asets')
def index():
    search_query = request.args.get('search', '')

    mydb = get_db_connection()
    mycursor = mydb.cursor()

    if search_query:
        sql = """
        SELECT * FROM aset 
        WHERE nama_aset LIKE %s OR kode LIKE %s OR id_kategori LIKE %s OR qr_code LIKE %s
        """
        search_term = f"%{search_query}%"
        mycursor.execute(sql, (search_term, search_term, search_term, search_term))
    else:
        mycursor.execute("SELECT * FROM aset")

    myresult = mycursor.fetchall()
    mydb.close()
    return render_template('aset_home.html', asets=myresult, search_query=search_query)



@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        id_aset = request.form['id_aset']
        nama_aset = request.form['nama_aset']
        kode = request.form['kode']
        id_kategori = request.form['id_kategori']
        qr_code = request.form['qr_code']
        
        mydb = get_db_connection()
        mycursor = mydb.cursor()
        sql = "INSERT INTO aset (id_aset, nama_aset, kode, id_kategori, qr_code) VALUES (%s, %s, %s, %s, %s)"
        val = (id_aset, nama_aset, kode, id_kategori, qr_code)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        
        return redirect(url_for('index'))
    
    return render_template('add_data.html')

@app.route('/edit_aset/<int:id_aset>', methods=['GET', 'POST'])
def edit_aset(id_aset):
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    if request.method == 'POST':
        nama_aset = request.form['nama_aset']
        kode = request.form['kode']
        id_kategori = request.form['id_kategori']
        qr_code = request.form['qr_code']
        
        sql = "UPDATE aset SET nama_aset=%s, kode=%s, id_kategori=%s, qr_code=%s WHERE id_aset=%s"
        val = (nama_aset, kode, id_kategori, qr_code, id_aset)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        
        return redirect(url_for('index'))
    
    mycursor.execute("SELECT * FROM aset WHERE id_aset=%s", (id_aset,))
    aset = mycursor.fetchone()
    mydb.close()
    return render_template('edit_aset.html', aset=aset)

@app.route('/delete_aset/<int:id_aset>', methods=['GET', 'POST'])
def delete_aset(id_aset):
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = "DELETE FROM aset WHERE id_aset=%s"
    val = (id_aset,)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()
    return redirect(url_for('index'))

@app.route('/visualize_asets')
def visualize_asets():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT id_kategori, COUNT(*) as jumlah FROM aset GROUP BY id_kategori")
    data = mycursor.fetchall()
    mydb.close()

    # Extract data for plotting
    categories = [row[0] for row in data] 
    counts = [row[1] for row in data]       

    # Plot data using matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(categories, counts, color='purple')
    plt.xlabel('Kategori Aset')
    plt.ylabel('Jumlah')
    plt.title('Jumlah Aset per Kategori')
    plt.xticks(rotation=45)

    # Simpan gambar ke buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Mengirimkan buffer ke template untuk ditampilkan
    img_str = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('visual_data.html', graph_url=img_str)

if __name__ == '__main__':
    app.run(debug=True)