from flask import current_app as app,jsonify
from .models import ParkingLot, ParkingSpot, Reservation
from .database import db 



@app.route('/api/lots')
def api_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        data.append({
            'id': lot.id,
            'location_name': lot.location_name,
            'address': lot.address,
            'pincode': lot.pincode,
            'price_per_hour': lot.price_per_hour,
            'max_spots': lot.max_spots
        })
    return jsonify(data)


@app.route('/api/spots')
def api_spots():
    spots = ParkingSpot.query.all()
    data = []
    for spot in spots:
        data.append({
            'id': spot.id,
            'lot_id': spot.lot_id,
            'status': spot.status  # A or O
        })
    return jsonify(data)


@app.route('/api/reservations')
def api_reservations():
    reservations = Reservation.query.all()
    data = []
    for r in reservations:
        data.append({
            'id': r.id,
            'user_id': r.user_id,
            'spot_id': r.spot_id,
            'start_time': r.start_time.isoformat() if r.start_time else None,
            'end_time': r.end_time.isoformat() if r.end_time else None,
            'cost': r.cost,
            'vehicle_no': r.vehicle_no
        })
     
    return jsonify(data)