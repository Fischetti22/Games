from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import random
import requests
from dotenv import load_dotenv
from datamuse import Datamuse
import giphy_client
from giphy_client.rest import ApiException

# ─── Load environment variables ────────────────────────────────────────────────
load_dotenv()  # expects .env in project root

WORDS_API_KEY   = os.getenv("WORDS_API_KEY", "")
WORDS_API_HOST  = "wordsapiv1.p.rapidapi.com"

NASA_API_KEY    = os.getenv("NASA_API_KEY", "")

GIPHY_API_KEY   = os.getenv("GIPHY_API_KEY", "")

OXFORD_APP_ID   = os.getenv("APP_ID", "")
OXFORD_APP_KEY  = os.getenv("APP_KEYS", "")

# ─── Flask setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─── Initialize external clients ───────────────────────────────────────────────
dm = Datamuse()                      # Datamuse for antonyms
giphy_api = giphy_client.DefaultApi()  # Giphy Python SDK

# ─── 1) MATH PROBLEMS (in-process) ────────────────────────────────────────────
def generate_math_problem(grade: int):
    if grade == 1:
        a, b = random.randint(1, 10), random.randint(1, 10)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        answer = a + b if op == "+" else a - b
    else:
        op = random.choice(["+", "-", "*"])
        if op == "*":
            a, b = random.randint(1, 10), random.randint(1, 10)
        else:
            a, b = random.randint(1, 20), random.randint(1, 20)
            if op == "-" and a < b:
                a, b = b, a
        answer = a + b if op == "+" else a - b if op == "-" else a * b
    return {"problem": f"{a} {op} {b}", "answer": answer}

@app.route("/api/math_problem")
def api_math_problem():
    grade = int(request.args.get("grade", 1))
    return jsonify(generate_math_problem(grade))


# ─── 2) READING (WordsAPI → Datamuse → Oxford → static) ───────────────────────
STATIC_WORDS = [
    {"word":"cat",  "definition":"a small furry animal that says meow"},
    {"word":"dog",  "definition":"a friendly pet that barks and wags its tail"},
    {"word":"sun",  "definition":"the star at the center of our solar system"},
    {"word":"tree", "definition":"a tall plant with a trunk and branches"}
]

@app.route("/api/word_problem")
def api_word_problem():
    # 2a) Try to get a random word + definition from WordsAPI
    correct = None
    definition = None
    if WORDS_API_KEY:
        try:
            r = requests.get(
                f"https://{WORDS_API_HOST}/words/?random=true",
                headers={
                    "X-RapidAPI-Key": WORDS_API_KEY,
                    "X-RapidAPI-Host": WORDS_API_HOST
                },
                timeout=3
            ).json()
            correct = r.get("word")
            defs = r.get("results", [])
            definition = defs[0].get("definition") if defs else None
        except Exception:
            app.logger.warning("WordsAPI lookup failed, falling back to static.")

    # 2b) Fallback to static list
    if not correct or not definition:
        pick = random.choice(STATIC_WORDS)
        correct, definition = pick["word"], pick["definition"]

    # 2c) Fetch antonyms from Datamuse
    wrongs = []
    try:
        ants = dm.words(rel_ant=correct, max=5)
        wrongs = [w["word"] for w in ants if w.get("word") and w["word"] != correct][:3]
    except Exception:
        app.logger.warning("Datamuse lookup failed.")

    # 2d) Fill with additional random words from WordsAPI if needed
    while len(wrongs) < 3 and WORDS_API_KEY:
        try:
            r2 = requests.get(
                f"https://{WORDS_API_HOST}/words/?random=true",
                headers={
                    "X-RapidAPI-Key": WORDS_API_KEY,
                    "X-RapidAPI-Host": WORDS_API_HOST
                },
                timeout=2
            ).json()
            w2 = r2.get("word")
            if w2 and w2 != correct and w2 not in wrongs:
                wrongs.append(w2)
        except Exception:
            break

    # 2e) Final static fill if still short
    if len(wrongs) < 3:
        for pick in random.sample(STATIC_WORDS, 3 - len(wrongs)):
            if pick["word"] != correct:
                wrongs.append(pick["word"])

    # 2f) Try Oxford for richer definition
    if OXFORD_APP_ID and OXFORD_APP_KEY:
        try:
            od = requests.get(
                f"https://od-api-sandbox.oxforddictionaries.com/api/v2/entries/en-us/{correct.lower()}",
                headers={"app_id": OXFORD_APP_ID, "app_key": OXFORD_APP_KEY},
                timeout=3
            ).json()
            defs = od["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"]
            if defs:
                definition = defs[0]
        except Exception:
            app.logger.warning("Oxford lookup failed.")

    # 2g) Shuffle and respond
    options = wrongs + [correct]
    random.shuffle(options)
    return jsonify({"definition": definition, "options": options, "answer": correct})


