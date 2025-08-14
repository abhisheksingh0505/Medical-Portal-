# app.py - Global Medical Portal Application
import streamlit as st
import json
import hashlib
import re
from datetime import datetime
import pandas as pd
from PIL import Image
import io
import base64
from typing import Dict, Optional, Tuple, List

# Page Configuration
st.set_page_config(
    page_title="Global Medical Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# UTILITY FUNCTIONS
# ===============================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_pincode(pincode: str) -> bool:
    """Validate pincode format"""
    return pincode.isdigit() and len(pincode) in [5, 6]

def authenticate_user(users_db: Dict, email: str, password: str, user_type: str) -> Optional[Dict]:
    """Authenticate user login"""
    hashed_password = hash_password(password)
    users = users_db.get(f"{user_type}s", [])
    
    for user in users:
        if user['email'] == email and user['password'] == hashed_password:
            return user
    return None

def save_user_to_db(users_db: Dict, user_data: Dict, user_type: str) -> None:
    """Save user data to database"""
    user_data['created_at'] = datetime.now().isoformat()
    user_data['user_id'] = len(users_db[f"{user_type}s"]) + 1
    users_db[f"{user_type}s"].append(user_data)

def load_sample_data() -> Dict:
    """Load sample data - returns sample users for demo"""
    return {
        "patients": [
            {
                "user_type": "patient",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": hash_password("password123"),
                "address": {
                    "line1": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "pincode": "10001"
                },
                "user_id": 1,
                "created_at": datetime.now().isoformat()
            }
        ],
        "doctors": [
            {
                "user_type": "doctor",
                "first_name": "Dr. Jane",
                "last_name": "Smith",
                "username": "drjanesmith",
                "email": "jane.smith@hospital.com",
                "password": hash_password("doctor123"),
                "address": {
                    "line1": "456 Medical Center",
                    "city": "Los Angeles",
                    "state": "CA",
                    "pincode": "90210"
                },
                "user_id": 1,
                "created_at": datetime.now().isoformat()
            }
        ]
    }

def check_user_exists(users_db: Dict, email: str, user_type: str) -> bool:
    """Check if user already exists"""
    users = users_db.get(f"{user_type}s", [])
    return any(user['email'] == email for user in users)

def image_to_base64(image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# ===============================
# SESSION STATE INITIALIZATION
# ===============================

def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'users_db' not in st.session_state:
        st.session_state.users_db = load_sample_data()

# ===============================
# STYLING AND CSS
# ===============================

def load_css():
    """Load custom CSS styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        color: #ffffff;
        text-align: center;
        margin: 2rem 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subtitle */
    .subtitle {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    
    /* Welcome Cards */
    .welcome-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
    }
    
    .welcome-card-doctor {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        box-shadow: 0 10px 30px rgba(67, 233, 123, 0.3);
    }
    
    /* Form Container */
    .form-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Messages */
    .success-msg {
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .error-msg {
        background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    
    .info-msg {
        background: linear-gradient(90deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        margin: 1rem;
        padding: 1rem;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .form-container {
            padding: 2rem;
            margin: 1rem 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ===============================
# FORM COMPONENTS
# ===============================

def signup_form():
    """User registration form"""
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("### 📝 Create Your Account")
    st.markdown("Join our global medical community")
    
    with st.form("signup_form"):
        # User Type Selection
        col1, col2 = st.columns(2)
        with col1:
            user_type = st.selectbox(
                "👥 I am a:", 
                ["patient", "doctor"],
                format_func=lambda x: "🩺 Healthcare Provider" if x == "doctor" else "🏥 Patient"
            )
        
        with col2:
            if user_type == "doctor":
                st.success("🩺 Healthcare Provider Registration")
            else:
                st.info("🏥 Patient Registration")
        
        # Personal Information
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*", placeholder="Enter your first name")
        with col2:
            last_name = st.text_input("Last Name*", placeholder="Enter your last name")
        
        # Profile Picture Upload
        profile_picture = st.file_uploader(
            "📸 Profile Picture (Optional)", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a profile picture"
        )
        
        if profile_picture:
            image = Image.open(profile_picture)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(image, caption="Profile Preview", width=150)
        
        # Account Information
        st.subheader("🔐 Account Information")
        username = st.text_input("Username*", placeholder="Choose a unique username")
        email = st.text_input("Email Address*", placeholder="your.email@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password*", type="password", 
                                   help="At least 6 characters with letters and numbers")
        with col2:
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        # Address Information
        st.subheader("📍 Location Information")
        address_line1 = st.text_input("Address*", placeholder="Street address")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City*", placeholder="Your city")
        with col2:
            state = st.text_input("State/Province*", placeholder="State or Province")
        with col3:
            pincode = st.text_input("Postal Code*", placeholder="ZIP/Postal code")
        
        # Terms and Conditions
        st.markdown("---")
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
        
        # Submit Button
        submitted = st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            
            # Required fields check
            if not all([first_name, last_name, username, email, password, confirm_password, 
                       address_line1, city, state, pincode]):
                errors.append("All required fields must be filled")
            
            if not terms_accepted:
                errors.append("You must accept the Terms of Service")
            
            if not validate_email(email):
                errors.append("Please enter a valid email address")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            is_valid_password, password_message = validate_password(password)
            if not is_valid_password:
                errors.append(password_message)
            
            if pincode and not validate_pincode(pincode):
                errors.append("Postal code must be 5-6 digits")
            
            # Check if user already exists
            if check_user_exists(st.session_state.users_db, email, user_type):
                errors.append("An account with this email already exists")
            
            if errors:
                for error in errors:
                    st.markdown(f'<div class="error-msg">❌ {error}</div>', unsafe_allow_html=True)
            else:
                # Create user account
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
                
                # Save user to database
                save_user_to_db(st.session_state.users_db, user_data, user_type)
                
                st.markdown(f'<div class="success-msg">✅ Account created successfully! You can now login with your credentials.</div>', unsafe_allow_html=True)
                st.balloons()
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def login_form():
    """User login form"""
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("### 🔑 Welcome Back")
    st.markdown("Sign in to access your account")
    
    with st.form("login_form"):
        # User Type Selection
        user_type = st.selectbox(
            "Login as:", 
            ["patient", "doctor"],
            format_func=lambda x: "🩺 Healthcare Provider" if x == "doctor" else "🏥 Patient"
        )
        
        email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
        password = st.text_input("🔐 Password", type="password")
        
        remember_me = st.checkbox("Remember me")
        
        submitted = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        if submitted:
            if email and password:
                user = authenticate_user(st.session_state.users_db, email, password, user_type)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    st.markdown(f'<div class="success-msg">✅ Welcome back, {user["first_name"]}!</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">❌ Invalid email or password. Please try again.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ Please enter both email and password.</div>', unsafe_allow_html=True)
    
    # Demo accounts info
    st.markdown("---")
    st.markdown("### 🔍 Demo Accounts")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Patient Demo:**")
        st.code("Email: john.doe@example.com\nPassword: password123")
    with col2:
        st.markdown("**Doctor Demo:**")
        st.code("Email: jane.smith@hospital.com\nPassword: doctor123")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# DASHBOARD COMPONENTS
# ===============================

def user_dashboard():
    """User dashboard after login"""
    user = st.session_state.user_data
    user_type = user['user_type']
    
    # Welcome Header
    card_class = "welcome-card-doctor" if user_type == "doctor" else "welcome-card"
    icon = "👨‍⚕️" if user_type == "doctor" else "🏥"
    
    st.markdown(f'''
    <div class="{card_class}">
        <h1>{icon} Welcome, {user["first_name"]} {user["last_name"]}!</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            {user_type.title()} Dashboard | User ID: {user.get('user_id', 'N/A')}
        </p>
        <p style="opacity: 0.9;">Manage your medical journey with our comprehensive platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Dashboard Content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile Picture and Info
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Profile")
        
        if 'profile_picture' in user:
            try:
                img_data = base64.b64decode(user['profile_picture'])
                st.image(img_data, width=200, caption="Profile Picture")
            except:
                st.image("https://via.placeholder.com/200x200/cccccc/666666?text=Profile", width=200)
        else:
            st.image("https://via.placeholder.com/200x200/cccccc/666666?text=No+Photo", width=200)
        
        st.markdown("**Account Details:**")
        st.write(f"📧 Email: {user['email']}")
        st.write(f"👤 Username: {user['username']}")
        st.write(f"📍 Location: {user['address']['city']}, {user['address']['state']}")
        st.write(f"📅 Joined: {user.get('created_at', 'N/A')[:10]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Main Dashboard Content
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        if user_type == "doctor":
            st.markdown("### 🩺 Doctor Dashboard")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Patients", "127", "↗️ +5")
            with col2:
                st.metric("📅 Appointments", "8", "Today")
            with col3:
                st.metric("⭐ Rating", "4.9/5", "↗️ +0.1")
            
            # Quick Actions
            st.markdown("### ⚡ Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👥 View Patients", use_container_width=True):
                    st.info("Patient management system would open here")
                if st.button("📊 Reports", use_container_width=True):
                    st.info("Analytics dashboard would open here")
            with col2:
                if st.button("📅 Schedule", use_container_width=True):
                    st.info("Appointment scheduler would open here")
                if st.button("💊 Prescriptions", use_container_width=True):
                    st.info("Prescription manager would open here")
        
        else:  # Patient Dashboard
            st.markdown("### 🏥 Patient Dashboard")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🩺 Appointments", "3", "This month")
            with col2:
                st.metric("💊 Prescriptions", "2", "Active")
            with col3:
                st.metric("💪 Health Score", "95%", "↗️ +3%")
            
            # Quick Actions
            st.markdown("### ⚡ Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📅 Book Appointment", use_container_width=True, type="primary"):
                    st.info("Appointment booking would open here")
                if st.button("📊 Health Records", use_container_width=True):
                    st.info("Medical records would open here")
            with col2:
                if st.button("💊 Medications", use_container_width=True):
                    st.info("Medication tracker would open here")
                if st.button("💬 Contact Doctor", use_container_width=True):
                    st.info("Messaging system would open here")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent Activity
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 🔔 Recent Activity")
    
    if user_type == "doctor":
        activities = [
            "👥 New patient registration: Emma Wilson",
            "📅 Appointment scheduled for tomorrow",
            "📊 Monthly report generated successfully",
            "⭐ Received 5-star rating from patient"
        ]
    else:
        activities = [
            "💊 Medication reminder: Take evening pills",
            "📅 Upcoming appointment in 3 days",
            "🩺 Lab results available for review", 
            "💪 Health score improved to 95%"
        ]
    
    for activity in activities:
        st.success(activity)
    
    st.markdown('</div>', unsafe_allow_html=True)

def admin_panel():
    """Admin panel for managing users"""
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 👨‍💼 System Administration")
    
    # Statistics
    total_patients = len(st.session_state.users_db.get("patients", []))
    total_doctors = len(st.session_state.users_db.get("doctors", []))
    total_users = total_patients + total_doctors
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", total_users)
    with col2:
        st.metric("🏥 Patients", total_patients)
    with col3:
        st.metric("👨‍⚕️ Doctors", total_doctors)
    with col4:
        ratio = f"{(total_doctors/total_users*100):.1f}%" if total_users > 0 else "0%"
        st.metric("📊 Doctor Ratio", ratio)
    
    # Users Table
    st.markdown("### 👥 All Registered Users")
    
    if total_users > 0:
        all_users = []
        
        # Add patients to list
        for patient in st.session_state.users_db.get("patients", []):
            all_users.append({
                "ID": patient.get("user_id", "N/A"),
                "Name": f"{patient['first_name']} {patient['last_name']}",
                "Email": patient['email'],
                "Type": "Patient",
                "City": patient['address']['city'],
                "State": patient['address']['state'],
                "Joined": patient.get('created_at', 'N/A')[:10]
            })
        
        # Add doctors to list
        for doctor in st.session_state.users_db.get("doctors", []):
            all_users.append({
                "ID": doctor.get("user_id", "N/A"),
                "Name": f"{doctor['first_name']} {doctor['last_name']}",
                "Email": doctor['email'],
                "Type": "Doctor",
                "City": doctor['address']['city'],
                "State": doctor['address']['state'],
                "Joined": doctor.get('created_at', 'N/A')[:10]
            })
        
        # Display users table
        df = pd.DataFrame(all_users)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export functionality
        if st.button("📤 Export User Data"):
            json_data = json.dumps(st.session_state.users_db, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="users_data.json",
                mime="application/json"
            )
    else:
        st.info("No users registered yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# MAIN APPLICATION
# ===============================

def main():
    """Main application function"""
    initialize_session_state()
    load_css()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("## 🏥 Global Medical Portal")
        st.markdown("*Connecting healthcare worldwide*")
        
        if st.session_state.logged_in:
            user = st.session_state.user_data
            st.success(f"✅ Logged in as:")
            st.write(f"**{user['first_name']} {user['last_name']}**")
            st.write(f"*{user['user_type'].title()}*")
            
            # Navigation
            page = st.selectbox("📍 Navigate to:", ["Dashboard", "Admin Panel", "Settings"])
            
            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_data = None
                st.rerun()
        else:
            st.info("Welcome! Please sign in or create an account.")
            page = st.selectbox("📍 Get Started:", ["Login", "Sign Up", "About"])
        
        # System Statistics
        st.markdown("---")
        st.markdown("### 📊 Live Stats")
        patients_count = len(st.session_state.users_db.get('patients', []))
        doctors_count = len(st.session_state.users_db.get('doctors', []))
        st.write(f"🏥 Patients: **{patients_count}**")
        st.write(f"👨‍⚕️ Doctors: **{doctors_count}**")
        st.write(f"🌍 Total Users: **{patients_count + doctors_count}**")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Content Area
    if not st.session_state.logged_in:
        # Landing page header
        st.markdown('''
        <div style="text-align: center; margin: 2rem 0;">
            <h1 class="main-header">🏥 Global Medical Portal</h1>
            <p class="subtitle">Your Health, Our Priority - Connecting Patients and Healthcare Providers Worldwide</p>
        </div>
        ''', unsafe_allow_html=True)
        
        if page == "Sign Up":
            signup_form()
        elif page == "About":
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### 🌟 About Global Medical Portal")
            st.markdown("""
            Welcome to the **Global Medical Portal** - a comprehensive healthcare platform designed to connect patients 
            and healthcare providers worldwide. Our mission is to make quality healthcare accessible, efficient, and 
            connected across the globe.
            
            #### 🎯 Our Features:
            - **🏥 Patient Management**: Comprehensive patient records and health tracking
            - **👨‍⚕️ Healthcare Providers**: Professional tools for medical practitioners
            - **📅 Appointment System**: Easy scheduling and management
            - **📅 Appointment System**: Easy scheduling and management of appointments
            - **💬 Communication Tools**: Secure messaging between patients and doctors
            - **📊 Health Analytics**: Insights and reports for better health management
            
            Join us in revolutionizing healthcare!
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            login_form()
    else:
        if page == "Dashboard":
            user_dashboard()
        elif page == "Admin Panel":
            admin_panel()
        elif page == "Settings":
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### ⚙️ Account Settings")
            st.markdown("Manage your account settings here.")
            # Add settings options here (e.g., change password, update profile)
            st.markdown('</div>', unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()

