from flask import Flask,render_template,redirect,request,flash,session
from flask import current_app as app 
from datetime import datetime

from .models import *
import random
import string
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import numpy as np

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        role = request.form.get("role")
        

        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == pwd:
                session["user_id"] = this_user.id  
                session["role"] = this_user.role

                if this_user.role == "admin":
                    return redirect("/admin")
                else:
                    return redirect(f"/user_dashboard/{this_user.id}")
            else:
                return render_template("incorrect_p.html")
        else:
            return render_template("not_exist.html")

    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        mobile_number = request.form.get('mobile_number')

        if not username or not password:
            flash("Username and Password are required.", "danger")
            return redirect("/register")

        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect("/register")

        new_user = User(username=username,password=password,role='user',fullname=fullname,address=address,pin_code=pin_code,
        mobile_number=mobile_number)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route('/admin')
def admin_dashboard():
    this_user = User.query.filter_by(role="admin").first()
    lots = ParkingLot.query.all()
    
    return render_template("admin_dashboard.html",this_user=this_user, lots=lots)

@app.route('/user_dashboard/<int:user_id>', methods=['GET', 'POST'])
def user_dashboard(user_id):
    this_user = User.query.get(user_id)
    history = Reservation.query.filter_by(user_id=user_id).all()
    searched_location = None
    lots = None

    if request.method == 'POST':
        searched_location = request.form.get("location", "").strip()
        lots = ParkingLot.query.filter(
            (ParkingLot.address.ilike(f"%{searched_location}%")) |
            (ParkingLot.location_name.ilike(f"%{searched_location}%"))
        ).all()

    return render_template('user_dashboard.html',
                           this_user=this_user,
                           history=history,
                           searched_location=searched_location,
                           lots=lots)



@app.route("/add_parking_lot", methods=['GET', 'POST'])
def add_parking_lot():
    if request.method == 'POST':
        location_name = request.form.get("location_name")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        price_per_hour = request.form.get("price_per_hour")
        max_spots = int(request.form.get("max_spots"))

        lot = ParkingLot(
            location_name=location_name,
            address=address,
            pincode=pin_code,
            price_per_hour=price_per_hour,
            max_spots=max_spots
        )
        db.session.add(lot)
        db.session.commit()  

        
        for i in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)

        db.session.commit()
        flash("Parking lot and spots added successfully!", "success")
        return redirect("/admin")

    return render_template("add_parking.html")


@app.route("/edit_parking_lot/<int:lot_id>", methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        
        lot.location_name = request.form.get("location_name")
        lot.address = request.form.get("address")
        lot.pincode = request.form.get("pin_code")
        lot.price_per_hour = float(request.form.get("price"))
        lot.max_spots = int(request.form.get("max_spots"))

        db.session.commit()
        flash("Lot updated successfully.", "success")
        return redirect("/admin")

    return render_template("edit_parking_lot.html", lot=lot)


    



@app.route('/delete/<int:lot_id>', methods=["POST"])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if not lot:
        flash("Parking lot not found!", "error")
        return redirect("/admin")

    
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()

    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted!", "success")
    return redirect("/admin")

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access this page.', 'danger')
        return redirect("/login")

    user = User.query.get(user_id)

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password') 

        
        if not (fullname and address and pin_code and mobile_number):
            
            return render_template('edit_profile.html', this_user=user)

        user.fullname = fullname
        user.address = address
        user.pin_code = pin_code
        user.mobile_number = mobile_number

        

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect("/user_dashboard /{{user.id}}")

    return render_template('edit_profile.html', this_user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")



@app.route("/book_parking/<int:lot_id>", methods=["POST"])
def book_parking(lot_id):
    
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in first.")
        return redirect("/login")
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash("No available spots in this lot.")
        return redirect(f"/user_dashboard/{user_id}")

    spot.status = 'O'
    reservation = Reservation(user_id=user_id,start_time = datetime.utcnow() ,spot_id=spot.id,cost=0.0)
    db.session.add(reservation)
    db.session.commit()
    flash("Parking booked successfully.")
    return redirect(f"/user_dashboard/{user_id}")

@app.route("/admin/<int:lot_id>/spots")
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template("view_spots.html", lot=lot, spots=spots)



@app.route('/registered_users')
def registered_users():
    
    users = User.query.filter_by(role='user').all()
    
    active_reservations = Reservation.query.filter_by(end_time=None).all()

    
    reservation_map = {}
    for r in active_reservations:
       reservation_map[r.user_id] = r


    return render_template("registered_users.html",users=users,reservation_map=reservation_map)




@app.route("/summary")
def summary():
    history = Reservation.query.all()
    labels = []
    data = []
    durations = []

    for r in history:
        if r.start_time and r.end_time and r.cost is not None:
            labels.append(r.start_time.strftime("%Y-%m-%d"))
            data.append(r.cost)

            duration = (r.end_time - r.start_time).total_seconds() / 3600  # in hours
            durations.append(round(duration, 2))

    return render_template("summary.html", labels=labels, data=data, durations=durations)




@app.route('/reserve_parking', methods=['POST'])
def reserve_parking():
    spot_id = request.form.get("spot_id")
    user_id = request.form.get("user_id")
    vehicle_no = request.form.get("vehicle_no")

   
    if not all([spot_id, user_id, vehicle_no]):
        flash("All fields are required.", "danger")
        return redirect(f"/user_dashboard/{user_id}")

    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        flash("Spot not found.", "danger")
        return redirect(f"/user_dashboard/{user_id}")

    if spot.status != 'A':
        flash("Selected spot is already occupied.", "danger")
        return redirect(f"/user_dashboard/{user_id}")

    
    spot.status = 'O'

    
    reservation = Reservation(
        user_id=user_id,
        spot_id=spot.id,
        vehicle_no=vehicle_no,
        start_time=datetime.utcnow(),
        end_time=None,
        cost=0.0  
    )
    
    db.session.add(reservation)
    db.session.commit()

    flash("Parking spot reserved successfully!", "success")
    return redirect(f"/user_dashboard/{user_id}")




@app.route("/release_parking/<int:reservation_id>", methods=["GET", "POST"])
def release_parking(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if request.method == "POST":
        if reservation.end_time:
            flash("This reservation has already been released.", "warning")
            return redirect(f"/user_dashboard/{reservation.user_id}")

        
        reservation.end_time = datetime.utcnow()
        reservation.spot.status = 'A'
        
        
        duration = (reservation.end_time - reservation.start_time).total_seconds() / 3600
        reservation.cost = round(duration * reservation.spot.lot.price_per_hour, 2)

        db.session.commit()

        flash(f"Reservation {reservation.id} released successfully. Total cost: ₹{reservation.cost}", "success")
        return redirect(f"/user_dashboard/{reservation.user_id}")

    
    return render_template("release_parking.html", reservation=reservation)



@app.route('/admin/parking_records')
def admin_parking_records():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    reservations = Reservation.query.all()
    return render_template(
        'admin_parking_records.html',
        reservations=reservations
    )

