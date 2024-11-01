import requests
import pandas as pd
import streamlit as st
import random
from datetime import datetime
import base64
from io import BytesIO
import json
import os


APOD_URL = "https://api.nasa.gov/planetary/apod"
API_KEY = st.secrets["NASA_API_KEY"] 


SPACE_FACTS = [
    "One day on Venus is longer than one year on Venus.",
    "The footprints on the Moon will last for 100 million years.",
    "The Sun makes up 99.86% of our solar system's mass.",
    "A year on Mercury is just 88 Earth days long.",
    "Jupiter's Great Red Spot is shrinking.",
    "Saturn's rings are mostly made of ice and rock.",
    "You can fit all the planets in the solar system between Earth and the Moon.",
    "There are more stars in the universe than grains of sand on Earth.",
]

# Initialize session state for favorites
if 'favorites' not in st.session_state:
    if os.path.exists('favorites.json'):
        with open('favorites.json', 'r') as f:
            st.session_state.favorites = json.load(f)
    else:
        st.session_state.favorites = {}

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main background with starry effect */
        .main {
            background: linear-gradient(to bottom, #0a192f, #000000);
            color: #e6f1ff;
            background-image: 
                radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 5px),
                radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 3px),
                radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 4px);
            background-size: 550px 550px, 350px 350px, 250px 250px;
            background-position: 0 0, 40px 60px, 130px 270px;
        }

        /* Glowing headers */
        .stTitle, .stHeader {
            color: #64ffda !important;
            text-shadow: 0 0 10px rgba(100,255,218,0.5),
                         0 0 20px rgba(100,255,218,0.3),
                         0 0 30px rgba(100,255,218,0.2);
            font-family: 'Space Grotesk', sans-serif;
        }

        /* Neon buttons */
        .stButton>button {
            background-color: transparent;
            color: #64ffda;
            border: 2px solid #64ffda;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(100,255,218,0.2);
        }

        .stButton>button:hover {
            background-color: rgba(100,255,218,0.1);
            box-shadow: 0 0 20px rgba(100,255,218,0.4);
            transform: translateY(-2px);
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(to bottom, #020c1b, #0a192f);
            border-right: 1px solid rgba(100,255,218,0.1);
        }

        /* Alert boxes */
        .stAlert {
            background-color: rgba(10,25,47,0.7);
            border: 1px solid #64ffda;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(100,255,218,0.1);
        }

        /* Image container */
        .image-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(100,255,218,0.2),
                       0 0 40px rgba(100,255,218,0.1);
            border: 1px solid rgba(100,255,218,0.3);
            padding: 4px;
            background: rgba(10,25,47,0.5);
        }

        /* Download button */
        .download-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: transparent;
            color: #64ffda;
            text-decoration: none;
            border: 2px solid #64ffda;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(100,255,218,0.2);
        }

        .download-button:hover {
            background-color: rgba(100,255,218,0.1);
            box-shadow: 0 0 20px rgba(100,255,218,0.4);
            transform: translateY(-2px);
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0a192f;
        }

        ::-webkit-scrollbar-thumb {
            background: #64ffda;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #4ac8ac;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            color: #64ffda !important;
            background-color: rgba(10,25,47,0.7);
            border: 1px solid rgba(100,255,218,0.2);
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def fetch_apod_data():
    try:
        response = requests.get(f"{APOD_URL}?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def fetch_apod_data_date(date):
    try:
        response = requests.get(f"{APOD_URL}?api_key={API_KEY}&date={date}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_image_download_link(img_url, filename):
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        img = BytesIO(response.content)
        b64 = base64.b64encode(img.getvalue()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="{filename}" class="download-button">📥 Download Image</a>'
        return href
    except Exception as e:
        st.error(f"Error creating download link: {str(e)}")
        return None

def save_favorites():
    try:
        with open('favorites.json', 'w') as f:
            json.dump(st.session_state.favorites, f)
    except Exception as e:
        st.error(f"Error saving favorites: {str(e)}")

def add_to_favorites(data):
    st.session_state.favorites[data['date']] = {
        'title': data['title'],
        'url': data['url'],
        'explanation': data['explanation']
    }
    save_favorites()
    st.success("Added to favorites!")

def remove_from_favorites(date):
    if date in st.session_state.favorites:
        del st.session_state.favorites[date]
        save_favorites()
        st.success("Removed from favorites!")

def display_apod(data):
    if not data:
        st.error("No data to display")
        return

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(data["url"], use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            download_link = get_image_download_link(data["url"], f"APOD_{data['date']}.jpg")
            if download_link:
                st.markdown(download_link, unsafe_allow_html=True)
        
        with btn_col2:
            if data['date'] in st.session_state.favorites:
                if st.button('❌ Remove from Favorites'):
                    remove_from_favorites(data['date'])
            else:
                if st.button('⭐ Add to Favorites'):
                    add_to_favorites(data)
    
    with col2:
        st.markdown(f"## 🎯 {data['title']}")
        st.markdown(f"**🗓 Date:** {data['date']}")
        if 'copyright' in data:
            st.markdown(f"**©️ Credit:** {data['copyright']}")
        
        with st.expander("🔍 Learn More About This Image"):
            st.write(data['explanation'])

def display_favorites():
    st.sidebar.markdown("### ⭐ Your Favorite APODs")
    if not st.session_state.favorites:
        st.sidebar.info("No favorites yet! Add some by clicking the star button.")
    else:
        for date, data in st.session_state.favorites.items():
            with st.sidebar.expander(f"{data['title']} ({date})"):
                st.image(data['url'], use_column_width=True)
                if st.button('Remove', key=f"remove_{date}"):
                    remove_from_favorites(date)

def main():
    st.set_page_config(
        page_title="🌌 SpaceSnap: Your Window to the Cosmos",
        page_icon="🔭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_css()
    
    st.markdown("# 🌌 SpaceSnap: Your Window to the Cosmos")
    st.markdown("### Explore the wonders of space, one picture at a time 🚀")
    
    st.sidebar.markdown("## 🎮 Control Panel")
    
    st.sidebar.markdown("### 🌟 Did You Know?")
    st.sidebar.info(random.choice(SPACE_FACTS))
    
    st.sidebar.markdown("### 🗓 Time Travel")
    selected_date = st.sidebar.date_input(
        "Select a date to explore",
        pd.Timestamp.today(),
        min_value=datetime(1995, 6, 16),
        max_value=pd.Timestamp.today()
    )
    
    st.sidebar.markdown("### 🎲 Feeling Lucky?")
    if st.sidebar.button("🚀 Show Random APOD"):
        with st.spinner("Traveling through time and space... 🌠"):
            start_date = pd.to_datetime("1995-06-16")
            end_date = pd.Timestamp.today()
            random_date = pd.to_datetime(random.randint(start_date.value, end_date.value))
            random_date_str = random_date.strftime("%Y-%m-%d")
            apod_data = fetch_apod_data_date(random_date_str)
            if apod_data:
                display_apod(apod_data)
    
    display_favorites()
    
    try:
        if selected_date.strftime("%Y-%m-%d") != pd.Timestamp.today().strftime("%Y-%m-%d"):
            with st.spinner("Loading your cosmic view... 🛸"):
                apod_data = fetch_apod_data_date(selected_date.strftime("%Y-%m-%d"))
        else:
            with st.spinner("Fetching today's cosmic wonder... ✨"):
                apod_data = fetch_apod_data()
        
        if apod_data:
            display_apod(apod_data)
        
    except Exception as e:
        st.error("🌋 Houston, we have a problem! Failed to fetch the image. Please try again later.")
        st.error(f"Error details: {str(e)}")
    
    st.markdown("---")
    st.markdown("Made with ❤️ for space enthusiasts | Data provided by NASA's APOD API")

if __name__ == "__main__":
    main()
