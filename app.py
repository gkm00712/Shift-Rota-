import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# 1. App Configuration
st.set_page_config(page_title="CHP Shift Rota Perpetual", layout="centered", initial_sidebar_state="collapsed")

# Inject Custom CSS for Dark Theme and Mobile Padding reduction
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
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
# Updated cycle with suffixes for 1st and 2nd days
CYCLE = ['M1', 'M2', 'E1', 'E2', 'N1', 'N2', 'O', 'G']

# Base Date is set to May 28, 2026 to sync perfectly with user's live data
BASE_DATE = date(2026, 5, 28)

# Group offsets calibrated to the May 28, 2026 base date
OFFSETS = {
    'A': 3,   # 2nd Evening (E2)
    'B': 5,   # 2nd Night (N2)
    'C': 7,   # General (G)
    'D': 1    # 2nd Morning (M2)
}

HOLIDAYS = {
    "01-26": "Republic Day", "03-04": "Holi", "03-21": "Eid-Ul-Fitr",
    "08-15": "Independence Day", "10-02": "Gandhi Jayanti",
    "10-20": "DUSSEHRA", "11-24": "Gurunanak Jayanti", "12-25": "Christmas Day"
}

# Updated get_shift function to handle Sunday/Holiday logic for General shifts
def get_shift(target_date, group_name, is_holiday):
    delta = (target_date - BASE_DATE).days
    idx = (delta + OFFSETS[group_name]) % 8
    shift = CYCLE[idx]
    
    # Rule: If it's a General Shift ('G') AND the day is Sunday (6) or a Holiday, make it an Off day ('O')
    if shift == 'G':
        if target_date.weekday() == 6 or is_holiday:
            return 'O'
            
    return shift

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

# 4. Mobile Quick-Glance Dashboard
if view_mode == "Continuous (Today Onwards)":
    st.markdown(f"### 📍 Today's Shifts ({today.strftime('%d-%b')})")
    
    # Check if today is a holiday for the quick-glance calculation
    today_holiday_str = HOLIDAYS.get(today.strftime("%m-%d"), "")
    is_today_holiday = bool(today_holiday_str)
    
    col1, col2, col3, col4 = st.columns(4)
    s_A = get_shift(today, 'A', is_today_holiday)
    s_B = get_shift(today, 'B', is_today_holiday)
    s_C = get_shift(today, 'C', is_today_holiday)
    s_D = get_shift(today, 'D', is_today_holiday)

    col1.metric("Grp A", s_A)
    col2.metric("Grp B", s_B)
    col3.metric("Grp C", s_C)
    col4.metric("Grp D", s_D)
    
    if is_today_holiday:
         st.info(f"🎉 Today is a Holiday: {today_holiday_str} (General shifts marked as 'O')")
         
    st.markdown("---")

# 5. Generate Rota Data
rota_data = []
for i in range(num_days):
    if view_mode == "Continuous (Today Onwards)":
        curr_date = start_date + timedelta(days=i)
    else:
        curr_date = date(sel_year, sel_month, i + 1)
        
    date_str_mm_dd = curr_date.strftime("%m-%d")
    holiday_name = HOLIDAYS.get(date_str_mm_dd, "")
    is_holiday = bool(holiday_name)

    row = {
        "Date": curr_date.strftime("%d-%b"), 
        "Day": curr_date.strftime("%a"),     
        "A": get_shift(curr_date, 'A', is_holiday),
        "B": get_shift(curr_date, 'B', is_holiday),
        "C": get_shift(curr_date, 'C', is_holiday),
        "D": get_shift(curr_date, 'D', is_holiday),
        "Holiday": holiday_name
    }
    rota_data.append(row)

df = pd.DataFrame(rota_data)

# 6. Styling the DataFrame for Dark Theme
def highlight_shifts(val):
    # Updated to apply colors to the suffixed shift names
    colors = {
        'M1': ('#D4A373', '#000000'), 
        'M2': ('#D4A373', '#000000'), 
        'E1': ('#90323D', '#FFFFFF'), 
        'E2': ('#90323D', '#FFFFFF'), 
        'N1': ('#212F45', '#FFFFFF'), 
        'N2': ('#212F45', '#FFFFFF'), 
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
<b>Timings:</b> M1/M2 (07-14) | E1/E2 (14-22) | N1/N2 (22-07) <br>
<i>Note: General shifts ('G') automatically convert to Off ('O') on Sundays and Holidays.</i>
</div>
""", unsafe_allow_html=True)
