import streamlit as st
import requests
import numpy as np
from datetime import date

# --- App Settings ---
st.set_page_config(
    page_title="Israel to ROW Salary Converter",
    page_icon="💱",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.title("About")
    st.markdown(
        """
        This application converts between salaries as they are expressed in Israel and the rest of the world. 
        
        It uses the latest available exchange rates from [exchangerate-api](https://www.exchangerate-api.com). All salaries are assumed to be *annual* salaries.
        
        Developed by Daniel Rosehill. 
        [GitHub Profile](https://github.com/danielrosehill)
        """
    )
# Function to fetch exchange rates
def get_exchange_rates():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/ILS")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        rates = data["rates"]
        return rates
    except requests.exceptions.RequestException as e:
         st.error(f"Error fetching exchange rates: {e}. Please try again later.")
         return None

# Cache the exchange rates so we don't hammer the API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_rates():
    return get_exchange_rates()

def convert_salary_israel_to_world(nis_salary, rates):
    if rates is None:
        return None, None, None

    annual_nis_salary = nis_salary * 12
    usd_salary = annual_nis_salary * rates.get("USD", 1)
    eur_salary = annual_nis_salary * rates.get("EUR", 1)
    gbp_salary = annual_nis_salary * rates.get("GBP", 1)

    return usd_salary, eur_salary, gbp_salary


def convert_salary_world_to_israel(world_salary, currency, rates):
    if rates is None:
        return None
    
    if currency == "USD":
       ils_salary = (world_salary / rates.get("USD", 1) )
    elif currency == "EUR":
       ils_salary = (world_salary / rates.get("EUR", 1) )
    elif currency == "GBP":
       ils_salary = (world_salary / rates.get("GBP", 1) )
    else:
        return None

    return ils_salary / 12


# --- Main App ---

rates = load_rates()

if rates is not None:
    tab1, tab2 = st.tabs(["🇮🇱 Israel to World", "🌎 World to Israel"])

    # --- Israel to World Tab ---
    with tab1:
        st.header("Convert Salary from Israel to Rest of World", divider="blue")
        st.markdown("Enter your monthly salary in NIS using the slider, and it will be converted.")
        
        col1, col2 = st.columns([2, 3])  # Adjusted column ratio for better layout
        
        with col1:
            nis_salary = st.slider(
                "Enter your Monthly Salary in NIS:",
                 min_value=0,
                  max_value=50000,
                  step=500,
                  value=15000,
            )
            
            if nis_salary:
                nis_salary_k = f"{nis_salary/1000:.0f}k" if nis_salary >= 1000 else f"{nis_salary}"

                st.markdown(f"<p style='font-size: 2em; font-weight: bold;'>Israel 🇮🇱 =  <span style='color: #117A65;'>{nis_salary_k}</span></p>", unsafe_allow_html=True)

        with col2:
           if nis_salary:
                with st.spinner("Updating rates..."): # Loading animation
                    usd_salary, eur_salary, gbp_salary = convert_salary_israel_to_world(nis_salary, rates)
            
                st.subheader("Converted Salaries")
                
                col_usd, col_eur, col_gbp = st.columns(3)
                
                with col_usd:
                  st.metric(label="🇺🇸 USD", value=f"${usd_salary:,.0f}")
                with col_eur:
                  st.metric(label="🇪🇺 EUR", value=f"€{eur_salary:,.0f}")
                with col_gbp:
                   st.metric(label="🇬🇧 GBP", value=f"£{gbp_salary:,.0f}")

    # --- World to Israel Tab ---
    with tab2:
        st.header("Convert Salary from World to Israel", divider="blue")
        st.markdown("Enter your annual salary in your chosen currency and it will be converted.")
        
        col1, col2 = st.columns([2,3]) # Adjusted column ratio for better layout
        
        with col1:
            selected_currency = st.selectbox("Select Currency", ["USD", "EUR", "GBP"])

            world_salary = st.slider(
                f"Enter your Annual Salary in {selected_currency}:",
                min_value=0,
                max_value=200000,
                step=1000,
                value=50000,
                
            )

            if world_salary:
              world_salary_k = f"{world_salary/1000:.0f}k" if world_salary >= 1000 else f"{world_salary}"
              st.markdown(f"<p style='font-size: 2em; font-weight: bold;'>{selected_currency} = <span style='color: #117A65;'>{world_salary_k}</span></p>", unsafe_allow_html=True)

        with col2:
            if world_salary:
               with st.spinner("Updating rates..."): # Loading animation
                   ils_salary = convert_salary_world_to_israel(world_salary, selected_currency, rates)
                
               st.subheader("Converted Salary")
               if ils_salary:
                    st.metric(label="🇮🇱 NIS (Approximate Monthly)", value=f"{ils_salary:,.0f} ₪")
               else:
                    st.error("Invalid salary input")

else:
    st.error("Failed to fetch exchange rates. Please try again later.")