"""
Sunshines App - A fun way to collect anonymous messages and images!

This app was inspired by THON at Penn State where users submit anonymous messages
to be reviewed and revealed at the end of a meeting. Originally created by 
Matthew-Holowsko (https://sunshines.app), this version adds image support.

Built with Cursor in under 6 hours
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import random, string
import os
import json
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
local_cred_path = "your-firebase-service-account.json" #CHANGE THIS TO YOUR FIREBASE SERVICE ACCOUNT JSON FILE PATH

if os.path.exists(local_cred_path):
    cred = credentials.Certificate(local_cred_path)
else:
    raise ValueError("Firebase credentials file not found at the specified path.")

firebase_admin.initialize_app(cred)
db = firestore.client()

# Creates a random 6-character room code using letters and numbers
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Creates a secure 100-character token for room admin access
def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=100))

# Makes sure we don't accidentally create a room with a code that already exists
def generate_unique_room_code():
    while True:
        room_code = generate_room_code()
        room_ref = db.collection("rooms").document(room_code).get()
        if not room_ref.exists:
            return room_code

# Load Cloudinary credentials from JSON
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

# Initialize Cloudinary with credentials from JSON
cloudinary.config(
    cloud_name=config_data["cloud_name"],
    api_key=config_data["api_key"],
    api_secret=config_data["api_secret"]
)

# Creates a new room and returns the room code and admin token
@app.route('/create-room', methods=['POST'])
def create_room():
    room_code = generate_unique_room_code()
    token = generate_token()
    db.collection("rooms").document(room_code).set({"messages": [], "submissions_closed": False, "token": token})
    return jsonify({"room_code": room_code, "token": token})

# The landing page where users can create or join rooms
@app.route('/')
def home():
    return render_template("index.html")

# The page where users can submit messages to a specific room
@app.route('/room/<room_code>/submit')
def submit_room(room_code):
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        return render_template("submissions.html", room_code=room_code)
    return render_template("error.html")

# The admin page where room creators can review all submissions
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

# Checks if a room exists when a user tries to join
@app.route('/join-room', methods=['POST'])
def join_room():
    data = request.json
    room_code = data.get("room_code")
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Room not found"})

# Handles text message submissions to a room
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

# Gets all messages for a room (used by the review page)
@app.route('/get-messages/<room_code>', methods=['GET'])
def get_messages(room_code):
    room_ref = db.collection("rooms").document(room_code).get()
    if room_ref.exists:
        messages = room_ref.to_dict().get("messages", [])
        return jsonify({"messages": messages})
    return jsonify({"status": "error", "message": "Room not found"})

# Lets room admins close submissions when they're ready
@app.route('/close-submissions', methods=['POST'])
def close_submissions():
    data = request.json
    room_code = data.get("room_code")
    room_ref = db.collection("rooms").document(room_code)
    room_ref.update({"submissions_closed": True})
    
    return jsonify({"status": "success"})

# Lets room admins delete a room when they're done with it
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

# Automatically deletes a room when the admin closes their browser
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

# Handles image uploads via Cloudinary
@app.route('/upload-image', methods=['POST'])
def upload_image():
    room_code = request.form.get("room_code")
    image = request.files.get("image")
    if not room_code or not image:
        return jsonify({"status": "error", "message": "Invalid input"})
    
    try:
        upload_result = cloudinary.uploader.upload(image, transformation={"width": 800, "height": 600, "crop": "limit"})
        image_url = upload_result.get('secure_url')  # Use secure_url to ensure the link works
        image_tag = f'<img src="{image_url}" alt="Image" style="max-width: 100%; height: auto;">'
        room_ref = db.collection("rooms").document(room_code)
        room_ref.update({"messages": firestore.ArrayUnion([image_tag])})
        return jsonify({"status": "success", "image_url": image_url})
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to upload image", "error": str(e)})

# Shows error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404

# Shows error page when something goes wrong on the server (incorrect link, closed room)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html"), 500

# Starts the app locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