# ─── 3) SCIENCE (static → NASA APOD/Image Library → static) ────────────────
SCIENCE_STATIC = [
    {"fact":"The Sun is a star that gives us light and heat",
     "image":"https://media.giphy.com/media/L1UVDdpRxkdJqJ3dK6/giphy.gif",
     "explanation":"The Sun helps plants grow and keeps us warm!"},
    {"fact":"Plants make their own food using sunlight",
     "image":"https://media.giphy.com/media/3o7TKDEhaHWJpBs2Xu/giphy.gif",
     "explanation":"This process is called photosynthesis."},
    {"fact":"Butterflies start as caterpillars",
     "image":"https://media.giphy.com/media/3o7TKDEhaHWJpBs2Xu/giphy.gif",
     "explanation":"This change is called metamorphosis."},
]

def fetch_nasa_fact():
    if not NASA_API_KEY:
        return None
    # APOD
    try:
        apod = requests.get(
            f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}",
            timeout=5
        ).json()
        if "explanation" in apod:
            return {
                "fact": apod.get("title","NASA Fact"),
                "image": apod.get("url",""),
                "explanation": apod["explanation"][:150] + "...",
                "source": "NASA APOD"
            }
    except Exception:
        pass
    # Image Library
    try:
        term = random.choice(["moon","mars","stars","rocket"])
        lib = requests.get(
            f"https://images-api.nasa.gov/search?q={term}&media_type=image",
            timeout=5
        ).json()
        items = lib.get("collection",{}).get("items",[])
        if items:
            it = random.choice(items)
            meta = it["data"][0]
            href = next((l["href"] for l in it.get("links",[]) if "href" in l), None)
            if href:
                return {
                    "fact": meta.get("title","Space Image"),
                    "image": href,
                    "explanation": (meta.get("description","")[:150] + "..."),
                    "source": "NASA Images"
                }
    except Exception:
        pass
    return None

@app.route("/api/science_fact")
def api_science_fact():
    # 1) instant static
    fallback = random.choice(SCIENCE_STATIC)
    # 2) try live NASA
    live = fetch_nasa_fact()
    if live:
        return jsonify(live)
    # 3) final fallback
    return jsonify(fallback)


# ─── 4) CELEBRATION GIF (Giphy SDK → static) ────────────────────────────────
CELEBRATION_STATIC = [
    "https://media.giphy.com/media/L1UVDdpRxkdJqJ3dK6/giphy.gif",
    "https://media.giphy.com/media/3o7TKDEhaHWJpBs2Xu/giphy.gif"
]

@app.route("/api/celebration_gif")
def api_celebration_gif():
    if GIPHY_API_KEY:
        try:
            resp = giphy_api.gifs_search_get(
                api_key=GIPHY_API_KEY,
                q="funny dog",
                limit=25,
                rating="g"
            )
            gifs = resp.data or []
            if gifs:
                choice = random.choice(gifs)
                return jsonify({"url": choice.images.fixed_height.url})
        except ApiException:
            app.logger.warning("Giphy SDK lookup failed.")
    return jsonify({"url": random.choice(CELEBRATION_STATIC)})


# ─── 5) UI ROUTES ─────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/game")
def game():
    return render_template("game.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

