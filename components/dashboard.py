# components/dashboard.py - Dashboard Components
import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def user_profile_card(user_data):
    """Display user profile card"""
    user_type = user_data['user_type']
    
    # Profile header with gradient background
    if user_type == "doctor":
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        icon = "👨‍⚕️"
        title = "Doctor Profile"
    else:
        gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        icon = "🏥"
        title = "Patient Profile"
    
    st.markdown(f"""
    <div style="
        background: {gradient};
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <h1>{icon} {title}</h1>
        <h2>Welcome, {user_data['first_name']} {user_data['last_name']}!</h2>
        <p>User ID: {user_data.get('user_id', 'N/A')} | Status: Active</p>
    </div>
    """, unsafe_allow_html=True)

def profile_picture_display(user_data):
    """Display profile picture or placeholder"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if 'profile_picture' in user_data:
            try:
                img_data = base64.b64decode(user_data['profile_picture'])
                st.image(img_data, width=200, caption="Profile Picture")
            except:
                st.image("https://via.placeholder.com/200x200/cccccc/666666?text=No+Image", 
                        width=200, caption="Profile Picture")
        else:
            st.image("https://via.placeholder.com/200x200/cccccc/666666?text=No+Image", 
                    width=200, caption="No Profile Picture")

def user_information_table(user_data):
    """Display user information in a formatted table"""
    st.subheader("📋 Personal Information")
    
    # Create information dictionary
    info_data = {
        "Field": [
            "Full Name",
            "Username", 
            "Email Address",
            "User Type",
            "User ID",
            "Account Created",
            "Address",
            "City",
            "State", 
            "Pincode"
        ],
        "Information": [
            f"{user_data['first_name']} {user_data['last_name']}",
            user_data['username'],
            user_data['email'],
            user_data['user_type'].title(),
            str(user_data.get('user_id', 'N/A')),
            user_data.get('created_at', 'N/A'),
            user_data['address']['line1'],
            user_data['address']['city'],
            user_data['address']['state'],
            user_data['address']['pincode']
        ]
    }
    
    df = pd.DataFrame(info_data)
    
    # Style the dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Field": st.column_config.TextColumn("Field", width="medium"),
            "Information": st.column_config.TextColumn("Information", width="large")
        }
    )

def doctor_dashboard_metrics():
    """Display doctor-specific metrics"""
    st.subheader("🩺 Doctor Dashboard Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Patients",
            value="127",
            delta="5 new this week",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="📅 Today's Appointments", 
            value="8",
            delta="2 more than yesterday",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="📊 This Month",
            value="312",
            delta="23 more than last month",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="⭐ Rating",
            value="4.8/5",
            delta="0.2 increase",
            delta_color="normal"
        )
    
    # Appointments chart
    st.subheader("📈 Weekly Appointments")
    
    # Sample data for demonstration
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    appointments = [12, 15, 10, 18, 14, 8, 5]
    
    fig = px.bar(
        x=days, 
        y=appointments,
        title="Appointments This Week",
        labels={'x': 'Day', 'y': 'Number of Appointments'},
        color=appointments,
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def patient_dashboard_metrics():
    """Display patient-specific metrics"""
    st.subheader("🏥 Patient Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🩺 Total Visits",
            value="12",
            delta="1 this month",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="💊 Prescriptions",
            value="3",
            delta="Active prescriptions", 
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="📅 Next Appointment",
            value="Aug 20",
            delta="5 days away",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="💪 Health Score",
            value="95%",
            delta="3% improvement",
            delta_color="normal"
        )
    
    # Health progress chart
    st.subheader("📊 Health Progress")
    
    # Sample health data
    dates = pd.date_range(start='2025-01-01', end='2025-08-01', freq='M')
    health_scores = [85, 87, 89, 91, 93, 94, 95, 95]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=health_scores,
        mode='lines+markers',
        name='Health Score',
        line=dict(color='#4facfe', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Health Score Over Time",
        xaxis_title="Month",
        yaxis_title="Health Score (%)",
        yaxis=dict(range=[80, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def recent_activity_feed(user_type):
    """Display recent activity feed"""
    st.subheader("🔔 Recent Activity")
    
    if user_type == "doctor":
        activities = [
            {"time": "2 hours ago", "activity": "👥 New patient registered: John Smith", "type": "info"},
            {"time": "4 hours ago", "activity": "📅 Appointment completed with Sarah Johnson", "type": "success"},
            {"time": "1 day ago", "activity": "💊 Prescription updated for Mike Wilson", "type": "warning"},
            {"time": "2 days ago", "activity": "📊 Monthly report generated", "type": "info"},
            {"time": "3 days ago", "activity": "🏆 Received 5-star rating from patient", "type": "success"}
        ]
    else:
        activities = [
            {"time": "1 hour ago", "activity": "💊 Prescription reminder: Take evening medication", "type": "warning"},
            {"time": "1 day ago", "activity": "📅 Appointment booked for Aug 20, 2025", "type": "info"},
            {"time": "3 days ago", "activity": "🩺 Check-up completed with Dr. Smith", "type": "success"},
            {"time": "1 week ago", "activity": "📊 Health score improved to 95%", "type": "success"},
            {"time": "2 weeks ago", "activity": "🔔 Lab results available in portal", "type": "info"}
        ]
    
    for activity in activities:
        if activity["type"] == "success":
            st.success(f"**{activity['time']}** - {activity['activity']}")
        elif activity["type"] == "warning":
            st.warning(f"**{activity['time']}** - {activity['activity']}")
        else:
            st.info(f"**{activity['time']}** - {activity['activity']}")

def quick_actions_panel(user_type):
    """Display quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    if user_type == "doctor":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥 View Patients", use_container_width=True, type="primary"):
                st.info("Redirecting to patient list...")
        
        with col2:
            if st.button("📅 Schedule Appointment", use_container_width=True):
                st.info("Opening appointment scheduler...")
        
        with col3:
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("Generating monthly report...")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💊 Manage Prescriptions", use_container_width=True):
                st.info("Opening prescription manager...")
        
        with col2:
            if st.button("🔔 Send Notifications", use_container_width=True):
                st.info("Opening notification center...")
        
        with col3:
            if st.button("⚙️ Settings", use_container_width=True):
                st.info("Opening settings panel...")
    
    else:  # Patient actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Book Appointment", use_container_width=True, type="primary"):
                st.info("Opening appointment booking...")
        
        with col2:
            if st.button("💊 View Prescriptions", use_container_width=True):
                st.info("Loading your prescriptions...")
        
        with col3:
            if st.button("📊 Health Records", use_container_width=True):
                st.info("Accessing health records...")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🩺 Lab Results", use_container_width=True):
                st.info("Loading lab results...")
        
        with col2:
            if st.button("💬 Message Doctor", use_container_width=True):
                st.info("Opening messaging system...")
        
        with col3:
            if st.button("⚙️ Profile Settings", use_container_width=True):
                st.info("Opening profile settings...")

