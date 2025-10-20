# web content scraping tools for agent calling
import requests
from bs4 import BeautifulSoup
import logging

def fetch_webpage(url: str):
    '''
    fetch_webpage: fetch and extract main text content from a webpage
    args: url - the webpage URL to fetch
    return: extracted text content or error message starting with "error in fetching webpage"
    '''
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
        
    except requests.exceptions.RequestException as e:
        return f"error in fetching webpage {url}: {str(e)}"
    except Exception as e:
        return f"error in fetching webpage {url}: {str(e)}"


def fetch_webpage_with_selector(url: str, selector: str = "body"):
    '''
    fetch_webpage_with_selector: fetch webpage and extract content using CSS selector
    args: 
        url - the webpage URL to fetch
        selector - CSS selector to target specific elements (default: "body")
    return: extracted text content from selected elements or error message
    '''
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find elements using CSS selector
        elements = soup.select(selector)
        
        if not elements:
            return f"No elements found with selector: {selector}"
        
        # Extract text from all matching elements
        texts = []
        for element in elements:
            text = element.get_text(strip=True)
            if text:
                texts.append(text)

        return '\n\n'.join(texts)
        
    except requests.exceptions.RequestException as e:
        return f"error in fetching webpage {url}: {str(e)}"
    except Exception as e:
        return f"error in fetching webpage {url}: {str(e)}"