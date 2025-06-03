from flask import Flask, render_template, request, redirect
import os
import time
import threading
import requests

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MSG_PATH = os.path.join(DATA_DIR, "messages.txt")
TOKEN_PATH = os.path.join(DATA_DIR, "tokens.txt")
CONVO_PATH = os.path.join(DATA_DIR, "convo.txt")
DELAY_PATH = os.path.join(DATA_DIR, "delay.txt")

# Utils
def read_file(path):
    if os.path.exists(path):
        return open(path, "r", encoding="utf-8").read()
    return ""

def write_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def append_file(path, data):
    with open(path, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def run_poster():
    msg_index = 0
    token_index = 0

    while True:
        try:
            messages = [m.strip() for m in read_file(MSG_PATH).splitlines() if m.strip()]
            tokens = [t.strip() for t in read_file(TOKEN_PATH).splitlines() if t.strip()]
            convo_id = read_file(CONVO_PATH).strip()
            delay = float(read_file(DELAY_PATH).strip())
        except Exception as e:
            print(f"[ERR] Reading data: {e}")
            time.sleep(5)
            continue

        if not messages or not tokens or not convo_id:
            print("[!] Missing messages, tokens or convo_id.")
            time.sleep(5)
            continue

        msg = messages[msg_index % len(messages)]
        token = tokens[token_index % len(tokens)]

        url = f"https://graph.facebook.com/v17.0/t_{convo_id}/"
        data = {"access_token": token, "message": msg}

        try:
            res = requests.post(url, json=data)
            if res.ok:
                print(f"[SENT] {msg}")
            else:
                print(f"[FAIL] {res.status_code}: {msg} | ERROR: {res.text}")
        except Exception as e:
            print(f"[POST ERR]: {e}")

        msg_index += 1
        token_index += 1
        time.sleep(delay)

# Flask App
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        if "message" in request.form:
            append_file(MSG_PATH, request.form["message"])
        if "token" in request.form:
            append_file(TOKEN_PATH, request.form["token"])
        if "convo" in request.form:
            write_file(CONVO_PATH, request.form["convo"])
        if "delay" in request.form:
            write_file(DELAY_PATH, request.form["delay"])
        return redirect("/")

    messages = read_file(MSG_PATH)
    tokens = read_file(TOKEN_PATH)
    convo = read_file(CONVO_PATH)
    delay = read_file(DELAY_PATH)
    return render_template("index.html", messages=messages, tokens=tokens, convo=convo, delay=delay)

if __name__ == "__main__":
    threading.Thread(target=run_poster, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)