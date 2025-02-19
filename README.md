# Financial Assistant

A comprehensive financial assistant with a React.js web interface that provides real-time stock information, financial news, and document analysis capabilities using LangChain, OpenAI, Yahoo Finance, and NewsAPI.

## Features
- Real-time stock information retrieval
- Latest financial news updates
- Document upload and summarization (supports PDF, DOCX, and TXT files)
- Modern React.js web interface
- Conversational interface with memory
- Vector database support for efficient data retrieval

## Backend Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   NEWS_API_KEY=your_newsapi_key
   ```

3. Run the Flask backend:
   ```bash
   python app.py
   ```

## Frontend Setup
1. Install Node.js and npm if you haven't already
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```

The web interface will be available at `http://localhost:3000`

## Usage
Through the web interface, you can:
- Search for stock information by entering a ticker symbol
- Get financial news by entering a search query
- Upload and analyze documents (PDF, DOCX, TXT) for summarization

## API Endpoints
- `GET /api/stock/<ticker>` - Get stock information
- `GET /api/news/<query>` - Get financial news
- `POST /api/upload` - Upload and analyze documents

## Technologies Used
- Backend:
  - Flask
  - LangChain
  - OpenAI
  - ChromaDB
  - Yahoo Finance
  - NewsAPI
- Frontend:
  - React.js
  - Material-UI
  - Axios