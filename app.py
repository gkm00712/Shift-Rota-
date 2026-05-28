import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# 1. App Configuration
st.set_page_config(page_title="CHP Shift Rota Perpetual", layout="wide")

st.title("🏭 CHP-Operation Department Shift Rota")
st.markdown("**NTPC Limited Unchahar | Safety Begins with Teamwork**")

# 2. Rota Logic Setup
# The core 8-day cycle derived from the 2026 roster
CYCLE = ['M', 'M', 'E', 'E', 'N', 'N', 'O', 'G']

# Base Date: January 1, 2026
BASE_DATE = date(2026, 1, 1)

# Group offsets calculated to match the exact Jan 1, 2026 schedule from the document
OFFSETS = {
    'Group I': 4,   # Starts on first 'N'
    'Group II': 0,  # Starts on first 'M'
    'Group III': 2, # Starts on first 'E'
    'Group IV': 6   # Starts on 'O'
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

# 3. Sidebar Navigation
st.sidebar.header("📅 Select Timeframe")
sel_year = st.sidebar.number_input("Year", min_value=2024, max_value=2050, value=2026, step=1)
sel_month = st.sidebar.selectbox("Month", range(1, 13), format_func=lambda x: calendar.month_name[x])

# 4. Helper Function: Calculate Shift
def get_shift(target_date, group_name):
    # Calculate the number of days since the base date
    delta = (target_date - BASE_DATE).days
    # Use modulo 8 arithmetic to find the current position in the cycle
    idx = (delta + OFFSETS[group_name]) % 8
    return CYCLE[idx]

# 5. Generate Rota Data for the Selected Month
num_days = calendar.monthrange(sel_year, sel_month)[1]
rota_data = []

for day in range(1, num_days + 1):
    curr_date = date(sel_year, sel_month, day)
    date_str_mm_dd = curr_date.strftime("%m-%d")
    
    # Check for holidays
    holiday = HOLIDAYS.get(date_str_mm_dd, "")

    row = {
        "Date": curr_date.strftime("%d-%b-%Y"),
        "Day": curr_date.strftime("%A"),
        "Group I": get_shift(curr_date, 'Group I'),
        "Group II": get_shift(curr_date, 'Group II'),
        "Group III": get_shift(curr_date, 'Group III'),
        "Group IV": get_shift(curr_date, 'Group IV'),
        "Remarks / Holiday": holiday
    }
    rota_data.append(row)

df = pd.DataFrame(rota_data)

# 6. Styling the DataFrame
def highlight_shifts(val):
    """Applies background colors to shifts for easier reading."""
    colors = {
        'M': '#FFE4B5', # Moccasin (Morning)
        'E': '#FFB6C1', # Light Pink (Evening)
        'N': '#ADD8E6', # Light Blue (Night)
        'O': '#D3D3D3', # Light Grey (Off)
        'G': '#98FB98'  # Pale Green (General)
    }
    bg_color = colors.get(val, '')
    return f'background-color: {bg_color}; font-weight: bold; text-align: center;' if bg_color else ''

# Apply styling specifically to the group columns
styled_df = df.style.map(
    highlight_shifts, 
    subset=['Group I', 'Group II', 'Group III', 'Group IV']
)

# 7. UI Output
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Footer Information
st.markdown("---")
st.markdown("""
**Shift Timings:**
* **M (Morning):** 07:00 to 14:00
* **E (Evening):** 14:00 to 22:00
* **N (Night):** 22:00 to 07:00
""")
