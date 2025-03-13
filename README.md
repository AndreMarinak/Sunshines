# Sunshines App


Sunshines is an inspiration from THON at Penn State where users could submit anonyomous messages to be reviewed/revealed to everyone at the end of a meeting. I first saw this created by Matthew-Holowsko, who made https://sunshines.app. However, this version here has a branch to allow users to submit pictures. This project was made in just under 6 hours with the help of Cursor. 


Note: The main branch works with messages ONLY. Pick "Messages-AND-Pictures" for both.


## 🌟 Features
- Create rooms with unique codes for collecting submissions
- Send messages and images without accounts
- See submissions in real-time
- Control when submissions close
- Upload images easily
- Works great on mobile

## 🛠️ What's Under the Hood
- Flask (Python) backend
- Firebase Firestore database
- Cloudinary for image storage
- Deployed on Railway


## 🚂 Deploy to Railway
1. Create a Railway account at [railway.app](https://railway.app)

2. Connect your GitHub repo to a new Railway project

3. Add these environment variables:
   - `FIREBASE_CREDENTIALS`: Your Firebase JSON contents
   - `CLOUDINARY_CONFIG`: Your Cloudinary JSON contents

4. Railway handles the rest! It'll give you a URL to access your app.


## 🔒 Keeping Things Secure
- Never commit your credentials to the repo
- Check out these helpful tutorials:
  - [GitIgnore Tutorial by Evan Gudmestad](https://www.youtube.com/watch?v=4Puzc9NnEzo)
  - [DotEnv Tutorial by The Coding Train](https://www.youtube.com/watch?v=17UVejOw3zA)


## 📝 How to Use
- **Create a room**: Click "Create Room" and save your room code and admin link
- **Join a room**: Enter the room code and start submitting
- **Send stuff**: Type messages or upload images
- **Manage your room**: Use the admin link to close submissions or delete the room when done