def logout_section():
    """Display logout section"""
    st.markdown("---")
    st.subheader("🚪 Session Management")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("⚙️ Account Settings", use_container_width=True):
            st.info("Account settings would open here")
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.success("Logged out successfully!")
            st.rerun()

def admin_statistics_dashboard(users_db):
    """Display admin statistics dashboard"""
    st.subheader("📊 System Statistics")
    
    # Calculate statistics
    total_patients = len(users_db.get("patients", []))
    total_doctors = len(users_db.get("doctors", []))
    total_users = total_patients + total_doctors
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", total_users)
    with col2:
        st.metric("🏥 Patients", total_patients)
    with col3:
        st.metric("👨‍⚕️ Doctors", total_doctors)
    with col4:
        ratio = f"{(total_doctors/total_users*100):.1f}%" if total_users > 0 else "0%"
        st.metric("📈 Doctor Ratio", ratio)
    
    # User distribution chart
    if total_users > 0:
        fig = px.pie(
            values=[total_patients, total_doctors],
            names=['Patients', 'Doctors'],
            title="User Distribution",
            color_discrete_sequence=['#4facfe', '#667eea']
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No users registered yet.")

def users_management_table(users_db):
    """Display users management table"""
    st.subheader("👥 All Registered Users")
    
    all_users = []
    
    # Add patients
    for patient in users_db.get("patients", []):
        all_users.append({
            "ID": patient.get("user_id", "N/A"),
            "Name": f"{patient['first_name']} {patient['last_name']}",
            "Email": patient['email'],
            "Type": "Patient",
            "City": patient['address']['city'],
            "State": patient['address']['state'],
            "Created": patient.get('created_at', 'N/A')[:10] if patient.get('created_at') else 'N/A'
        })
    
    # Add doctors
    for doctor in users_db.get("doctors", []):
        all_users.append({
            "ID": doctor.get("user_id", "N/A"),
            "Name": f"{doctor['first_name']} {doctor['last_name']}",
            "Email": doctor['email'],
            "Type": "Doctor",
            "City": doctor['address']['city'],
            "State": doctor['address']['state'],
            "Created": doctor.get('created_at', 'N/A')[:10] if doctor.get('created_at') else 'N/A'
        })
    
    if all_users:
        df = pd.DataFrame(all_users)
        
        # Add filtering options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox("Filter by Type:", ["All", "Patient", "Doctor"])
        with col2:
            search_term = st.text_input("Search by Name or Email:")
        
        # Apply filters
        if filter_type != "All":
            df = df[df['Type'] == filter_type]
        
        if search_term:
            df = df[df['Name'].str.contains(search_term, case=False, na=False) | 
                   df['Email'].str.contains(search_term, case=False, na=False)]
        
        # Display table with styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("User ID", width="small"),
                "Name": st.column_config.TextColumn("Full Name", width="large"),
                "Email": st.column_config.TextColumn("Email", width="large"),
                "Type": st.column_config.TextColumn("User Type", width="medium"),
                "City": st.column_config.TextColumn("City", width="medium"),
                "State": st.column_config.TextColumn("State", width="small"),
                "Created": st.column_config.TextColumn("Join Date", width="medium")
            }
        )
        
        st.caption(f"Showing {len(df)} of {len(all_users)} users")
    else:
        st.info("📝 No users registered yet. Users will appear here after registration.")