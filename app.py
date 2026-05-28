import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# 1. App Configuration
# Sidebar is open by default so users can see the new options
st.set_page_config(page_title="CHP Shift Rota Perpetual", layout="wide", initial_sidebar_state="expanded")

# Inject Custom CSS to force a dark background and white text globally
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 CHP-Operation Department Shift Rota")
st.markdown("**NTPC Limited Unchahar | Safety Begins with Teamwork**")

# 2. Rota Logic Setup
CYCLE = ['M', 'M', 'E', 'E', 'N', 'N', 'O', 'G']

# Base Date: January 1, 2026
BASE_DATE = date(2026, 1, 1)

# Group offsets translated from I, II, III, IV to A, B, C, D
OFFSETS = {
    'Group A': 4,   # Starts on first 'N' on Jan 1, 2026
    'Group B': 0,   # Starts on first 'M' on Jan 1, 2026
    'Group C': 2,   # Starts on first 'E' on Jan 1, 2026
    'Group D': 6    # Starts on 'O' on Jan 1, 2026
}

# Fixed Holidays (Month-Day format to repeat perpetually)
HOLIDAYS = {
    "01-26": "Republic Day",
    "03-04": "Holi",
    "03-21": "Eid-Ul-Fitr",
    "08-15": "Independence Day",
    "10-02": "Gandhi Jayanti",
    "10-20": "DUSSEHRA",
    "11-24": "Gurunanak Jayanti",
    "12-25": "Christmas Day"
}

# 3. Helper Function: Calculate Shift
def get_shift(target_date, group_name):
    delta = (target_date - BASE_DATE).days
    idx = (delta + OFFSETS[group_name]) % 8
    return CYCLE[idx]

# 4. Sidebar UI for Filtering
st.sidebar.header("📅 Display Options")
view_mode = st.sidebar.radio(
    "Choose View Mode:",
    ("Continuous (Today Onwards)", "Specific Month")
)

today = date.today()

# Determine the date range based on the selected view mode
if view_mode == "Continuous (Today Onwards)":
    start_date = today
    end_date = date(today.year + 1, 1, 31)
    num_days = (end_date - start_date).days + 1
else:
    # Year and Month inputs appear only if "Specific Month" is selected
    sel_year = st.sidebar.number_input("Year", min_value=2024, max_value=2050, value=today.year, step=1)
    # Default the month dropdown to the current month
    sel_month = st.sidebar.selectbox("Month", range(1, 13), format_func=lambda x: calendar.month_name[x], index=today.month - 1)
    
    start_date = date(sel_year, sel_month, 1)
    num_days = calendar.monthrange(sel_year, sel_month)[1]

# 5. Generate Rota Data
rota_data = []

for i in range(num_days):
    if view_mode == "Continuous (Today Onwards)":
        curr_date = start_date + timedelta(days=i)
    else:
        # For a specific month, build the date directly
        curr_date = date(sel_year, sel_month, i + 1)
        
    date_str_mm_dd = curr_date.strftime("%m-%d")
    holiday = HOLIDAYS.get(date_str_mm_dd, "")

    row = {
        "Date": curr_date.strftime("%d-%b-%Y"),
        "Day": curr_date.strftime("%A"),
        "Group A": get_shift(curr_date, 'Group A'),
        "Group B": get_shift(curr_date, 'Group B'),
        "Group C": get_shift(curr_date, 'Group C'),
        "Group D": get_shift(curr_date, 'Group D'),
        "Remarks / Holiday": holiday
    }
    rota_data.append(row)

df = pd.DataFrame(rota_data)

# 6. Styling the DataFrame for Dark Theme
def highlight_shifts(val):
    """Applies high-contrast dark theme colors to shifts."""
    colors = {
        'M': ('#D4A373', '#000000'), # Sand background -> Black text
        'E': ('#90323D', '#FFFFFF'), # Muted Dark Red -> White text
        'N': ('#212F45', '#FFFFFF'), # Deep Blue -> White text
        'O': ('#3E4C5E', '#FFFFFF'), # Slate Grey -> White text
        'G': ('#2D6A4F', '#FFFFFF')  # Forest Green -> White text
    }
    
    if val in colors:
        bg_color, text_color = colors[val]
        return f'background-color: {bg_color}; color: {text_color}; font-weight: bold; text-align: center;'
    return ''

styled_df = df.style.map(
    highlight_shifts, 
    subset=['Group A', 'Group B', 'Group C', 'Group D']
)

# 7. UI Output
# If in continuous mode, restrict height to enable scrolling. 
# If specific month, omit the height parameter to let it fit the data naturally.
if view_mode == "Continuous (Today Onwards)":
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=700)
else:
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Footer Information
st.markdown("---")
st.markdown("""
**Shift Timings:**
* **M (Morning):** 07:00 to 14:00
* **E (Evening):** 14:00 to 22:00
* **N (Night):** 22:00 to 07:00
""")
