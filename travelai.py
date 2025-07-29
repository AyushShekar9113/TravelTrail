import streamlit as st
import pandas as pd
from datetime import datetime

sample_flights = [
    {
        "airline": "Delta",
        "from": "NYC",
        "to": "SFO",
        "departure": "2025-08-01T08:00:00",
        "arrival": "2025-08-01T13:00:00",
        "price": 300,
        "loyalty_score": 8
    },
    {
        "airline": "United",
        "from": "NYC",
        "to": "SFO",
        "departure": "2025-08-01T09:00:00",
        "arrival": "2025-08-01T14:00:00",
        "price": 280,
        "loyalty_score": 6
    },
    {
        "airline": "American Airlines",
        "from": "NYC",
        "to": "SFO",
        "departure": "2025-08-01T07:30:00",
        "arrival": "2025-08-01T12:00:00",
        "price": 320,
        "loyalty_score": 9
    }
]

sample_hotels = [
    {
        "hotel_name": "Marriott SF",
        "city": "SFO",
        "checkin": "2025-08-01",
        "checkout": "2025-08-03",
        "price": 450,
        "loyalty_score": 9
    },
    {
        "hotel_name": "Hilton SF",
        "city": "SFO",
        "checkin": "2025-08-01",
        "checkout": "2025-08-03",
        "price": 390,
        "loyalty_score": 8
    },
    {
        "hotel_name": "Budget Inn",
        "city": "SFO",
        "checkin": "2025-08-01",
        "checkout": "2025-08-03",
        "price": 300,
        "loyalty_score": 6
    }
]

def rank_options(options, type_, weights):
    ranked = []

    for item in options:
        if type_ == "flight":
            duration = (
                pd.to_datetime(item['arrival']) - pd.to_datetime(item['departure'])
            ).seconds / 3600
            score = (
                weights['price'] * -item['price'] +
                weights['duration'] * -duration +
                weights['loyalty'] * item['loyalty_score']
            )
            item['duration_hr'] = round(duration, 2)
        else:  
            score = (
                weights['price'] * -item['price'] +
                weights['loyalty'] * item['loyalty_score']
            )
        item['score'] = round(score, 2)
        ranked.append(item)

    return sorted(ranked, key=lambda x: x['score'], reverse=True)


def get_recommendations(from_city, to_city, start_date, end_date):
    filtered_flights = [f for f in sample_flights if f['from'] == from_city and f['to'] == to_city]
    filtered_hotels = [h for h in sample_hotels if h['city'] == to_city]

    ranked_flights = rank_options(filtered_flights, "flight", {
        "price": 0.5, "duration": 0.3, "loyalty": 0.2
    })

    ranked_hotels = rank_options(filtered_hotels, "hotel", {
        "price": 0.6, "loyalty": 0.4
    })

    return ranked_flights[:5], ranked_hotels[:5]


st.set_page_config(page_title="TravelTrail – Business Travel Optimizer", layout="wide")
st.title("✈️ TravelTrail – Business-Travel Optimizer")

with st.form("travel_form"):
    col1, col2 = st.columns(2)
    with col1:
        from_city = st.text_input("From (City Code)", value="NYC")
        to_city = st.text_input("To (City Code)", value="SFO")
    with col2:
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    submitted = st.form_submit_button("Search Flights & Hotels")

if submitted:
    if from_city and to_city and start_date and end_date:
        with st.spinner("Fetching top travel options..."):
            top_flights, top_hotels = get_recommendations(from_city, to_city, start_date.isoformat(), end_date.isoformat())

        st.success("Here are your top travel options!")

        st.subheader("Top 5 Flights ✈️")
        flight_df = pd.DataFrame(top_flights)
        flight_df_display = flight_df[["airline", "price", "duration_hr", "loyalty_score", "score"]]
        st.dataframe(flight_df_display.style.highlight_max(axis=0), use_container_width=True)

        st.subheader("Top 5 Hotels 🏨")
        hotel_df = pd.DataFrame(top_hotels)
        hotel_df_display = hotel_df[["hotel_name", "price", "loyalty_score", "score"]]
        st.dataframe(hotel_df_display.style.highlight_max(axis=0), use_container_width=True)
    else:
        st.error("Please fill all fields.")
