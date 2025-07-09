# Games Collection

A collection of educational games and utility scripts.

## Projects

### 🎮 Learning Game (`learning_game/`)
A web-based educational game built with Flask that includes word games and interactive learning activities.

### 🔢 Algorithm Game (`algo_game/`)
An educational game to learn data structures and algorithms with visual representations.

### 🐍 Snake Game (`snake_game/`)
A classic Snake game implemented in C++.

### 🔧 Utility Scripts (`scripts/`)
Various utility scripts including:
- **Weather HUD**: A desktop weather widget
- **WiFi Monitor**: Network monitoring tools
- **Data Manager**: Data processing utilities

### 🧪 Test (`test/`)
Game development assets and test files.

## Setup

### Environment Variables
Some scripts require API keys. Create a `.env` file in the appropriate directory with:

```bash
# For learning_game/
WORDS_API_KEY=your_words_api_key_here
NASA_API_KEY=your_nasa_api_key_here
GIPHY_API_KEY=your_giphy_api_key_here
APP_ID=your_oxford_app_id
APP_KEYS=your_oxford_app_key

# For weather_hud script
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### API Key Sources
- **Words API**: https://www.wordsapi.com/
- **NASA API**: https://api.nasa.gov/
- **GIPHY API**: https://developers.giphy.com/
- **Oxford Dictionary API**: https://developer.oxforddictionaries.com/
- **OpenWeatherMap API**: https://openweathermap.org/api

## Usage

### Learning Game
```bash
cd learning_game
pip install -r requirements.txt
python app.py
```

### Weather HUD
```bash
cd scripts
# Make sure OPENWEATHER_API_KEY is set in your environment
python weather_hud.py
```

### Snake Game
```bash
cd snake_game
make
./snake
```

## Security Note
API keys are stored in `.env` files that are excluded from version control. Never commit API keys to the repository.
