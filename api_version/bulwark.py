from flask import Flask, request, render_template, redirect, url_for, session, jsonify, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from firebase_admin import credentials, auth, initialize_app, firestore
from flask import send_file
from mail import send_email_with_attachment 
from google_auth_oauthlib.flow import InstalledAppFlow
import report
import secrets
import requests
import os
import json
import subprocess
import time
import youtube2
import facebook
import instagram
from datetime import datetime


# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = "your_secret_key"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# Write the environment variable to a temporary JSON file
if os.getenv("FIREBASE_CREDENTIALS"):
    with open("firebase-adminsdk.json", "w") as f:
        f.write(os.environ["FIREBASE_CREDENTIALS"])
        
# Initialize Firebase Admin
cred = credentials.Certificate("firebase-adminsdk.json")  # Replace with your Firebase credentials file path
initialize_app(cred)
db = firestore.client()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session.get('email'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('output.html')
        
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return "Missing email or password.", 400

    try:
        user = auth.get_user_by_email(email)
        if user:
            user_instance = User(id=user.uid, email=user.email)
            login_user(user_instance)
            session['email'] = user.email
            return jsonify({"email": email}), 200
        else:
            return "Invalid credentials.", 401

    except auth.AuthError as e:
        return f"Authentication failed: {e}", 401
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/output', methods=["GET"])
@login_required
def output():
    return render_template("output.html", email=current_user.email)


@app.route('/generate/<platform>', methods=['POST'])
def generate_platform_data(platform):
    user_email = request.get_json().get('user_email')
    print(f"Generating data for {platform} with email: {user_email}")
    
    if not user_email:
        return "Invalid email. Please provide a valid email address.", 400

    try:
        # Query the 'users' collection
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', user_email).limit(1).stream()

        # Fetch the document
        user_data = None
        for doc in query:
            user_data = doc.to_dict()

        if not user_data or 'socialMedia' not in user_data:
            return "Social media data not found", 404
        
        # Extract firstname and lastname
        first_name = user_data.get("firstName", "")  # Default: "Unknown"
        last_name = user_data.get("lastName", "") 
        session['fname'] = first_name
        session['lname'] = last_name

        social_media = user_data["socialMedia"]
        
        # Handle different platforms
        if platform == 'youtube':
            platform_link = social_media.get('youtube')
            if not platform_link:
                return "No YouTube link found", 404
            import youtube2
            scores = youtube2.wholefunction(platform_link)
            
        elif platform == 'facebook':
            facebook_access = social_media.get('facebook_access')
            if not facebook_access:
                return "No Facebook access token found", 404
            import facebook
            scores = facebook.wholefunction(facebook_access)
            
        elif platform == 'instagram':
            instagram_access = social_media.get('instagram_access')
            if not instagram_access:
                return "No Instagram access token found", 404
            import instagram
            scores = instagram.wholefunction(instagram_access)
            
        elif platform == 'twitter':
            platform_link = social_media.get('twitter')
            print(platform_link)
            if not platform_link:
                return "No Twitter link found", 404
            import twitter
            scores = twitter.wholefunction(platform_link)
            
        else:
            return "Invalid platform", 400

        return jsonify(scores)

    except Exception as e:
        print(f"Error processing {platform} data:", str(e))  # Add detailed logging
        return f"An error occurred: {e}", 500


@app.route('/generate/report', methods=['POST'])
def generate_report():
    print("Entered report function ")
    try:
        print("Inside try block")
        data = request.get_json()
        
        platform_name = data.get('platform_name')
        comments_data = data.get('comments_data')
        dataurl = data.get('dataurl')
        print(platform_name, comments_data)
        if not all([platform_name, comments_data, dataurl]):
            return "Missing required data", 400
            
        # Call your report generation function
        pdf_filename = report.create_platform_report(
            platform_name=platform_name,
            comments_data=comments_data,
            dataurl=dataurl
        )
        
        # Send the generated PDF file back to the client
        return send_file(
            pdf_filename,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{platform_name}_cyberbullying_complaint_report.pdf"
        )
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return f"An error occurred: {str(e)}", 500
    
@app.route('/generate/complaint_report', methods=['POST'])
def generate_complaint_report():
    try:
        # print("Flask entered")
        data = request.get_json()
        # print(data)
        name = ""
        email = ""

        if not data:
            return jsonify({"error": "No data received"}), 400

        facebook_data = data.get("facebook", {"filtered_comments": []})
        instagram_data = data.get("instagram", {"filtered_comments": []})
        youtube_data = data.get("youtube", {"filtered_comments": []})
        twitter_data = data.get("twitter", {"filtered_comments": []})

        email = session.get('email')  
        fname = session.get('fname')
        lname = session.get('lname')
        # print(f"Logged-in user's email: {email}{fname}{lname}")
        name = fname + " " + lname  
        # print(full_name)

        pdf_filename = report.complaint_report(name,email,facebook_data, instagram_data, youtube_data, twitter_data)

        print("Report generated:", pdf_filename)

        return send_file(
            pdf_filename,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="Cyberbullying_Complaint_Report.pdf"
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/check_platform_account', methods=['POST'])
def check_platform_account():
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        platform = data.get('platform')
        
        if not user_email or not platform:
            return jsonify({"error": "Missing email or platform"}), 400
            
        print(f"Checking if user {user_email} has {platform} account")
        
        # Query the 'users' collection
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', user_email).limit(1).stream()
        
        # Fetch the document
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            
        if not user_data or 'socialMedia' not in user_data:
            return jsonify({"exists": False, "message": "User profile not found or social media data missing"}), 200
            
        # Check if platform data exists based on platform type
        social_media = user_data.get("socialMedia", {})
        
        # Different platforms have different field names in Firebase
        platform_fields = {
            'youtube': 'youtube',
            'instagram': 'instagram_access',
            'facebook': 'facebook_access',
            'twitter': 'twitter'
        }
        
        field_name = platform_fields.get(platform)
        if not field_name:
            return jsonify({"error": "Invalid platform"}), 400
            
        # Check if the platform field exists and has a non-empty value
        platform_exists = field_name in social_media and social_media[field_name]
        
        return jsonify({
            "exists": platform_exists,
            "message": f"{platform.capitalize()} account {'found' if platform_exists else 'not found'}"
        }), 200
            
    except Exception as e:
        print(f"Error checking platform account: {str(e)}")
        return jsonify({"error": str(e)}), 500

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
REDIRECT_URI = "http://localhost:5000/oauth2callback"

@app.route('/authenticate')
def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file("static/js/credentials.json", SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt='consent')
    return jsonify({'auth_url': auth_url})  # Send URL to frontend

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get("code")  # Get auth code from Google

    if not code:
        return "Error: Missing authorization code."

    # Exchange code for access token
    flow = InstalledAppFlow.from_client_secrets_file("static/js/credentials.json", SCOPES, redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)

    # Save credentials
    creds = flow.credentials
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

    print("✅ Authentication successful! Token saved.")

    # Send email after authentication
    send_email_with_attachment(
        "anushree2004321@gmail.com", 
        "Complaint Registration for Cyberbullying Attack", 
        "Dear Sir/Madam, Please find the attached cyberbullying complaint report for your review and necessary action.", 
        "Cyberbullying_Complaint_Report.pdf"
    )

    print("✅ Email sent successfully!")
    return "Authentication successful! Email sent. You can close this window."

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

# Updated routes to include Facebook and Instagram access tokens

@app.route('/edit_profile')
@login_required
def edit_profile():
    try:
        # Get user data from Firestore
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', current_user.email).limit(1).stream()
        
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            user_data['id'] = doc.id  # Save document ID for updates
        
        return render_template('edit_profile.html', user_data=user_data, email=current_user.email)
    except Exception as e:
        print(f"Error loading edit profile page: {str(e)}")
        # flash('Error loading profile data', 'error')
        return redirect(url_for('output'))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Get form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        youtube = request.form.get('youtube')
        facebook = request.form.get('facebook')
        instagram = request.form.get('instagram')
        twitter = request.form.get('twitter')
        
        # Get access tokens
        facebook_access = request.form.get('facebook_access')
        instagram_access = request.form.get('instagram_access')

        # Get current timestamp for token updates

        current_timestamp = datetime.now().isoformat()
        print(current_timestamp)
        
        # Handle profile picture upload if provided
        profile_picture_url = None
        if 'profile_picture' in request.files and request.files['profile_picture'].filename:
            # Implementation for file upload to Firebase Storage would go here
            # For now, we'll skip the actual upload and just handle the data update
            pass
            
        # Get user reference
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', current_user.email).limit(1).stream()
        
        user_ref = None
        user_data = None
        for doc in query:
            user_ref = doc.reference
            user_data = doc.to_dict()
        
        if not user_ref:
            # flash('User profile not found', 'error')
            return redirect(url_for('edit_profile'))
        
        # Check if we need to update token timestamps
        existing_social_media = user_data.get('socialMedia', {})
        existing_fb_token = existing_social_media.get('facebook_access')
        existing_insta_token = existing_social_media.get('instagram_access')

        

        # Update timestamps only if tokens have changed
        fb_token_timestamp = existing_social_media.get('facebook_token_timestamp')
        if facebook_access != existing_fb_token and facebook_access:
            fb_token_timestamp = current_timestamp

            

        insta_token_timestamp = existing_social_media.get('instagram_token_timestamp')
        if instagram_access != existing_insta_token and instagram_access:
            insta_token_timestamp = current_timestamp
        
        # Update the user document
        update_data = {
            'firstName': first_name,
            'lastName': last_name,
            'socialMedia': {
                'youtube': youtube,
                'facebook': facebook,
                'instagram': instagram,
                'twitter': twitter,
                'facebook_access': facebook_access,
                'instagram_access': instagram_access,
                'facebook_token_timestamp': fb_token_timestamp,
                'instagram_token_timestamp': insta_token_timestamp
            }
        }
        
        # Only update profile picture if a new one was uploaded
        if profile_picture_url:
            update_data['profilePicture'] = profile_picture_url
        
        # Update Firestore
        user_ref.update(update_data)
        
        # Update session data
        session['fname'] = first_name
        session['lname'] = last_name
        
        # flash('Profile updated successfully', 'success')
        return redirect(url_for('output'))
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        # flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('edit_profile'))
    
@app.route('/check_token_expiry', methods=['POST'])
def check_token_expiry():
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        platform = data.get('platform')
        
        if not user_email or not platform:
            return jsonify({"error": "Missing email or platform"}), 400
        
        # Query the 'users' collection
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', user_email).limit(1).stream()
        
        # Fetch the document
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            
        if not user_data or 'socialMedia' not in user_data:
            return jsonify({"error": "User profile not found or social media data missing", "expired": True}), 200
            
        # Get social media data
        social_media = user_data.get("socialMedia", {})
        
        # Check which platform we're validating
        if platform == 'facebook':
            # Check if Facebook token exists
            if not social_media.get('facebook_access'):
                return jsonify({"expired": True, "message": "No Facebook access token found"}), 200
                
            # Check token expiry
            token_timestamp = social_media.get('facebook_token_timestamp')
            if not token_timestamp:
                return jsonify({"expired": True, "message": "No Facebook token timestamp found"}), 200
                
            # Parse the timestamp and check if it's expired (55 days)
            from datetime import datetime, timedelta
            token_date = datetime.fromisoformat(token_timestamp.replace('Z', '+00:00'))
            current_date = datetime.now()
            expiry_date = token_date + timedelta(days=55)
            
            is_expired = current_date > expiry_date
            
            return jsonify({
                "expired": is_expired,
                "message": "Facebook token expired" if is_expired else "Facebook token valid",
                "expiry_date": expiry_date.isoformat()
            }), 200
            
        elif platform == 'instagram':
            # Check if Instagram token exists
            if not social_media.get('instagram_access'):
                return jsonify({"expired": True, "message": "No Instagram access token found"}), 200
                
            # Check token expiry
            token_timestamp = social_media.get('instagram_token_timestamp')
            if not token_timestamp:
                return jsonify({"expired": True, "message": "No Instagram token timestamp found"}), 200
                
            # Parse the timestamp and check if it's expired (55 days)
            from datetime import datetime, timedelta
            token_date = datetime.fromisoformat(token_timestamp.replace('Z', '+00:00'))
            current_date = datetime.now()
            expiry_date = token_date + timedelta(days=55)
            
            is_expired = current_date > expiry_date
            
            return jsonify({
                "expired": is_expired,
                "message": "Instagram token expired" if is_expired else "Instagram token valid",
                "expiry_date": expiry_date.isoformat()
            }), 200
            
        else:
            # For platforms that don't require tokens (YouTube, Twitter)
            return jsonify({"expired": False, "message": f"{platform} does not require access token"}), 200
            
    except Exception as e:
        print(f"Error checking token expiry: {str(e)}")
        return jsonify({"error": str(e), "expired": True}), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
