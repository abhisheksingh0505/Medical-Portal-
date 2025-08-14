# app.py - Main Streamlit Application
import streamlit as st
import json
import hashlib
import re
from datetime import datetime
import pandas as pd
from PIL import Image
import io
import base64

# Page Configuration
st.set_page_config(
    page_title="Medical Portal - ATG",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"patients": [], "doctors": []}

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .user-type-header {
        font-size: 2rem;
        color: #2e8b57;
        text-align: center;
        margin: 1rem 0;
    }
    .dashboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .patient-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .doctor-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .form-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Utility Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def save_user_data(user_data, user_type):
    """Save user data to session state database"""
    user_data['created_at'] = datetime.now().isoformat()
    user_data['user_id'] = len(st.session_state.users_db[f"{user_type}s"]) + 1
    st.session_state.users_db[f"{user_type}s"].append(user_data)

def find_user(email, password, user_type):
    """Find user in the database"""
    hashed_password = hash_password(password)
    users = st.session_state.users_db.get(f"{user_type}s", [])
    
    for user in users:
        if user['email'] == email and user['password'] == hashed_password:
            return user
    return None

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Authentication Functions
def signup_form():
    st.markdown('<h2 class="user-type-header">🔐 Create Account</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # User Type Selection
        col1, col2 = st.columns(2)
        with col1:
            user_type = st.selectbox("Select User Type", ["patient", "doctor"], key="signup_user_type")
        
        with col2:
            st.write(f"Signing up as: **{user_type.title()}** 👨‍⚕️" if user_type == "doctor" else "Signing up as: **Patient** 🏥")
        
        # Personal Information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", key="signup_fname")
        with col2:
            last_name = st.text_input("Last Name*", key="signup_lname")
        
        # Profile Picture
        profile_picture = st.file_uploader(
            "Profile Picture", 
            type=['png', 'jpg', 'jpeg'],
            key="signup_profile_pic"
        )
        
        if profile_picture:
            image = Image.open(profile_picture)
            st.image(image, caption="Profile Picture Preview", width=150)
        
        # Account Information
        st.subheader("Account Information")
        username = st.text_input("Username*", key="signup_username")
        email = st.text_input("Email Address*", key="signup_email")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password*", type="password", key="signup_password")
        with col2:
            confirm_password = st.text_input("Confirm Password*", type="password", key="signup_confirm_password")
        
        # Address Information
        st.subheader("Address Information")
        address_line1 = st.text_input("Address Line 1*", key="signup_address_line1")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City*", key="signup_city")
        with col2:
            state = st.text_input("State*", key="signup_state")
        with col3:
            pincode = st.text_input("Pincode*", key="signup_pincode")
        
        # Submit Button
        if st.button("Create Account", type="primary", key="signup_submit"):
            # Validation
            errors = []
            
            if not all([first_name, last_name, username, email, password, confirm_password, address_line1, city, state, pincode]):
                errors.append("All required fields must be filled")
            
            if not validate_email(email):
                errors.append("Invalid email format")
            
            if password != confirm_password:
                errors.append("Password and Confirm Password do not match")
            
            is_valid_password, password_message = validate_password(password)
            if not is_valid_password:
                errors.append(password_message)
            
            if not pincode.isdigit() or len(pincode) not in [5, 6]:
                errors.append("Pincode must be 5-6 digits")
            
            # Check if user already exists
            existing_users = st.session_state.users_db.get(f"{user_type}s", [])
            if any(user['email'] == email for user in existing_users):
                errors.append("User with this email already exists")
            
            if errors:
                for error in errors:
                    st.markdown(f'<div class="error-message">❌ {error}</div>', unsafe_allow_html=True)
            else:
                # Create user data
                user_data = {
                    "user_type": user_type,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "email": email,
                    "password": hash_password(password),
                    "address": {
                        "line1": address_line1,
                        "city": city,
                        "state": state,
                        "pincode": pincode
                    }
                }
                
                # Add profile picture if uploaded
                if profile_picture:
                    user_data["profile_picture"] = image_to_base64(image)
                
                # Save user
                save_user_data(user_data, user_type)
                
                st.markdown(f'<div class="success-message">✅ Account created successfully! You can now login.</div>', unsafe_allow_html=True)
                st.balloons()
        
        st.markdown('</div>', unsafe_allow_html=True)

def login_form():
    st.markdown('<h2 class="user-type-header">🔑 Login to Your Account</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # User Type Selection
        user_type = st.selectbox("Login as", ["patient", "doctor"], key="login_user_type")
        
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("Login", type="primary", key="login_submit", use_container_width=True):
                if email and password:
                    user = find_user(email, password, user_type)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.markdown(f'<div class="success-message">✅ Login successful! Welcome back, {user["first_name"]}!</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown('<div class="error-message">❌ Invalid credentials. Please check your email and password.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-message">❌ Please fill in both email and password.</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    user = st.session_state.user_data
    user_type = user['user_type']
    
    # Header
    st.markdown(f'<h1 class="main-header">👋 Welcome, {user["first_name"]} {user["last_name"]}!</h1>', unsafe_allow_html=True)
    
    # Dashboard Card
    card_class = "doctor-card" if user_type == "doctor" else "patient-card"
    
    st.markdown(f'''
    <div class="dashboard-card {card_class}">
        <h2>🏥 {user_type.title()} Dashboard</h2>
        <p>You are successfully logged in to your {user_type} account.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # User Information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if 'profile_picture' in user:
            st.markdown("### Profile Picture")
            img_data = base64.b64decode(user['profile_picture'])
            st.image(img_data, width=200)
        else:
            st.markdown("### Profile")
            st.info("No profile picture uploaded")
    
    with col2:
        st.markdown("### Account Information")
        
        info_data = {
            "Full Name": f"{user['first_name']} {user['last_name']}",
            "Username": user['username'],
            "Email": user['email'],
            "User Type": user['user_type'].title(),
            "User ID": str(user.get('user_id', 'N/A')),
            "Account Created": user.get('created_at', 'N/A')
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
    
    # Address Information
    st.markdown("### Address Information")
    address = user['address']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Address:** {address['line1']}")
        st.write(f"**City:** {address['city']}")
    with col2:
        st.write(f"**State:** {address['state']}")
        st.write(f"**Pincode:** {address['pincode']}")
    with col3:
        if user_type == "doctor":
            st.success("🩺 Doctor Account")
        else:
            st.info("🏥 Patient Account")
    
    # Logout Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()
    
    # Statistics (for demo purposes)
    if user_type == "doctor":
        st.markdown("### Doctor Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patients", "127", "↗️ 5")
        with col2:
            st.metric("Appointments Today", "8", "↗️ 2")
        with col3:
            st.metric("This Month", "312", "↗️ 23")
    else:
        st.markdown("### Patient Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Appointments", "3", "→ 0")
        with col2:
            st.metric("Last Visit", "2 weeks ago", "")
        with col3:
            st.metric("Health Score", "95%", "↗️ 3%")

def admin_panel():
    st.markdown('<h2 class="user-type-header">👨‍💼 Admin Panel</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Statistics", "👥 All Users", "🗑️ Data Management"])
    
    with tab1:
        # Statistics
        total_patients = len(st.session_state.users_db.get("patients", []))
        total_doctors = len(st.session_state.users_db.get("doctors", []))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patients", total_patients)
        with col2:
            st.metric("Total Doctors", total_doctors)
        with col3:
            st.metric("Total Users", total_patients + total_doctors)
    
    with tab2:
        # All Users
        st.subheader("All Registered Users")
        
        all_users = []
        for patient in st.session_state.users_db.get("patients", []):
            all_users.append({
                "ID": patient.get("user_id", "N/A"),
                "Name": f"{patient['first_name']} {patient['last_name']}",
                "Email": patient['email'],
                "Type": "Patient",
                "City": patient['address']['city'],
                "State": patient['address']['state']
            })
        
        for doctor in st.session_state.users_db.get("doctors", []):
            all_users.append({
                "ID": doctor.get("user_id", "N/A"),
                "Name": f"{doctor['first_name']} {doctor['last_name']}",
                "Email": doctor['email'],
                "Type": "Doctor",
                "City": doctor['address']['city'],
                "State": doctor['address']['state']
            })
        
        if all_users:
            df = pd.DataFrame(all_users)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users registered yet.")
    
    with tab3:
        # Data Management
        st.subheader("Data Management")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.confirm("Are you sure you want to clear all user data?"):
                st.session_state.users_db = {"patients": [], "doctors": []}
                st.success("All data cleared successfully!")
                st.rerun()

# Main Application
def main():
    load_css()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="user-type-header">🏥 Medical Portal</h2>', unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            st.success(f"Logged in as: {st.session_state.user_data['first_name']} {st.session_state.user_data['last_name']}")
            st.info(f"User Type: {st.session_state.user_data['user_type'].title()}")
            
            page = st.selectbox("Navigate to:", ["Dashboard", "Admin Panel"])
        else:
            page = st.selectbox("Choose Action:", ["Login", "Sign Up"])
        
        st.markdown("---")
        st.markdown("### 📈 System Stats")
        st.write(f"Patients: {len(st.session_state.users_db.get('patients', []))}")
        st.write(f"Doctors: {len(st.session_state.users_db.get('doctors', []))}")
    
    # Main Content
    if not st.session_state.logged_in:
        st.markdown('<h1 class="main-header">🏥 Medical Portal - ATG</h1>', unsafe_allow_html=True)
        
        if page == "Sign Up":
            signup_form()
        else:
            login_form()
    else:
        if page == "Dashboard":
            dashboard()
        else:
            admin_panel()

if __name__ == "__main__":
    main()