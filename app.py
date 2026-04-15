from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import google.generativeai as genai

app = Flask(__name__)

# ---------- Gemini AI Setup ----------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ai_response(question):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text.strip()
    except Exception as e:
        return "AI error: " + str(e)

# ---------- Rule-based Short Responses ----------
def local_commands(question):
    q = question.lower()
    if q in ["hello", "hi", "hlo"]:
        return "Hello! How can I assist you, Sir?"
    elif q in ["how are you"]:
        return "I am fully operational, ready to assist!"
    elif q in ["time", "current time"]:
        return datetime.now().strftime("Current time is %H:%M:%S")
    elif q in ["date", "today's date"]:
        return datetime.now().strftime("Today's date is %d-%m-%Y")
    return None

# ---------- Live Google ----------
def online_google(question):
    try:
        url = f"https://www.google.com/search?q={question}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        answer_box = soup.find("div", class_="BNeawe")
        if answer_box:
            answer = answer_box.text.strip().split('.')[0] + "."
            return answer if len(answer) <= 200 else answer[:200] + "..."
        return "Live answer not found."
    except:
        return "Error fetching live answer."

def is_live_question(q):
    live_words = ["today","current","live","now","weather","price","score","rate","aaj","abhi"]
    return any(word in q.lower() for word in live_words)

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    q = data.get("question", "")

    # Step 1: local commands
    answer = local_commands(q)

    # Step 2: live or AI
    if not answer:
        if is_live_question(q):
            answer = online_google(q)
        else:
            answer = ai_response(q)

    return jsonify({"answer": answer})

# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
