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
        
        It uses the latest available exchange rates. All salaries are assumed to be *annual* salaries.
        
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
        col1, col2 = st.columns(2)
        with col1:
            nis_salary = st.slider(
                "Select Monthly Salary in NIS:",
                 min_value=0,
                  max_value=50000,
                  step=500,
                  value=15000,
            )

            if nis_salary:
                usd_salary, eur_salary, gbp_salary = convert_salary_israel_to_world(nis_salary, rates)

                with col2:
                    st.subheader("Converted Salaries")
                    st.markdown(f"<p style='font-size: 1.3em;'><b>🇺🇸 USD:</b>  ${usd_salary:,.0f} </p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 1.3em;'><b>🇪🇺 EUR:</b>  €{eur_salary:,.0f} </p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 1.3em;'><b>🇬🇧 GBP:</b>  £{gbp_salary:,.0f} </p>", unsafe_allow_html=True)

    # --- World to Israel Tab ---
    with tab2:
        st.header("Convert Salary from World to Israel", divider="blue")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_currency = st.radio("Select Currency", ["USD", "EUR", "GBP"])
            world_salary = st.slider(
                f"Select Annual Salary in {selected_currency}:",
                min_value=0,
                max_value=200000,
                step=1000,
                value=50000,
            )
            
            if world_salary:
                ils_salary = convert_salary_world_to_israel(world_salary, selected_currency, rates)
                
                with col2:
                    st.subheader("Converted Salary")
                    if ils_salary:
                        st.markdown(f"<p style='font-size: 1.3em;'><b>🇮🇱:</b> {ils_salary:,.0f} ₪</p>", unsafe_allow_html=True)
                    else:
                        st.error("Invalid salary input")

else:
    st.error("Failed to fetch exchange rates. Please try again later.")