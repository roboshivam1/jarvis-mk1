from ddgs import DDGS
import webbrowser

def search_web(query: str) -> str:
    """
    Searches the internet for up-to-date information, news, or facts.
    Use this tool when the user asks a question that requires current world knowledge.
    
    :param query: The specific search query to look up.
    """
    try:
        # We limit to 3 results so we don't overload Ollama's context window
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found on the web."
        
        # Format the top results into a clean string for JARVIS to read
        formatted_results = "Here are the top web search results:\n\n"
        for i, res in enumerate(results):
            formatted_results += f"Result {i+1}:\nTitle: {res['title']}\nSnippet: {res['body']}\n\n"
            
        return formatted_results.strip()
    except Exception as e:
        return f"Error searching the web: {e}"

def open_website(url: str) -> str:
    """
    Opens a specific website URL in the user's default web browser.
    Use this tool ONLY when the user explicitly asks to open or navigate to a website.
    
    :param url: The website address to open (e.g., 'youtube.com' or 'github.com').
    """
    try:
        # Python's built-in webbrowser module needs 'https://' to work properly
        if not url.startswith("http"):
            url = "https://" + url
            
        webbrowser.open(url)
        return f"Successfully opened {url} in the browser."
    except Exception as e:
        return f"Error opening website: {e}"

# We create a separate dictionary for these specific tools
WEB_TOOLS = {
    "search_web": search_web,
    "open_website": open_website
}