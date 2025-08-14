# components/forms.py - Reusable Form Components
import streamlit as st
from PIL import Image
import base64
import io
from utils.validators import validate_email, validate_password, validate_pincode
from utils.auth import hash_password
from utils.database import save_user_to_db, check_user_exists

def profile_picture_uploader(key_suffix=""):
    """Reusable profile picture uploader component"""
    profile_picture = st.file_uploader(
        "📸 Profile Picture (Optional)", 
        type=['png', 'jpg', 'jpeg'],
        key=f"profile_pic_{key_suffix}",
        help="Upload a profile picture (PNG, JPG, JPEG formats only)"
    )
    
    if profile_picture:
        image = Image.open(profile_picture)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(image, caption="Profile Picture Preview", width=150)
        return image
    return None

def personal_info_form(key_suffix=""):
    """Personal information form component"""
    st.subheader("👤 Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input(
            "First Name*", 
            key=f"fname_{key_suffix}",
            placeholder="Enter your first name"
        )
    with col2:
        last_name = st.text_input(
            "Last Name*", 
            key=f"lname_{key_suffix}",
            placeholder="Enter your last name"
        )
    
    return first_name, last_name

def account_info_form(key_suffix=""):
    """Account information form component"""
    st.subheader("🔐 Account Information")
    
    username = st.text_input(
        "Username*", 
        key=f"username_{key_suffix}",
        placeholder="Choose a unique username"
    )
    
    email = st.text_input(
        "Email Address*", 
        key=f"email_{key_suffix}",
        placeholder="your.email@example.com"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input(
            "Password*", 
            type="password", 
            key=f"password_{key_suffix}",
            help="Password must be at least 6 characters with letters and numbers"
        )
    with col2:
        confirm_password = st.text_input(
            "Confirm Password*", 
            type="password", 
            key=f"confirm_password_{key_suffix}"
        )
    
    return username, email, password, confirm_password

def address_form(key_suffix=""):
    """Address information form component"""
    st.subheader("📍 Address Information")
    
    address_line1 = st.text_input(
        "Address Line 1*", 
        key=f"address_line1_{key_suffix}",
        placeholder="Street address, apartment, suite, etc."
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input(
            "City*", 
            key=f"city_{key_suffix}",
            placeholder="City name"
        )
    with col2:
        state = st.selectbox(
            "State*",
            ["", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"],
            key=f"state_{key_suffix}"
        )
    with col3:
        pincode = st.text_input(
            "Pincode*", 
            key=f"pincode_{key_suffix}",
            placeholder="12345 or 123456"
        )
    
    return address_line1, city, state, pincode

def user_type_selector(key_suffix=""):
    """User type selection component"""
    col1, col2 = st.columns(2)
    
    with col1:
        user_type = st.selectbox(
            "👥 Select User Type", 
            ["patient", "doctor"], 
            key=f"user_type_{key_suffix}",
            format_func=lambda x: "👨‍⚕️ Doctor" if x == "doctor" else "🏥 Patient"
        )
    
    with col2:
        if user_type == "doctor":
            st.success("🩺 Signing up as Doctor")
            st.info("Doctors can manage patients and appointments")
        else:
            st.info("🏥 Signing up as Patient")
            st.info("Patients can book appointments and view records")
    
    return user_type

def login_form_component():
    """Login form component"""
    st.markdown("### 🔑 Login to Your Account")
    
    with st.container():
        # User Type Selection
        user_type = st.selectbox(
            "Login as", 
            ["patient", "doctor"], 
            key="login_user_type",
            format_func=lambda x: "👨‍⚕️ Doctor Login" if x == "doctor" else "🏥 Patient Login"
        )
        
        # Login form
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔐 Password", type="password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            
            if submitted:
                return email, password, user_type
    
    return None, None, None

def signup_form_component():
    """Complete signup form component"""
    st.markdown("### 📝 Create New Account")
    
    with st.form("signup_form"):
        # User type selection
        user_type = user_type_selector("signup")
        
        # Personal information
        first_name, last_name = personal_info_form("signup")
        
        # Profile picture
        profile_picture = profile_picture_uploader("signup")
        
        # Account information
        username, email, password, confirm_password = account_info_form("signup")
        
        # Address information
        address_line1, city, state, pincode = address_form("signup")
        
        # Terms and conditions
        st.markdown("---")
        terms_accepted = st.checkbox(
            "I agree to the Terms and Conditions and Privacy Policy*",
            key="terms_signup"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🎉 Create Account", use_container_width=True, type="primary")
        
        if submitted:
            return {
                "user_type": user_type,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
                "address_line1": address_line1,
                "city": city,
                "state": state,
                "pincode": pincode,
                "profile_picture": profile_picture,
                "terms_accepted": terms_accepted
            }
    
    return None

def validate_signup_form(form_data):
    """Validate signup form data"""
    errors = []
    
    # Check required fields
    required_fields = ['first_name', 'last_name', 'username', 'email', 'password', 
                      'confirm_password', 'address_line1', 'city', 'state', 'pincode']
    
    for field in required_fields:
        if not form_data.get(field):
            field_name = field.replace('_', ' ').title()
            errors.append(f"{field_name} is required")
    
    # Terms acceptance
    if not form_data.get('terms_accepted'):
        errors.append("You must accept the Terms and Conditions")
    
    # Email validation
    if form_data.get('email') and not validate_email(form_data['email']):
        errors.append("Invalid email format")
    
    # Password validation
    if form_data.get('password'):
        is_valid, message = validate_password(form_data['password'])
        if not is_valid:
            errors.append(message)
    
    # Password confirmation
    if form_data.get('password') != form_data.get('confirm_password'):
        errors.append("Password and Confirm Password do not match")
    
    # Pincode validation
    if form_data.get('pincode') and not validate_pincode(form_data['pincode']):
        errors.append("Pincode must be 5-6 digits")
    
    return errors

def success_message(message, icon="✅"):
    """Display success message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(40, 167, 69, 0.1);
    ">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def error_message(message, icon="❌"):
    """Display error message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(220, 53, 69, 0.1);
    ">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def info_message(message, icon="ℹ️"):
    """Display info message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(23, 162, 184, 0.1);
    ">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)