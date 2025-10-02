# Design is created using chatgpt

import streamlit as st
import pandas as pd
import pickle as pkl
import requests


# ----------------- PAGE CONFIG ----------------- #
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ----------------- CUSTOM CSS ----------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

.stApp { background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%); font-family: 'Inter', sans-serif; color: #ffffff; }
.stApp > header { background-color: transparent; }
.main .block-container { padding-top: 2rem; max-width: 1200px; }

/* ---------- SELECTION BOX ---------- */
.stSelectbox > div:first-child { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(245, 197, 24, 0.3); border-radius: 15px; padding: 0.5rem 1rem; transition: all 0.3s ease; }
.stSelectbox > div:first-child:hover { background: rgba(255, 255, 255, 0.1); border-color: #f5c518; box-shadow: 0 5px 20px rgba(245,197,24,0.4); }

/* ---------- BUTTON ---------- */
.stButton>button { background: linear-gradient(135deg, #f5c518, #ff6b6b); color: #0c0c0c; font-weight: 600; font-size: 1rem; border-radius: 15px; padding: 0.6rem 2rem; transition: all 0.3s ease; margin: 1rem auto; display: block; box-shadow: 0 5px 15px rgba(245,197,24,0.3); }
.stButton>button:hover { transform: scale(1.05); box-shadow: 0 10px 25px rgba(245,197,24,0.5); }

/* ---------- LOADING SPINNER TEXT ---------- */
.stSpinner>div>div { color: #f5c518 !important; font-weight: 600; font-size: 1.1rem; text-align: center; }

/* ---------- SECTION HEADERS ---------- */
.section-header, .recommendations-header { text-align: center; font-size: 2rem; font-family: 'Orbitron', monospace; font-weight: 700; margin: 3rem 0 2rem 0; background: linear-gradient(135deg, #ffffff, #f5c518); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ---------- MOVIE CARDS ---------- */
.movie-card { background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)); backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 15px 35px rgba(0,0,0,0.5); transition: all 0.5s ease; overflow: hidden; margin-bottom: 1rem; }
.movie-card:hover { transform: perspective(1000px) rotateX(-8deg) rotateY(8deg) translateZ(40px) scale(1.05); box-shadow: 0 25px 50px rgba(0,0,0,0.6), 0 15px 35px rgba(245,197,24,0.3); border-color: rgba(245,197,24,0.5); }
.movie-poster { border-radius: 20px; width: 100%; max-width: 220px; height: auto; transition: transform 0.3s ease; }
.movie-card:hover .movie-poster { transform: scale(1.05); }
.movie-title { margin-top: 1rem; font-size: 1.2rem; font-weight: 600; color: #ffffff; transition: color 0.3s ease, transform 0.3s ease; }
.movie-card:hover .movie-title { color: #f5c518; transform: scale(1.1); }

/* ---------- FOOTER ---------- */
footer { text-align: center; padding: 2rem 0; font-size: 0.9rem; color: #aaa; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 4rem; }
</style>
""", unsafe_allow_html=True)

# ----------------- LOAD DATA ----------------- #
movies_dict = pkl.load(open("model/movie_list.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pkl.load(open("model/similarity.pkl", "rb"))

# ----------------- FUNCTIONS ----------------- #
def fetch_poster(movie_title):
    api_key = "da2d6348"  # OMDB API Key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True" and data.get("Poster") != "N/A":
            return data["Poster"]
        else:
            return f"https://via.placeholder.com/300x450/1a1a2e/f5c518?text={movie_title.replace(' ', '+')}"
    except:
        return f"https://via.placeholder.com/300x450/1a1a2e/f5c518?text={movie_title.replace(' ', '+')}"

def recommend(movie):
    movie_index = movies[movies['title'].str.lower() == movie.lower()].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommend_movies.append(title)
        recommend_posters.append(fetch_poster(title))

    return recommend_movies, recommend_posters

# ----------------- STREAMLIT UI ----------------- #
st.markdown('<div class="section-header">🎭 Choose Your Movie</div>', unsafe_allow_html=True)

# Movie selection
option = st.selectbox(
    "Select a movie", 
    movies['title'].values, 
    key="movie_select", 
    label_visibility="collapsed"  
)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

# Button click
if st.button("🚀 Get Recommendations"):
    with st.spinner("Analyzing cinematic patterns..."):
        
        try:
            names, posters = recommend(option)
            st.session_state.recommendations = (names, posters)
        except:
            st.session_state.recommendations = None
            st.error("❌ Movie not found. Try another title.")

# Show recommendations
if st.session_state.recommendations:
    names, posters = st.session_state.recommendations
    st.markdown('<div class="recommendations-header">🍿 Recommended For You</div>', unsafe_allow_html=True)
    cols = st.columns(5, gap="large")
    for i in range(5):
        with cols[i]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" class="movie-poster" alt="{names[i]}" loading="lazy">
                    <div class="movie-title">{names[i]}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown('<footer>© 2025 Cinemascope. All rights reserved.</footer>', unsafe_allow_html=True)
