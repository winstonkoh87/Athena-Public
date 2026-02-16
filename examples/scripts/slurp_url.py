import sys
import re
import requests
from bs4 import BeautifulSoup

def slurp_url(url):
    """
    Generic content extractor for the Bionic Unit.
    Fetches URL, attempts to isolate the main content (article/post),
    and converts it to clean Markdown.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        print(f"Checking URL: {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Extract Title
        title = "Unknown Title"
        # Try metadata first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
        else:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)

        print(f"=== {title} ===\n")
        print(f"URL: {url}\n")
        print("-" * 40 + "\n")

        # 2. Heuristic Content Extraction
        # We look for common semantic tags or large blocks of text
        
        # Strategy A: Specific Forum tags (XenForo/EDMW style)
        posts = soup.find_all('article', class_='message')
        if posts:
            print("[Detected Forum Format]\n")
            for i, post in enumerate(posts):
                user_tag = post.find('h4', class_='message-name')
                user = user_tag.get_text(strip=True) if user_tag else "Anonymous"
                content_div = post.find('div', class_='bbWrapper')
                if content_div:
                    # Mark quotes
                    for bq in content_div.find_all('blockquote'):
                        bq.insert_before("> [Quote Start]\n")
                        bq.insert_after("\n> [Quote End]\n")
                    text = content_div.get_text(separator='\n', strip=True)
                    text = re.sub(r'\n{3,}', '\n\n', text)
                    print(f"#{i+1} | Author: {user}")
                    print("-" * 20)
                    print(text)
                    print("\n" + "=" * 40 + "\n")
            return

        # Strategy B: Article Body (Semantic)
        article = soup.find('article')
        if article:
            main_content = article
        else:
            # Fallback to <main>
            main_content = soup.find('main')
            
        if not main_content:
            # Fallback to finding the div with the most p tags
            max_p = 0
            candidate = None
            for div in soup.find_all('div'):
                p_count = len(div.find_all('p', recursive=False)) # Direct children preferred
                if p_count > max_p:
                    max_p = p_count
                    candidate = div
            main_content = candidate

        if main_content:
            # Cleanup noise within content
            for tag in main_content(['script', 'style', 'nav', 'footer', 'aside']):
                tag.decompose()
            
            text = main_content.get_text(separator='\n\n', strip=True)
            # Normalize whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            print(text)
        else:
            print("⚠️ Could not heuristically isolate main content. Dumping raw text extraction:")
            print("-" * 20)
            print(soup.get_text(separator='\n\n', strip=True))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 slurp_url.py <URL>")
    else:
        slurp_url(sys.argv[1])
