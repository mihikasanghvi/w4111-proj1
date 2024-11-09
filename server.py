from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify, session, get_flashed_messages
from sqlalchemy import create_engine, text
from datetime import datetime, date
import random

# Initialize Flask app and configure secret key
app = Flask(__name__)
app.secret_key = '274c0bc449148203b26b9fce61d02133'

# Database URI - adjust to match your PostgreSQL setup
DATABASEURI = "postgresql://aa5477:076638@104.196.222.236/proj1part2"
engine = create_engine(DATABASEURI)

# Connect to the database
@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("Problem connecting to database")
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception:
        pass

# Define routes
@app.route('/')
def index():
    return redirect(url_for('login'))  # Redirect root route to login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query database to check if the credentials are correct
        query = text("SELECT * FROM users WHERE email = :email AND password = :password")
        result = g.conn.execute(query, {"email": email, "password": password}).fetchone()

        if result:
            session['user_id'] = result.user_id  # Store user_id in session
            #flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))  # Stay on login page if credentials are incorrect

    return render_template('login.html')

@app.before_request
def load_user():
    g.user_id = session.get('user_id')  # Load user_id into global context

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        pin = request.form['pin']
        password = request.form['password']

        # Insert new user data into the database
        insert_query = text("""
            INSERT INTO users (name, gender, email, phone_number, pin_code, password)
            VALUES (:name, :gender, :email, :phone, :pin, :password)
        """)
        g.conn.execute(insert_query, {
            "name": name,
            "gender": gender,
            "email": email,
            "phone": phone,
            "pin": pin,
            "password": password
        })
        g.conn.commit()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))  # Redirect to login page after successful signup

    return render_template('signup.html')

@app.route('/stores_db.html', methods=['GET'])
def fetch_stores():
    pin_code = request.args.get('pincode', type=int)
    service_type_id = request.args.get('service_type_id', type=int)

    query = text("SELECT store_id, service_type_id, store_name, store_pin_code FROM Store")
    filters = []
    if pin_code:
        filters.append("store_pin_code IN (CAST(:pin_code AS TEXT), CAST(:pin_code_plus_one AS TEXT), CAST(:pin_code_minus_one AS TEXT))")
    if service_type_id:
        filters.append("service_type_id = :service_type_id")

    if filters:
        query = text(f"{query} WHERE {' AND '.join(filters)}")
    
    stores = g.conn.execute(query, {
        "pin_code": pin_code,
        "pin_code_plus_one": pin_code + 1 if pin_code else None,
        "pin_code_minus_one": pin_code - 1 if pin_code else None,
        "service_type_id": service_type_id
    }).fetchall()

    store_list = [{
        'store_id': store.store_id,
        'store_name': store.store_name.strip(),
        'service_type': store.service_type_id,
        'pin_code': store.store_pin_code
    } for store in stores]

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(store_list)
    else:
        return render_template('stores_db.html', stores=store_list)


#Route to fetch store services
@app.route('/store_services.html', methods=['GET'])
def store_services():
    store_id = request.args.get('store_id', type=int)  # Get the store ID from the query parameters
    if store_id is not None:
        # Query to fetch services for the specific store
        query = text("""
            SELECT service_name, price 
            FROM services 
            WHERE store_id = :store_id
        """)
        services = g.conn.execute(query, {"store_id": store_id}).fetchall()
        
        # Create a list of services to send to the template
        service_list = [{
            'service_name': service.service_name.strip(),  # Strip extra spaces
            'price': service.price
        } for service in services]

        print("Services fetched from database for store_id {}: {}".format(store_id, service_list))  # Debug print
        return render_template('store_services.html', store_id=store_id, services=service_list)
    
    # If no store ID is provided, you might want to handle it accordingly
    flash('No store ID provided.', 'warning')
    return redirect(url_for('fetch_stores'))

@app.route('/booking1.html')
def booking_page():
    store_id = request.args.get('store_id')
    service_name = request.args.get('service_name')
    if store_id:
        # Fetch store_name from the database
        query = text("SELECT store_name FROM Store WHERE store_id = :store_id")
        result = g.conn.execute(query, {"store_id": store_id}).fetchone()
        if result:
            store_name = result.store_name.strip()
        else:
            flash('Store not found.', 'danger')
            return redirect(url_for('fetch_stores'))
    else:
        flash('No store ID provided.', 'danger')
        return redirect(url_for('fetch_stores'))
    
    if service_name:
        price_query = text("""
            SELECT price FROM services 
            WHERE store_id = :store_id AND service_name = :service_name
        """)
        price_result = g.conn.execute(price_query, {
            "store_id": store_id,
            "service_name": service_name
        }).fetchone()
        
        if price_result:
            price = price_result.price
        else:
            price = None
            flash('Service not found or price unavailable.', 'danger')
    else:
        price = None

    return render_template('booking1.html', store_id=store_id, store_name=store_name, service_name = service_name, price=price)


