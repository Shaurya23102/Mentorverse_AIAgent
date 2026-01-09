import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import re

class RobustCrawler:
    def __init__(self, base_url, max_pages=10):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque([base_url])
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def get_clean_text(self, soup):
        """Extracts only human-readable text."""
        # Remove non-visible elements
        for element in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside']):
            element.decompose()
        
        # Get text and clean up whitespaces/newlines
        raw_text = soup.get_text(separator=' ')
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        return clean_text

    def crawl(self):
        pages_scraped = 0
        
        while self.queue and pages_scraped < self.max_pages:
            url = self.queue.popleft()
            
            if url in self.visited:
                continue

            try:
                print(f"Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                self.visited.add(url)
                pages_scraped += 1

                # 1. Extract and Save Text
                page_text = self.get_clean_text(soup)
                self.save_data(url, page_text)

                # 2. Find and Queue new links
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(self.base_url, link['href'])
                    
                    # Ensure the link is within the same domain and hasn't been visited
                    if urlparse(full_url).netloc == self.domain and full_url not in self.visited:
                        self.queue.append(full_url)
                
                # Polite delay to avoid getting blocked
                time.sleep(1)

            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

    def save_data(self, url, text):
        """Saves output to a text file."""
        with open("scraped_data.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- URL: {url} ---\n")
            f.write(text + "\n")

# Usage
if __name__ == "__main__":
    # Replace with your target website
    crawler = RobustCrawler("", max_pages=5)
    crawler.crawl()
    print("\nScraping Complete. Check 'scraped_data.txt'.")