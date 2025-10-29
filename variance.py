import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection 

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Customer Feedback", layout="centered")

# ==========================================
# GOOGLE SHEETS CONNECTION & URL
# ==========================================

# NOTE: This assumes 'feedback_submissions_url' and 'gcp_service_account' are
# correctly set up in your .streamlit/secrets.toml file.
try:
    conn_feedback_submissions = st.connection("feedback_submissions_sheet", type=GSheetsConnection)
    FEEDBACK_SUBMISSIONS_SHEET_URL = st.secrets["feedback_submissions_url"]
except Exception as e:
    st.error(f"❌ Configuration Error: Check .streamlit/secrets.toml. Error: {e}")
    FEEDBACK_SUBMISSIONS_SHEET_URL = None


# ------------------------------------------------------------------
# --- DATA SUBMISSION FUNCTION (To Google Sheets) ---
# ------------------------------------------------------------------

def save_feedback(data):
    """Writes the list of submitted feedback to the Customer Feedback Google Sheet."""
    if not data or not FEEDBACK_SUBMISSIONS_SHEET_URL:
        st.warning("⚠️ Data not saved. Google Sheet connection is not configured correctly.")
        return
        
    df_to_append = pd.DataFrame(data)
    
    try:
        conn_feedback_submissions.write(
            df=df_to_append,
            spreadsheet=FEEDBACK_SUBMISSIONS_SHEET_URL, 
            # --- UPDATED WORKSHEET NAME HERE ---
            worksheet="madina feedback", 
            ttl=0, 
            header=False, 
            append=True
        )
        st.toast("✅ Feedback submitted successfully to Google Sheet!", icon="💬")
    except Exception as e:
        # Check for common permission error (403)
        if "403" in str(e):
             st.error("❌ Permission Denied. Have you shared your Google Sheet with the service account email?")
        else:
             st.error(f"❌ Error submitting feedback to Google Sheet: {e}")

# ==========================================
# MOCK LOGIN AND STATE SETUP 
# ==========================================
full_outlets = [
    "Hilal", "Safa Super", "Azhar HP", "Azhar", "Blue Pearl", "Fida", "Hadeqat",
    "Jais", "Sabah", "Sahat", "Shams salem", "Shams Liwan", "Superstore",
    "Tay Tay", "Safa oudmehta", "Port saeed"
]

# Initialize essential session state variables
for key in ["logged_in", "selected_outlet", "submitted_feedback"]: 
    if key not in st.session_state:
        st.session_state[key] = full_outlets[0] if key == "selected_outlet" else False if key == "logged_in" else []


# ==========================================
# LOGIN MOCK-UP
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Login (Mock)")
    outlet = st.selectbox("Select your outlet", full_outlets)
    
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.selected_outlet = outlet
        st.rerun()
else:
    # ----------------------------------------
    # CUSTOMER FEEDBACK PAGE 
    # ----------------------------------------
    outlet_name = st.session_state.selected_outlet
    
    st.title("📝 Customer Feedback Form")
    st.markdown(f"Submitting feedback for **{outlet_name}**")
    st.markdown("---")

    if st.button("Logout 🚪", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.submitted_feedback = [] 
        st.rerun()
    
    st.markdown("---")

    with st.form("feedback_form", clear_on_submit=True):
        name = st.text_input("Customer Name", key="feedback_name")
        rating = st.slider("Rate Our Outlet", 1, 5, 5)
        feedback = st.text_area("Your Feedback (Required)", key="feedback_text")
        submitted = st.form_submit_button("📤 Submit Feedback", type="primary")

    if submitted:
        if name.strip() and feedback.strip():
            new_feedback = {
                "Customer Name": name,
                "Email": "N/A", 
                "Rating": f"{rating} / 5",
                "Outlet": outlet_name,
                "Feedback": feedback,
                "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.submitted_feedback.append(new_feedback)

            # Call the save function to write to Google Sheets
            save_feedback([new_feedback]) 
            
            st.success("✅ Feedback submitted successfully! The form has been cleared.")
        else:
            st.error("⚠️ Please fill **Customer Name** and **Feedback** before submitting.")
        
        st.rerun() 

    if st.session_state.submitted_feedback:
        st.markdown("---")
        st.markdown("### 🗂 Recent Customer Feedback (Display Only)")
        df = pd.DataFrame(st.session_state.submitted_feedback)
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)

        if st.button("🗑 Clear Displayed Feedback Records", type="secondary"):
            st.session_state.submitted_feedback = []
            st.rerun()
