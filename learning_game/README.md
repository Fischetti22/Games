# Learning Game

A fun educational web game for elementary school children, featuring Math, Reading, and Science sections.

## Setup

1. **Clone the repository**
2. **Install dependencies**
   - Recommended: Use Docker (see below)
   - Or, create a virtual environment and run:
     ```sh
     pip install -r requirements.txt
     ```
3. **Create a `.env` file in the project root:**
   ```ini
   WORDS_API_KEY=your_wordsapi_key
   NASA_API_KEY=your_nasa_api_key
   GIPHY_API_KEY=your_giphy_api_key
   APP_ID=your_oxford_app_id
   APP_KEYS=your_oxford_app_key
   ```
   (You can leave these blank for static-only mode.)

## Running Locally

```sh
python app.py
```
Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Running with Docker

```sh
docker build -t learning_game .
docker run --env-file .env -p 5000:5000 learning_game
```

Then visit [http://localhost:5000](http://localhost:5000) or use your Raspberry Pi's IP address.

## Features
- Math, Reading, and Science games
- Child-friendly UI
- API fallback to static content if keys are missing

---

Enjoy learning! 