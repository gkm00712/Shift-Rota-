import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# 1. App Configuration - 'centered' layout often behaves better on mobile
st.set_page_config(page_title="CHP Shift Rota Perpetual", layout="centered", initial_sidebar_state="collapsed")

# Inject Custom CSS for Dark Theme and Mobile Padding reduction
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    /* Reduce default padding for mobile screens */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    /* Style the Today's Shift Cards */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 CHP Shift Rota")
st.markdown("**NTPC Unchahar | Safety First**")

# 2. Rota Logic Setup
CYCLE = ['M', 'M', 'E', 'E', 'N', 'N', 'O', 'G']
BASE_DATE = date(2026, 1, 1)

# Group offsets (A=I, B=II, C=III, D=IV)
OFFSETS = {
    'A': 4,   # Starts on first 'N' 
    'B': 0,   # Starts on first 'M' 
    'C': 2,   # Starts on first 'E' 
    'D': 6    # Starts on 'O' 
}

HOLIDAYS = {
    "01-26": "Republic Day", "03-04": "Holi", "03-21": "Eid-Ul-Fitr",
    "08-15": "Independence Day", "10-02": "Gandhi Jayanti",
    "10-20": "DUSSEHRA", "11-24": "Gurunanak Jayanti", "12-25": "Christmas Day"
}

def get_shift(target_date, group_name):
    delta = (target_date - BASE_DATE).days
    idx = (delta + OFFSETS[group_name]) % 8
    return CYCLE[idx]

# 3. Sidebar UI
st.sidebar.header("📅 Display Options")
view_mode = st.sidebar.radio(
    "Choose View Mode:",
    ("Continuous (Today Onwards)", "Specific Month")
)

today = date.today()

if view_mode == "Continuous (Today Onwards)":
    start_date = today
    end_date = date(today.year + 1, 1, 31)
    num_days = (end_date - start_date).days + 1
else:
    sel_year = st.sidebar.number_input("Year", min_value=2024, max_value=2050, value=today.year, step=1)
    sel_month = st.sidebar.selectbox("Month", range(1, 13), format_func=lambda x: calendar.month_name[x], index=today.month - 1)
    start_date = date(sel_year, sel_month, 1)
    num_days = calendar.monthrange(sel_year, sel_month)[1]

# 4. Mobile Quick-Glance Dashboard (Only show if looking at current/future continuous view)
if view_mode == "Continuous (Today Onwards)":
    st.markdown(f"### 📍 Today's Shifts ({today.strftime('%d-%b')})")
    
    col1, col2, col3, col4 = st.columns(4)
    # Calculate today's shifts dynamically
    s_A = get_shift(today, 'A')
    s_B = get_shift(today, 'B')
    s_C = get_shift(today, 'C')
    s_D = get_shift(today, 'D')

    # Display in mobile-friendly metric cards
    col1.metric("Grp A", s_A)
    col2.metric("Grp B", s_B)
    col3.metric("Grp C", s_C)
    col4.metric("Grp D", s_D)
    st.markdown("---")

# 5. Generate Rota Data with Shortened Column Names
rota_data = []
for i in range(num_days):
    if view_mode == "Continuous (Today Onwards)":
        curr_date = start_date + timedelta(days=i)
    else:
        curr_date = date(sel_year, sel_month, i + 1)
        
    date_str_mm_dd = curr_date.strftime("%m-%d")
    holiday = HOLIDAYS.get(date_str_mm_dd, "")

    # Shortened keys to prevent horizontal scrolling on mobile
    row = {
        "Date": curr_date.strftime("%d-%b"), # Removed year to save space
        "Day": curr_date.strftime("%a"),     # Shortened day (e.g., 'Mon' instead of 'Monday')
        "A": get_shift(curr_date, 'A'),
        "B": get_shift(curr_date, 'B'),
        "C": get_shift(curr_date, 'C'),
        "D": get_shift(curr_date, 'D'),
        "Holiday": holiday
    }
    rota_data.append(row)

df = pd.DataFrame(rota_data)

# 6. Styling the DataFrame for Dark Theme
def highlight_shifts(val):
    colors = {
        'M': ('#D4A373', '#000000'), 
        'E': ('#90323D', '#FFFFFF'), 
        'N': ('#212F45', '#FFFFFF'), 
        'O': ('#3E4C5E', '#FFFFFF'), 
        'G': ('#2D6A4F', '#FFFFFF')  
    }
    if val in colors:
        bg_color, text_color = colors[val]
        return f'background-color: {bg_color}; color: {text_color}; font-weight: bold; text-align: center;'
    return ''

styled_df = df.style.map(
    highlight_shifts, 
    subset=['A', 'B', 'C', 'D']
)

# 7. UI Output
st.markdown("### 🗓️ Shift Schedule")
if view_mode == "Continuous (Today Onwards)":
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
else:
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Footer Information
st.markdown("---")
st.markdown("""
<div style='font-size: 0.9em; color: #ccc;'>
<b>Timings:</b> M (07-14) | E (14-22) | N (22-07)
</div>
""", unsafe_allow_html=True)
