from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
import uvicorn
from gnews import GNews
import yfinance as yf
# Ref: https://github.com/modelcontextprotocol/python-sdk

# Create an MCP server
mcp = FastMCP("Custom MCP Server")
google_news = GNews(max_results=3)


@mcp.tool()
def get_latest_news(search: str):
    """search information on google news, and return relative news in full text, you need to analysis and provide a summary back to user"""
    try:
        # Perform a search using GNews
        news = google_news.get_news(search)
        if not news:
            return f"No news found for '{search}'."
        # Format the news results
        formatted_news = "\n".join([f"{item['title']}: {item['url']}" for item in news])
        return formatted_news
    except Exception as e:
        return f"Error fetching news: {str(e)}"

@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """
    Retrieve the current stock price for the given ticker symbol.
    Returns the latest closing price as a float.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get today's historical data; may return empty if market is closed or symbol is invalid.
        data = ticker.history(period="1d")
        if not data.empty:
            # Use the last closing price from today's data
            price = data['Close'].iloc[-1]
            return float(price)
        else:
            # As a fallback, try using the regular market price from the ticker info
            info = ticker.info
            price = info.get("regularMarketPrice", None)
            if price is not None:
                return float(price)
            else:
                return -1.0  # Indicate failure
    except Exception:
        # Return -1.0 to indicate an error occurred when fetching the stock price
        return -1.0
    
@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """
    Retrieve historical data for a stock given a ticker symbol and a period.
    Returns the historical data as a CSV formatted string.
    
    Parameters:
        symbol: The stock ticker symbol.
        period: The period over which to retrieve historical data (e.g., '1mo', '3mo', '1y').
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            return f"No historical data found for symbol '{symbol}' with period '{period}'."
        # Convert the DataFrame to a CSV formatted string
        csv_data = data.to_csv()
        return csv_data
    except Exception as e:
        return f"Error fetching historical data: {str(e)}"



app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8000, reload=False, log_level="debug")