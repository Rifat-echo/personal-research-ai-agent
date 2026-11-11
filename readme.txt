# Personal Research AI Agent

A Python-based AI assistant powered by Google Gemini, with business operations tools and global stock market research capabilities.

## Features

- Conversational AI powered by Google Gemini
- Business order lookup using SQLite
- Calculator tool
- Historical stock market data collection using yfinance
- MongoDB storage for market data
- Stock market trend analysis
- Support for S&P 500, FTSE 100, Nikkei 225, NIFTY 50, and DAX

## Technologies

Python, Google Gemini API, MongoDB, PyMongo, SQLite, yfinance, pandas

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Install and run MongoDB Community Server.
5. Create a `.env` file containing:
   - `GEMINI_API_KEY=your_api_key`
   - `MONGODB_URI=mongodb://127.0.0.1:27017/`
   - `MONGODB_DB=global_market_agent`
6. Run `python init_db.py` to initialize the business database.
7. Run `python init_market_db.py` to initialize the market database.
8. Run `python fetch_market_data.py` to collect historical market prices.
9. Run `python main.py` to start the assistant.

## Disclaimer

Market data is intended for research and educational purposes. Historical trends do not guarantee future performance.