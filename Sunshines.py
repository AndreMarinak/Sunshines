from flask import Flask, request, jsonify, render_template, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import random, string
import os
import json

#Welcome to Sunshines - a simple app for creating rooms where people can submit messages.


# Setting up our Flask app - this is what powers our web server
app = Flask(__name__)

# Firebase setup
# Make sure you've got your Firebase credentials file in the right place
local_cred_path = "your-firebase-service-account.json"

if os.path.exists(local_cred_path):
    cred = credentials.Certificate(local_cred_path)
else:
    raise ValueError("Firebase credentials file not found at the specified path.")

firebase_admin.initialize_app(cred)
db = firestore.client()

# Creates a random room code like "ABC123" 
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Generates a secure token for room owners (there is no authentication, only a link to the room)
def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=100))

# Creates a fresh new room and returns the room code and secret token
@app.route('/create-room', methods=['POST'])
def create_room():
    room_code = generate_room_code()
    token = generate_token()
    db.collection("rooms").document(room_code).set({"messages": [], "submissions_closed": False, "token": token})
    return jsonify({"room_code": room_code, "token": token})

# The landing page
@app.route('/')
def home():
    return render_template("index.html")

# The page where people can submit their messages to a room
@app.route('/room/<room_code>/submit')
def submit_room(room_code):
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        return render_template("submissions.html", room_code=room_code)
    return render_template("error.html")

# The review page where room owners can see all the submitted messages
# Only admin link can do this
@app.route('/room/<room_code>/review')
def review_room(room_code):
    token = request.args.get("token")
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        room_data = room_ref.to_dict()
        if room_data.get("token") == token:
            return render_template("review.html", room_code=room_code)
        else:
            return render_template("error.html")
    return render_template("error.html")

# Checks if a room exists when someone tries to join 
@app.route('/join-room', methods=['POST'])
def join_room():
    data = request.json
    room_code = data.get("room_code")
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Room not found"})

# Adds a new message to the room - as long as submissions are still open
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    room_code = data.get("room_code")
    message = data.get("message")
    if not room_code or not message:
        return jsonify({"status": "error", "message": "Invalid input"})
    room_ref = db.collection("rooms").document(room_code)
    room_snapshot = room_ref.get()
    room_data = room_snapshot.to_dict()
    if room_data.get("submissions_closed"):
        return jsonify({"status": "closed", "message": "Submissions are closed for this room"})
    room_ref.update({"messages": firestore.ArrayUnion([message])})
    return jsonify({"status": "success"})

# Fetches all messages for a room
@app.route('/get-messages/<room_code>', methods=['GET'])
def get_messages(room_code):
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        return jsonify({"messages": room_ref.to_dict().get("messages", [])})
    return jsonify({"status": "error", "message": "Room not found"})

# Locks a room so no more messages can be submitted
@app.route('/close-submissions', methods=['POST'])
def close_submissions():
    data = request.json
    room_code = data.get("room_code")
    room_ref = db.collection("rooms").document(room_code)
    room_ref.update({"submissions_closed": True})
    return jsonify({"status": "success"})

#Deletes a room
@app.route('/delete-room/<room_code>', methods=['DELETE'])
def delete_room(room_code):
    token = request.args.get("token")
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        room_data = room_ref.to_dict()
        if room_data.get("token") == token:
            room_ref.reference.delete()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
    return jsonify({"status": "error", "message": "Room not found"}), 404

#Another way to delete a room, typically used when closing the browser
@app.route('/delete-room-on-close', methods=['POST'])
def delete_room_on_close():
    data = request.json
    room_code = data.get("room_code")
    token = data.get("token")
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        room_data = room_ref.to_dict()
        if room_data.get("token") == token:
            room_ref.reference.delete()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
    return jsonify({"status": "error", "message": "Room not found"}), 404

#Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404

#Invalid URL
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html"), 500

#Host locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
