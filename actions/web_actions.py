import webbrowser

def is_safe_url(url):
    return url.startswith("http")

def open_url(url):
    if not is_safe_url(url):
        return "Invalid URL"

    webbrowser.open(url)
    return "Opening website"

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for {query}"

