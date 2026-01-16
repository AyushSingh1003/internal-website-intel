import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import time
import re


class AdvancedWebsiteScraper:
    """
    Advanced scraper with multiple strategies for maximum compatibility
    """
    
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = self._normalize_url(base_url)
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.scraped_pages = []
    
    def _normalize_url(self, url: str) -> str:
        """Ensure URL has proper scheme"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is from same domain"""
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain
    
    def scrape(self) -> Dict:
        """
        Main scraping method with multiple strategies
        """
        print(f"[Scraper] Starting scrape of {self.base_url}")
        
        # Strategy 1: Scrape homepage
        homepage_data = self._scrape_page(self.base_url)
        if not homepage_data:
            return self._empty_result("Failed to scrape homepage")
        
        self.scraped_pages.append(homepage_data)
        
        # Strategy 2: Find and scrape contact-related pages
        contact_pages = self._find_contact_pages(homepage_data['links'])
        print(f"[Scraper] Found {len(contact_pages)} potential contact pages")
        
        for page_url in contact_pages[:4]:  # Limit to 4 additional pages
            time.sleep(0.5)  # Polite delay
            page_data = self._scrape_page(page_url)
            if page_data:
                self.scraped_pages.append(page_data)
        
        if not contact_pages:
            fallback_urls = self._fallback_contact_urls()
            for page_url in fallback_urls[:4]:
                time.sleep(0.5)
                page_data = self._scrape_page(page_url)
                if page_data:
                    self.scraped_pages.append(page_data)
        
        # Combine all content
        combined_text = "\n\n".join([p['text'] for p in self.scraped_pages])
        combined_html = "\n\n".join([p['html'] for p in self.scraped_pages])
        
        print(f"[Scraper] Scraped {len(self.scraped_pages)} pages, {len(combined_text)} chars")
        
        return {
            'base_url': self.base_url,
            'pages': self.scraped_pages,
            'combined_text': combined_text,
            'combined_html': combined_html,
            'pages_scraped': len(self.scraped_pages)
        }
    
    def _scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape single page with error handling"""
        try:
            print(f"[Scraper] Fetching {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Parse with lxml parser (faster and more robust)
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.title.string.strip() if soup.title else ""
            
            json_ld_texts = []
            for tag in soup.find_all('script', type='application/ld+json'):
                try:
                    json_ld_texts.append(tag.string or tag.get_text())
                except Exception:
                    pass
            
            # Remove unwanted elements but KEEP footer/header (they have contact info!)
            for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
                tag.decompose()
            
            # Get all text
            text = soup.get_text(separator=' ', strip=True)
            if json_ld_texts:
                text = text + "\n\n" + "\n\n".join(json_ld_texts)
            
            if len(text) < 200:
                try:
                    from playwright.sync_api import sync_playwright
                    print("[Scraper] Rendering JS with Playwright")
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        context = browser.new_context()
                        page = context.new_page()
                        page.goto(url, wait_until="networkidle")
                        content = page.content()
                        browser.close()
                    soup = BeautifulSoup(content, 'lxml')
                    text = soup.get_text(separator=' ', strip=True)
                except Exception as e:
                    print(f"[Scraper] Playwright fallback failed: {e}")
            
            # Also get text from specific contact-relevant sections
            contact_text = self._extract_contact_sections(soup)
            if contact_text:
                text = text + "\n\n" + contact_text
            
            scripts = []
            for script in soup.find_all('script', src=True):
                scripts.append(urljoin(url, script['src']))
            js_texts = []
            for s in scripts[:3]:
                try:
                    r = requests.get(s, headers=self.headers, timeout=self.timeout)
                    if r.status_code == 200 and len(r.text) < 2_000_000:
                        js_texts.append(r.text)
                except Exception as e:
                    pass
            if js_texts:
                text = text + "\n\n" + "\n\n".join(js_texts)
            
            # Get all links
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if self._is_same_domain(full_url) and full_url not in links:
                    links.append(full_url)
            
            return {
                'url': url,
                'title': title,
                'text': text,
                'html': str(soup),
                'links': links
            }
            
        except Exception as e:
            print(f"[Scraper] Error scraping {url}: {e}")
            return None
    
    def _extract_contact_sections(self, soup: BeautifulSoup) -> str:
        """Extract text from sections likely to contain contact info"""
        contact_text_parts = []
        
        # Look for elements with contact-related classes/ids
        contact_keywords = [
            'contact', 'footer', 'header', 'info', 'phone', 'email',
            'address', 'location', 'reach', 'connect', 'social'
        ]
        
        for keyword in contact_keywords:
            # Find by class
            elements = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
            for elem in elements:
                contact_text_parts.append(elem.get_text(separator=' ', strip=True))
            
            # Find by id
            elements = soup.find_all(id=lambda x: x and keyword in str(x).lower())
            for elem in elements:
                contact_text_parts.append(elem.get_text(separator=' ', strip=True))
        
        # Also check footer, header, address tags explicitly
        for tag_name in ['footer', 'header', 'address']:
            for elem in soup.find_all(tag_name):
                contact_text_parts.append(elem.get_text(separator=' ', strip=True))
        
        return "\n".join(contact_text_parts)
    
    def _find_contact_pages(self, links: List[str]) -> List[str]:
        """Find links likely to be contact/about pages"""
        contact_keywords = [
            'contact', 'about', 'team', 'connect', 'reach',
            'phone', 'email', 'location', 'office', 'headquarters',
            'get-in-touch', 'contact-us', 'about-us', 'who-we-are'
        ]
        
        contact_pages = []
        for link in links:
            link_lower = link.lower()
            # Check if URL contains contact keywords
            if any(keyword in link_lower for keyword in contact_keywords):
                # Avoid duplicates and non-page URLs
                if link not in contact_pages and not link.endswith(('.pdf', '.jpg', '.png', '.gif')):
                    contact_pages.append(link)
        
        return contact_pages
    
    def _empty_result(self, reason: str) -> Dict:
        """Return empty result with error message"""
        return {
            'base_url': self.base_url,
            'pages': [],
            'combined_text': '',
            'combined_html': '',
            'pages_scraped': 0,
            'error': reason
        }

    def _fallback_contact_urls(self) -> List[str]:
        """Build common contact/about pages when homepage has few links"""
        candidates = [
            'contact',
            'contact-us',
            'about',
            'about-us',
            'stores',
            'store',
            'locations',
            'support',
            'customer-care',
            'reach-us'
        ]
        urls: List[str] = []
        for path in candidates:
            urls.append(urljoin(self.base_url.rstrip('/') + '/', path))
        return urls


def scrape_website_advanced(url: str) -> Dict:
    """Main function to scrape website with advanced strategies"""
    scraper = AdvancedWebsiteScraper(url)
    return scraper.scrape()
