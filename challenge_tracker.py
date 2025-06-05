import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# File path for JSON storage
DATA_FILE = 'challenge_data.json'

def save_data():
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(st.session_state.data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data():
    """Load data from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data
        else:
            return {}
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

if 'users' not in st.session_state:
    st.session_state.users = ['Aryan', 'Priyal', 'Paarth']

# Auto-save data whenever it changes
if 'last_data_hash' not in st.session_state:
    st.session_state.last_data_hash = hash(str(st.session_state.data))

current_data_hash = hash(str(st.session_state.data))
if current_data_hash != st.session_state.last_data_hash:
    save_data()
    st.session_state.last_data_hash = current_data_hash

def calculate_weekly_points(user_data, start_date, end_date):
    """Calculate points for a specific week"""
    week_data = {}
    total_points = 0
    
    # Count activities for the week
    cold_showers = 0
    workout_days = 0
    diet_days = 0
    dsa_questions = 0
    water_days = 0
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str in user_data:
            day_data = user_data[date_str]
            if day_data.get('cold_shower', False):
                cold_showers += 1
            if day_data.get('workout', False):
                workout_days += 1
            if day_data.get('diet', False):
                diet_days += 1
            if day_data.get('dsa_question', False):
                dsa_questions += 1
            if day_data.get('water', False):
                water_days += 1
        current_date += timedelta(days=1)
    
    # Calculate points
    # Cold shower points
    total_points += cold_showers
    
    # Workout points
    if workout_days >= 5:
        total_points += 10
    elif workout_days >= 3:
        total_points += 5
    
    # Diet points
    if diet_days >= 6:
        total_points += 10
    elif diet_days >= 5:
        total_points += 6
    elif diet_days >= 3:
        total_points += 3
    
    # DSA points
    total_points += dsa_questions
    if dsa_questions >= 7:
        total_points += 3  # Bonus points
    
    # Water points
    total_points += water_days
    
    return {
        'cold_showers': cold_showers,
        'workout_days': workout_days,
        'diet_days': diet_days,
        'dsa_questions': dsa_questions,
        'water_days': water_days,
        'total_points': total_points
    }

def calculate_total_points(user_data):
    """Calculate total points for all time"""
    if not user_data:
        return 0
    
    # Get all dates and calculate total points across all weeks
    all_dates = sorted([datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in user_data.keys()])
    
    if not all_dates:
        return 0
    
    total_points = 0
    
    # Calculate points week by week from the beginning
    start_date = all_dates[0]
    end_date = all_dates[-1]
    
    current_week_start = start_date
    while current_week_start <= end_date:
        current_week_end = min(current_week_start + timedelta(days=6), end_date)
        week_stats = calculate_weekly_points(user_data, current_week_start, current_week_end)
        total_points += week_stats['total_points']
        current_week_start += timedelta(days=7)
    
    return total_points

def get_current_week_dates():
    """Get start and end dates for current week (starting from today, going back 7 days)"""
    today = datetime.now().date()
    week_start = today - timedelta(days=6)  # 6 days ago + today = 7 days total
    week_end = today
    return week_start, week_end

# Main app
st.title("🔥 5-Rule Challenge Tracker")
st.markdown("Track your daily progress for the 5-rule challenge!")

# Display rules
with st.expander("📋 Challenge Rules & Points System"):
    st.markdown("""
    **THE FIVE RULES:**
    1. COLD SHOWER EVERY MORNING
    2. 45 MINUTES OF EXERCISE 5 DAYS A WEEK
    3. FOLLOW YOUR DIET 6 DAYS A WEEK (1 Cheat Day)
    4. 1 DSA QUESTION EVERYDAY
    5. DRINK 2.5L OF WATER A DAY
    
    **POINTS SYSTEM:**
    - Cold shower: 1 point per day
    - Workout: 10 points (5+ days/week), 5 points (3-4 days/week)
    - Diet: 10 points (6+ days/week), 6 points (5 days/week), 3 points (3-4 days/week)
    - DSA: 1 point per question + 3 bonus points for 7+ questions/week
    - Water: 1 point per day
    """)

# User selection
selected_user = st.selectbox("👤 Select your name:", st.session_state.users)

# Date selection
selected_date = st.date_input("📅 Select date:", datetime.now().date())
date_str = selected_date.strftime('%Y-%m-%d')

# Initialize user data if not exists
if selected_user not in st.session_state.data:
    st.session_state.data[selected_user] = {}

if date_str not in st.session_state.data[selected_user]:
    st.session_state.data[selected_user][date_str] = {
        'cold_shower': False,
        'workout': False,
        'diet': False,
        'dsa_question': False,
        'water': False
    }

# Daily activity logging
st.subheader(f"📝 Log activities for {selected_user} on {selected_date}")

col1, col2 = st.columns(2)

with col1:
    cold_shower = st.checkbox("🚿 Cold shower", 
                             value=st.session_state.data[selected_user][date_str]['cold_shower'])
    workout = st.checkbox("💪 45min workout", 
                         value=st.session_state.data[selected_user][date_str]['workout'])
    water = st.checkbox("💧 2.5L water", 
                       value=st.session_state.data[selected_user][date_str]['water'])

with col2:
    diet = st.checkbox("🥗 Followed diet", 
                      value=st.session_state.data[selected_user][date_str]['diet'])
    dsa_question = st.checkbox("💻 DSA question", 
                              value=st.session_state.data[selected_user][date_str]['dsa_question'])

# Update data and save to file
if st.button("💾 Save Progress"):
    st.session_state.data[selected_user][date_str] = {
        'cold_shower': cold_shower,
        'workout': workout,
        'diet': diet,
        'dsa_question': dsa_question,
        'water': water
    }
    if save_data():
        st.success("✅ Progress saved successfully!")
        st.balloons()
    else:
        st.error("❌ Failed to save progress. Please try again.")
        
# Add a refresh button to reload data from file
if st.button("🔄 Refresh Data"):
    st.session_state.data = load_data()
    st.success("🔄 Data refreshed from file!")
    st.rerun()

# Weekly summary
st.subheader("📊 Weekly Summary")

week_start, week_end = get_current_week_dates()
st.write(f"Week: {week_start} to {week_end} (Last 7 days including today)")

if selected_user in st.session_state.data:
    weekly_stats = calculate_weekly_points(st.session_state.data[selected_user], week_start, week_end)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🚿 Cold Showers", weekly_stats['cold_showers'], help="1 point each")
    with col2:
        st.metric("💪 Workout Days", weekly_stats['workout_days'], help="5+ days: 10pts, 3-4 days: 5pts")
    with col3:
        st.metric("🥗 Diet Days", weekly_stats['diet_days'], help="6+ days: 10pts, 5 days: 6pts, 3-4 days: 3pts")
    with col4:
        st.metric("💻 DSA Questions", weekly_stats['dsa_questions'], help="1pt each + 3 bonus for 7+")
    with col5:
        st.metric("💧 Water Days", weekly_stats['water_days'], help="1 point each")
    
    st.metric("🏆 **WEEKLY POINTS (Last 7 Days)**", weekly_stats['total_points'])
    
    # Calculate and display total points
    total_points = calculate_total_points(st.session_state.data[selected_user])
    st.metric("🌟 **TOTAL POINTS (All Time)**", total_points)

# Leaderboard
st.subheader("🏆 Leaderboard")

leaderboard_data = []
for user in st.session_state.users:
    if user in st.session_state.data:
        user_stats = calculate_weekly_points(st.session_state.data[user], week_start, week_end)
        total_points = calculate_total_points(st.session_state.data[user])
        leaderboard_data.append({
            'Name': user,
            'Weekly Points': user_stats['total_points'],
            'Total Points': total_points,
            'Cold Showers': user_stats['cold_showers'],
            'Workouts': user_stats['workout_days'],
            'Diet Days': user_stats['diet_days'],
            'DSA Questions': user_stats['dsa_questions'],
            'Water Days': user_stats['water_days']
        })
    else:
        leaderboard_data.append({
            'Name': user,
            'Weekly Points': 0,
            'Total Points': 0,
            'Cold Showers': 0,
            'Workouts': 0,
            'Diet Days': 0,
            'DSA Questions': 0,
            'Water Days': 0
        })

leaderboard_df = pd.DataFrame(leaderboard_data)
leaderboard_df = leaderboard_df.sort_values('Total Points', ascending=False)

# Display leaderboard as charts
col1, col2 = st.columns(2)

with col1:
    fig_weekly = px.bar(leaderboard_df, x='Name', y='Weekly Points', 
                 title='Weekly Points Leaderboard (Last 7 Days)',
                 color='Weekly Points',
                 color_continuous_scale='blues')
    fig_weekly.update_layout(showlegend=False)
    st.plotly_chart(fig_weekly, use_container_width=True)

with col2:
    fig_total = px.bar(leaderboard_df, x='Name', y='Total Points', 
                 title='Total Points Leaderboard (All Time)',
                 color='Total Points',
                 color_continuous_scale='viridis')
    fig_total.update_layout(showlegend=False)
    st.plotly_chart(fig_total, use_container_width=True)

# Display detailed leaderboard table
st.dataframe(leaderboard_df, use_container_width=True)

# Progress visualization for selected user
if selected_user in st.session_state.data and st.session_state.data[selected_user]:
    st.subheader(f"📈 {selected_user}'s Progress Over Time")
    
    # Prepare data for visualization
    user_progress = []
    for date_key, activities in st.session_state.data[selected_user].items():
        daily_points = sum([
            activities['cold_shower'],
            activities['workout'],
            activities['diet'],
            activities['dsa_question'],
            activities['water']
        ])
        user_progress.append({
            'Date': datetime.strptime(date_key, '%Y-%m-%d').date(),
            'Daily Points': daily_points,
            'Cold Shower': activities['cold_shower'],
            'Workout': activities['workout'],
            'Diet': activities['diet'],
            'DSA': activities['dsa_question'],
            'Water': activities['water']
        })
    
    if user_progress:
        progress_df = pd.DataFrame(user_progress)
        progress_df = progress_df.sort_values('Date')
        
        # Daily points line chart
        fig_line = px.line(progress_df, x='Date', y='Daily Points', 
                          title=f'{selected_user} - Daily Points',
                          markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Activity heatmap
        activities_only = progress_df[['Date', 'Cold Shower', 'Workout', 'Diet', 'DSA', 'Water']].copy()
        activities_melted = activities_only.melt(id_vars=['Date'], var_name='Activity', value_name='Completed')
        activities_melted['Completed'] = activities_melted['Completed'].astype(int)
        
        fig_heatmap = px.density_heatmap(activities_melted, x='Date', y='Activity', z='Completed',
                                       title=f'{selected_user} - Activity Completion Heatmap',
                                       color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_heatmap, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💪 Keep pushing! Consistency is key to success! 🔥")

# Data management section
with st.expander("🔧 Data Management"):
    st.markdown("**File Storage Info:**")
    if os.path.exists(DATA_FILE):
        file_size = os.path.getsize(DATA_FILE)
        last_modified = datetime.fromtimestamp(os.path.getmtime(DATA_FILE))
        st.write(f"📁 Data file: `{DATA_FILE}`")
        st.write(f"📊 File size: {file_size} bytes")
        st.write(f"🕐 Last modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show current data structure
        st.write(f"👥 Users with data: {list(st.session_state.data.keys())}")
        for user in st.session_state.data:
            entry_count = len(st.session_state.data[user])
            st.write(f"  - {user}: {entry_count} entries")
    else:
        st.write("📁 No data file found. Data will be created when you save progress.")
    
    # Manual data operations
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Force Save"):
            if save_data():
                st.success("Data saved!")
            else:
                st.error("Save failed!")
    
    with col2:
        if st.button("🔄 Force Reload"):
            st.session_state.data = load_data()
            st.success("Data reloaded!")
            st.rerun()
    
    # Export data
    if st.session_state.data:
        data_json = json.dumps(st.session_state.data, indent=2)
        st.download_button(
            label="📥 Download Data (JSON)",
            data=data_json,
            file_name=f"challenge_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )