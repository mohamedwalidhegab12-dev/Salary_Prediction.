import streamlit as st
import pandas as pd
import joblib
import time
import numpy as np

# =========================================
# 1. إعدادات الصفحة والـ CSS المطور (Dark Mode + Mobile Friendly)
# =========================================
st.set_page_config(page_title="Salary Oracle | Royal Edition", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;900&family=Playfair+Display:ital,wght@0,400;1,900&family=Montserrat:wght@100;300;600&display=swap');
    
    /* إجبار الثيم المظلم */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #050505 !important;
        color: #ffffff !important;
    }

    * { font-family: 'Montserrat', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at center, #1a1a1a 0%, #050505 100%);
    }

    /* العنوان الرئيسي */
    .royal-title {
        font-family: 'Cinzel', serif;
        background: linear-gradient(135deg, #856739 0%, #fff9ad 25%, #856739 50%, #fff9ad 75%, #856739 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        letter-spacing: 10px;
        margin-top: -40px;
        filter: drop-shadow(0 10px 20px rgba(0,0,0,1));
    }

    /* كروت التصميم */
    .royal-card {
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 40px 0 40px 0;
        padding: 40px;
        border-left: 3px solid #bf953f;
        border-right: 1px solid rgba(191, 149, 63, 0.1);
        box-shadow: 20px 20px 60px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }

    /* ضبط الموبايل */
    @media (max-width: 640px) {
        .royal-title {
            font-size: 2.2rem !important;
            letter-spacing: 3px !important;
        }
        .salary-res {
            font-size: 3rem !important; 
        }
        .result-card {
            padding: 30px !important;
        }
        .royal-card {
            padding: 20px !important;
        }
    }

    .section-header {
        font-family: 'Playfair Display', serif;
        color: #bf953f;
        font-size: 1.6rem;
        font-style: italic;
        margin-bottom: 20px;
    }

    /* زرار التوقع */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #bf953f 0%, #fcf6ba 100%);
        color: #000 !important;
        padding: 20px;
        font-size: 1.6rem;
        font-family: 'Cinzel', serif;
        font-weight: 900;
        border-radius: 0 40px 0 40px;
        border: none;
        transition: 0.4s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 50px rgba(191, 149, 63, 0.4);
    }

    /* تسميات الأسئلة */
    div[data-testid="stWidgetLabel"] p {
        color: #bf953f !important;
        font-size: 1.1rem !important;
        font-weight: 600;
        text-transform: capitalize;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================
# 2. Logic & Assets Loading
# =========================================
def group_job_titles(title):
    title = title.lower()
    if any(x in title for x in ['scientist', 'nlp', 'research', 'learning']): return 'Data Science'
    if any(x in title for x in ['engineer', 'infrastructure', 'developer']): return 'Engineering'
    if any(x in title for x in ['analyst', 'analytics']): return 'Analyst'
    if any(x in title for x in ['manager', 'head', 'director']): return 'Management'
    return 'Other'

@st.cache_resource
def load_assets():
    try:
        return {
            'model': joblib.load("xgb_model.pkl"),
            'ord': joblib.load("ordinal_encoder.pkl"),
            'ohe': joblib.load("ohe_encoder.pkl"),
            'scaler': joblib.load("scaler.pkl")
        }
    except: return None

assets = load_assets()

# =========================================
# 3. GUI Layout
# =========================================
st.markdown('<h1 class="royal-title">THE ORACLE</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#636b7f; letter-spacing:5px; margin-bottom:50px;">SMART SALARY PREDICTOR</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="royal-card"><div class="section-header">Personal Info</div>', unsafe_allow_html=True)
    job_title = st.selectbox("Job Title", ['AI Engineer', 'Data Analyst', 'Frontend Developer', 'Business Analyst', 'Product Manager', 'Backend Developer', 'Machine Learning Engineer', 'DevOps Engineer', 'Software Engineer', 'Cybersecurity Analyst', 'Data Scientist', 'Cloud Engineer'])
    exp = st.slider("Years of Experience", 0, 30, 5)
    edu = st.selectbox("Education Level", ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'], index=2)
    skills = st.number_input("Number of Skills", 1, 50, 10)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="royal-card"><div class="section-header">Job Details</div>', unsafe_allow_html=True)
    location = st.selectbox("Location", ['USA', 'UK', 'Germany', 'Canada', 'Australia', 'India', 'Singapore', 'Sweden', 'Netherlands', 'Remote'])
    industry = st.selectbox("Industry", ['Technology', 'Finance', 'Healthcare', 'Retail', 'Education', 'Manufacturing', 'Telecom', 'Consulting'])
    comp_size = st.selectbox("Company Size", ['Small', 'Medium', 'Large', 'Enterprise'], index=1)
    remote = st.radio("Work from Home?", ['No', 'Hybrid', 'Yes'], horizontal=True)
    certs = st.number_input("Certificates", 0, 15, 1)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================
# 4. Processing & Output
# =========================================
if st.button("⚜️ CALCULATE SALARY ⚜️"):
    if assets:
        with st.spinner("Analyzing data..."):
            job_cat = group_job_titles(job_title)
            is_lead = 1 if any(word in job_title for word in ['Lead', 'Manager', 'Director']) else 0
            
            input_df = pd.DataFrame({
                'Job_Category': [job_cat], 'industry': [industry], 'location': [location],
                'job_title': [job_title], 'education_level': [edu], 'company_size': [comp_size],
                'remote_work': [remote], 'experience_years': [exp], 'skills_count': [skills],
                'certifications': [certs], 'Is_Lead_Role': [is_lead], 'salary': [0]
            })

            # Preprocessing (نفس المنطق البرمجي)
            input_df[['education_level', 'company_size', 'remote_work']] = assets['ord'].transform(input_df[['education_level', 'company_size', 'remote_work']])
            encoded_df = assets['ohe'].transform(input_df)
            if 'salary' in encoded_df.columns: encoded_df.drop(columns=['salary'], inplace=True)
            
            num_cols = ['experience_years', 'skills_count', 'certifications', 'education_level', 'company_size', 'remote_work']
            encoded_df[num_cols] = assets['scaler'].transform(encoded_df[num_cols])

            try: model_cols = assets['model'].best_estimator_.feature_names_in_
            except: model_cols = assets['model'].feature_names_in_
            encoded_df = encoded_df[model_cols]

            res = assets['model'].predict(encoded_df)[0]
            time.sleep(1)

            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, #121212 0%, #2a2a2a 100%); border-radius: 60px 0 60px 0; padding: 50px; text-align: center; border: 3px solid #bf953f; box-shadow: 0 0 80px rgba(0,0,0,0.8);">
                    <p style="color: #bf953f; letter-spacing: 5px; margin-bottom: 5px;">ESTIMATED ANNUAL SALARY</p>
                    <h1 class="salary-res" style="font-family: 'Cinzel', serif; background: linear-gradient(to right, #856739, #fcf6ba, #856739); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 6rem; font-weight: 900; margin: 0;">${res:,.0f}</h1>
                    <div style="width: 100px; height: 1px; background: #bf953f; margin: 20px auto; opacity: 0.5;"></div>
                    <p style="color: #636b7f;">AI PREDICTION VERIFIED</p>
                </div>
            """, unsafe_allow_html=True)
            st.snow()
    else: st.error("Model files missing!")

st.markdown('<p style="text-align:center; color:#444; margin-top:40px;">SALARY ORACLE CORE © 2026</p>', unsafe_allow_html=True)
