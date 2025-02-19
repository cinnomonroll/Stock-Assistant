import os
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
import yfinance as yf
from newsapi import NewsApiClient
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize APIs
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
if not os.getenv("NEWS_API_KEY"):
    raise ValueError("NEWS_API_KEY is not set in the environment.")
openai = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

def get_stock_info(ticker):
    """Get real-time stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1d")
        
        current_price = info.get('currentPrice', 'N/A')
        previous_close = info.get('previousClose', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        volume = info.get('volume', 'N/A')
        company_name = info.get('longName', ticker)
        last_updated = history.index[-1].strftime('%Y-%m-%d %H:%M:%S') if not history.empty else 'N/A'
        
        return f"""
Company: {company_name}
Last Updated: {last_updated}
Current Price: ${current_price}
Previous Close: ${previous_close}
Market Cap: ${market_cap:,}
Volume: {volume:,}
"""
    except Exception as e:
        return f"Error fetching stock information: {str(e)}"

def get_financial_news(query):
    """Get latest financial news with summary"""
    try:
        news = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='publishedAt',
            from_param=(datetime.now() - timedelta(days=7)).date().isoformat()
        )
        if news['articles']:
            articles = news['articles'][:5]
            
            # Create a summary of all articles
            all_content = "\n\n".join([f"{article['title']}\n{article['description']}" 
                                     for article in articles if article['description']])
            
            llm = ChatOpenAI(temperature=0.3)
            
            # Create a document for summarization
            doc = Document(page_content=all_content)
            
            # Create the summarization chain
            chain = load_summarize_chain(
                llm,
                chain_type="stuff",
                verbose=True
            )
            
            summary = chain.run([doc])
            
            # Format individual articles
            articles_text = "\n\n".join([
                f"Title: {article['title']}\nDate: {article['publishedAt'][:10]}\nSource: {article['source']['name']}\nURL: {article['url']}" 
                for article in articles
            ])
            
            return f"""Summary of Recent News:
{summary}

Detailed Articles:
{articles_text}"""
        return "No news found."
    except Exception as e:
        return f"Error fetching news: {str(e)}"

# Initialize LangChain components
llm = ChatOpenAI(temperature=0.2)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create tools
tools = [
    Tool(
        name="StockInfo",
        func=get_stock_info,
        description="Useful for getting real-time stock information including company name, price, volume, and market cap. Input should be a valid stock ticker symbol (e.g., AAPL, TSLA, MSFT)."
    ),
    Tool(
        name="FinancialNews",
        func=get_financial_news,
        description="Useful for getting latest financial news. Input should be a search query related to financial news."
    )
]

# Initialize the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

def main():
    print("Financial Assistant: Hello! I can help you with stock information and financial news. What would you like to know?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Financial Assistant: Goodbye!")
            break
            
        try:
            response = agent.run(user_input)
            print(f"Financial Assistant: {response}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()