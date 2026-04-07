import os
import sqlite3
import random
import datetime
import pandas as pd
import numpy as np
from google import genai   # NEW import
from google.genai import types   # NEW for config if needed
from flask import Flask, render_template_string, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import threading

app = Flask(__name__)

# === SET YOUR GEMINI API KEY HERE ===
GEMINI_API_KEY = "AIzaSyBBd5AcefTw1cpSgKfx32tfQHtrKAKqmUE"  # Paste the key from https://aistudio.google.com/app/apikey

# Create the new GenAI client
client = genai.Client(api_key=GEMINI_API_KEY)

class Config:
    INITIAL_AD_BUDGET = 0

config = Config()

DB_FILE = "evoearn.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        strategy TEXT,
        niche TEXT,
        content_type TEXT,
        ad_spend REAL,
        revenue REAL,
        conversions INTEGER,
        improvement_score REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS strategies (
        id INTEGER PRIMARY KEY,
        niche TEXT UNIQUE,
        content_type TEXT,
        base_revenue REAL DEFAULT 50.0
    )''')
    strategies = [
        ("personal_finance", "blog", 80),
        ("health_wellness", "printable", 60),
        ("productivity", "template", 70),
        ("home_tech", "guide", 90)
    ]
    c.executemany("INSERT OR IGNORE INTO strategies (niche, content_type, base_revenue) VALUES (?,?,?)", strategies)
    conn.commit()
    conn.close()

# ... (keep the get_strategies, train_ml_model, select_best_strategy, and HTML_TEMPLATE exactly as in your current app.py)

# NEW: Generate full content with Gemini
def generate_full_content(niche, content_type):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free tier friendly
    prompt = f"""Create a helpful, SEO-friendly 800-word blog post titled: "Top 10 {niche.replace('_', ' ').title()} Tips & Free Resources for 2026"
Content type: {content_type}
Make it engaging, list-based, and include 3-5 natural places for affiliate links (Amazon or ClickBank products).
Also provide:
1. A short Pinterest pin description (max 200 chars)
2. A detailed image prompt for Canva or free AI image tool (e.g. "bright colorful Pinterest pin with text overlay: [title]")
Output in clear sections: TITLE, FULL_ARTICLE, PIN_DESCRIPTION, IMAGE_PROMPT"""

    response = model.generate_content(prompt)
    return response.text

def run_automation_cycle():
    print(f"[{datetime.datetime.now()}] EvoEarn AI cycle starting...")
    strategy = select_best_strategy(0)
    niche = strategy['niche']
    content_type = strategy['content_type']
    
    print(f"   → Generating full content for: {niche} ({content_type})")
    
    full_content = generate_full_content(niche, content_type)
    
    # Save to a file so you can easily copy
    filename = f"content_{niche}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    print(f"   → Full article + pin info saved to: {filename}")
    print(f"   → Next step: Open the file, copy article to Medium, use image prompt in Canva, post pin to Pinterest")

    # Simulate revenue (will improve with real data later)
    base = strategy['base_revenue'] * 0.6
    improvement = 1.0
    if ml_model is not None:
        improvement = 1 + (random.random() * 0.5)
    revenue = round(base * improvement * random.uniform(0.5, 2.0), 2)

    # Log
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO performance 
                 (timestamp, strategy, niche, content_type, ad_spend, revenue, conversions, improvement_score)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (datetime.datetime.now().isoformat(), f"{niche}-{content_type}", niche, content_type,
               0.0, revenue, random.randint(1, 15), improvement))
    conn.commit()
    conn.close()

    # Keep the weekly projection and retrain logic from before...

# Keep the rest of the file (dashboard routes, scheduler start, etc.) exactly the same as your current working version