@app.route('/booking_confirm.html', methods=['POST'])
def booking_confirm():
    user_id = request.form.get('user_id', type=int)
    store_id = request.form.get('store_id', type=int)
    store_name = request.form.get('store_name')
    service_date = request.form.get('service_date')
    service_time = request.form.get('service_time')
    # Get the current system date for booking_date
    booking_date = date.today()

    # Validate inputs
    if not all([user_id, store_id, store_name, service_date, service_time]):
        flash('Missing booking information.', 'danger')
        return redirect(url_for('booking_page', store_id=store_id))

    # Validate that service_date is today or in the future
    service_date_obj = datetime.strptime(service_date, '%Y-%m-%d').date()
    if service_date_obj < booking_date:
        flash('Service date must be today or in the future.', 'danger')
        return redirect(url_for('booking_page', store_id=store_id))

    # Generate a random integer for booking_id
    booking_id = random.randint(100000, 999999)  # Generates a random 6-digit integer

    # Check if the booking_id already exists in the database
    check_id_query = text("SELECT 1 FROM booking WHERE booking_id = :booking_id")
    id_exists = g.conn.execute(check_id_query, {'booking_id': booking_id}).fetchone()

    # If the booking_id exists, generate a new one until it is unique
    max_attempts = 5
    attempts = 0
    while id_exists and attempts < max_attempts:
        booking_id = random.randint(100000, 999999)
        id_exists = g.conn.execute(check_id_query, {'booking_id': booking_id}).fetchone()
        attempts += 1

    if id_exists:
        flash('Failed to generate a unique booking ID. Please try again.', 'danger')
        return redirect(url_for('booking_page', store_id=store_id))

    # Insert into booking table with the random booking_id
    insert_booking_query = text("""
        INSERT INTO booking (booking_id, user_id, store_id, booking_date, service_date, service_time, store_name)
        VALUES (:booking_id, :user_id, :store_id, :booking_date, :service_date, :service_time, :store_name)
    """)
    try:
        g.conn.execute(insert_booking_query, {
            'booking_id': booking_id,
            'user_id': user_id,
            'store_id': store_id,
            'booking_date': booking_date,
            'service_date': service_date,
            'service_time': service_time,
            'store_name': store_name
        })
        g.conn.commit()
    except Exception as e:
        print(f"Error inserting booking: {e}")
        flash('Failed to create booking. Please try again.', 'danger')
        return redirect(url_for('booking_page', store_id=store_id))


    
    if store_id:
        # Fetch service_type_id from 'store' table
        service_query = text("""
            SELECT service_type_id FROM store
            WHERE store_id = :store_id
        """)
        service_result = g.conn.execute(service_query, {
            'store_id': store_id
        }).fetchone()
        g.conn.commit()
        
        if service_result:
            service_type_id = service_result.service_type_id

            # Insert into user_select
            insert_user_service_selection_query = text("""
                INSERT INTO user_select (booking_id, user_id, service_type_id)
                VALUES (:booking_id, :user_id, :service_type_id)
            """)
            try:
                g.conn.execute(insert_user_service_selection_query, {
                    'user_id': user_id,
                    'service_type_id': service_type_id,
                    'booking_id' : booking_id
                })
                g.conn.commit()
            except Exception as e:
                print(f"Error inserting user service selection: {e}")
                flash('Failed to add service selection. Please try again.', 'danger')
                return redirect(url_for('store_services', store_id=store_id))
        else:
            flash('Service type not found.', 'danger')
            return redirect(url_for('store_services', store_id=store_id))

    # Render confirmation page with booking details
    return render_template('booking_confirm.html', booking_id=booking_id, user_id=user_id)


@app.route('/cancel_book.html', methods=['GET', 'POST'])
def cancel_booking():
    user_id = g.user_id
    if user_id is None:
        flash('You need to be logged in to cancel a booking.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        if not booking_id:
            flash('Please enter a booking ID.', 'danger')
            return redirect(url_for('cancel_booking'))
        
        # Check if the booking exists and belongs to the user
        check_booking_query = text("""
            SELECT 1 FROM booking WHERE booking_id = :booking_id AND user_id = :user_id
        """)
        booking_exists = g.conn.execute(check_booking_query, {
            'booking_id': booking_id,
            'user_id': user_id
        }).fetchone()
        
        if booking_exists:
            # Begin a transaction to delete from both tables
            try:
                # Delete the associated entry in user_select table first
                delete_user_select_query = text("""
                    DELETE FROM user_select WHERE booking_id = :booking_id
                """)
                g.conn.execute(delete_user_select_query, {'booking_id': booking_id})

                # Then delete the booking from the booking table
                delete_booking_query = text("""
                    DELETE FROM booking WHERE booking_id = :booking_id AND user_id = :user_id
                """)
                g.conn.execute(delete_booking_query, {
                    'booking_id': booking_id,
                    'user_id': user_id
                })
                
                g.conn.commit()
                flash('Booking canceled successfully.', 'success')
                return redirect(url_for('cancel_booking'))
                
            except Exception as e:
                print(f"Error deleting booking: {e}")
                g.conn.rollback()  # Rollback in case of error
                flash('An error occurred while canceling the booking. Please try again.', 'danger')
                return redirect(url_for('cancel_booking'))
        else:
            flash('No booking found with the provided ID for your account.', 'warning')
            return redirect(url_for('cancel_booking'))
    else:
        return render_template('cancel_book.html', user_id=user_id)

@app.route('/home')
def home():
    return render_template('home.html')  # Display the home page after login

if __name__ == '__main__':
    app.run(debug=True)
