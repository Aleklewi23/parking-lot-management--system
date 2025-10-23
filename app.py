from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__)

# Database file
DB_FILE = "parking.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT NOT NULL,
            slot_number INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Dashboard
@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status='occupied'")
    occupied = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status='available'")
    available = cursor.fetchone()[0]
    conn.close()
    return render_template('dashboard.html', available=available, occupied=occupied)

# Check-In Vehicle
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        license_plate = request.form['license_plate']
        slot_number = request.form['slot_number']
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vehicles (license_plate, slot_number, status) VALUES (?, ?, ?)",
                       (license_plate, slot_number, 'occupied'))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('checkin.html')

# Check-Out Vehicle
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        cursor.execute("UPDATE vehicles SET status='available' WHERE id=?", (vehicle_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    # Show all occupied vehicles
    cursor.execute("SELECT id, license_plate, slot_number FROM vehicles WHERE status='occupied'")
    vehicles = cursor.fetchall()
    conn.close()
    return render_template('checkout.html', vehicles=vehicles)

# View All Vehicles
@app.route('/vehicles')
def view_vehicles():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    conn.close()
    return render_template('vehicles.html', vehicles=vehicles)

# Run the app (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
