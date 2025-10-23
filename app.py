from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'parking.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license TEXT NOT NULL,
                    type TEXT NOT NULL,
                    slot INTEGER,
                    check_in TEXT,
                    check_out TEXT,
                    fee REAL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_number INTEGER,
                    is_occupied INTEGER
                )''')
    c.execute('SELECT COUNT(*) FROM slots')
    if c.fetchone()[0] == 0:
        for i in range(1, 11):
            c.execute('INSERT INTO slots (slot_number, is_occupied) VALUES (?, 0)', (i,))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM slots WHERE is_occupied=0')
    available = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM slots WHERE is_occupied=1')
    occupied = c.fetchone()[0]
    conn.close()
    return render_template('dashboard.html', available=available, occupied=occupied)

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        license_plate = request.form['license']
        vehicle_type = request.form['type']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('SELECT slot_number FROM slots WHERE is_occupied=0 ORDER BY slot_number LIMIT 1')
        slot = c.fetchone()
        if slot:
            slot_number = slot[0]
            check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute('INSERT INTO vehicles (license, type, slot, check_in) VALUES (?, ?, ?, ?)',
                      (license_plate, vehicle_type, slot_number, check_in_time))
            c.execute('UPDATE slots SET is_occupied=1 WHERE slot_number=?', (slot_number,))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            return "No available slots!"
    return render_template('checkin.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, license FROM vehicles WHERE check_out IS NULL')
    vehicles = c.fetchall()
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        check_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('SELECT check_in, slot FROM vehicles WHERE id=?', (vehicle_id,))
        check_in_time, slot_number = c.fetchone()
        fmt = '%Y-%m-%d %H:%M:%S'
        in_time = datetime.strptime(check_in_time, fmt)
        out_time = datetime.strptime(check_out_time, fmt)
        hours = (out_time - in_time).total_seconds() / 3600
        fee = round(hours * 2, 2)
        c.execute('UPDATE vehicles SET check_out=?, fee=? WHERE id=?', (check_out_time, fee, vehicle_id))
        c.execute('UPDATE slots SET is_occupied=0 WHERE slot_number=?', (slot_number,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('checkout.html', vehicles=vehicles)

@app.route('/vehicles')
def vehicles():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM vehicles')
    all_vehicles = c.fetchall()
    conn.close()
    return render_template('vehicles.html', vehicles=all_vehicles)

if __name__ == '__main__':
    app.run(debug=True)
