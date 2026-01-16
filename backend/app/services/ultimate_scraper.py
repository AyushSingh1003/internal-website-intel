import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import time
import re
from fake_useragent import UserAgent
import json


class UltimateWebScraper:
    """
    The most advanced web scraper - handles everything
    """
    
    def __init__(self, base_url: str, max_pages: int = 10, use_selenium: bool = True):
        self.base_url = self._normalize_url(base_url)
        self.max_pages = max_pages
        self.use_selenium = use_selenium
        self.visited_urls: Set[str] = set()
        self.scraped_pages: List[Dict] = []
        self.contact_forms: List[Dict] = []
        
        # Generate random user agent
        ua = UserAgent()
        self.user_agent = ua.random
        
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        self.selenium_driver: Optional[webdriver.Chrome] = None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL"""
        url = url.strip().rstrip('/')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is from same domain"""
        return self._get_domain(url) == self._get_domain(self.base_url)
    
    def _init_selenium(self):
        """Initialize Selenium driver"""
        if self.selenium_driver:
            return
        
        print("[Scraper] Initializing Selenium WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
            # Execute script to hide webdriver
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[Scraper] Selenium initialized successfully")
        except Exception as e:
            print(f"[Scraper] Selenium initialization failed: {e}")
            self.selenium_driver = None
    
    def _close_selenium(self):
        """Close Selenium driver"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                print("[Scraper] Selenium closed")
            except:
                pass
            self.selenium_driver = None
    
    def scrape(self) -> Dict:
        """
        Main scraping orchestrator
        """
        print(f"\n{'='*60}")
        print(f"[Scraper] ULTIMATE SCRAPER STARTING")
        print(f"[Scraper] Target: {self.base_url}")
        print(f"[Scraper] Max Pages: {self.max_pages}")
        print(f"[Scraper] Selenium: {'Enabled' if self.use_selenium else 'Disabled'}")
        print(f"{'='*60}\n")
        
        try:
            # Phase 1: Scrape homepage
            print("[Scraper] PHASE 1: Scraping Homepage")
            homepage_data = self._scrape_page(self.base_url, priority=True)
            
            if not homepage_data:
                return self._empty_result("Failed to scrape homepage")
            
            # Phase 2: Discover all relevant links
            print("\n[Scraper] PHASE 2: Discovering Links")
            all_links = self._discover_links(homepage_data)
            contact_links = self._prioritize_contact_links(all_links)
            
            print(f"[Scraper] Found {len(all_links)} total links")
            print(f"[Scraper] Found {len(contact_links)} priority contact links")
            
            # Phase 3: Scrape priority pages
            print("\n[Scraper] PHASE 3: Scraping Priority Pages")
            pages_to_scrape = contact_links[:self.max_pages - 1]
            
            for i, url in enumerate(pages_to_scrape, 1):
                if url in self.visited_urls:
                    continue
                
                print(f"[Scraper] Scraping page {i}/{len(pages_to_scrape)}: {url}")
                time.sleep(1)  # Polite delay
                self._scrape_page(url, priority=True)
            
            # Phase 4: Deep scrape with Selenium if enabled
            if self.use_selenium and len(self.scraped_pages) < 3:
                print("\n[Scraper] PHASE 4: Deep Selenium Scraping")
                self._selenium_deep_scrape([self.base_url] + contact_links[:2])
            
            # Phase 5: Detect contact forms
            print("\n[Scraper] PHASE 5: Detecting Contact Forms")
            self._detect_contact_forms()
            
            # Compile results
            combined_text = self._combine_text()
            combined_html = self._combine_html()
            
            print(f"\n{'='*60}")
            print(f"[Scraper] SCRAPING COMPLETE")
            print(f"[Scraper] Pages Scraped: {len(self.scraped_pages)}")
            print(f"[Scraper] Total Text Length: {len(combined_text):,} chars")
            print(f"[Scraper] Contact Forms Found: {len(self.contact_forms)}")
            print(f"{'='*60}\n")
            
            return {
                'base_url': self.base_url,
                'pages': self.scraped_pages,
                'combined_text': combined_text,
                'combined_html': combined_html,
                'pages_scraped': len(self.scraped_pages),
                'contact_forms': self.contact_forms,
                'metadata': {
                    'total_links_found': len(all_links),
                    'priority_links': len(contact_links),
                    'selenium_used': self.use_selenium,
                }
            }
            
        finally:
            self._close_selenium()
    
    def _scrape_page(self, url: str, priority: bool = False) -> Optional[Dict]:
        """
        Scrape single page with multiple strategies
        """
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        # Try static scraping first
        page_data = self._static_scrape(url)
        
        # If priority page and Selenium available, also try dynamic scraping
        if priority and self.use_selenium and page_data:
            dynamic_data = self._dynamic_scrape(url)
            if dynamic_data and len(dynamic_data['text']) > len(page_data.get('text', '')):
                print(f"[Scraper] ✓ Selenium found more content for {url}")
                page_data = dynamic_data
        
        if page_data:
            self.scraped_pages.append(page_data)
            return page_data
        
        return None
    
    def _static_scrape(self, url: str) -> Optional[Dict]:
        """
        Static HTML scraping with requests + BeautifulSoup
        """
        try:
            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Try multiple parsers for robustness
            for parser in ['lxml', 'html5lib', 'html.parser']:
                try:
                    soup = BeautifulSoup(response.content, parser)
                    break
                except:
                    continue
            else:
                print(f"[Scraper] ✗ All parsers failed for {url}")
                return None
            
            # Extract comprehensive data
            page_data = self._extract_page_data(soup, url, response.text)
            
            print(f"[Scraper] ✓ Static scrape: {len(page_data['text'])} chars")
            return page_data
            
        except Exception as e:
            print(f"[Scraper] ✗ Static scrape failed for {url}: {e}")
            return None
    
    def _dynamic_scrape(self, url: str) -> Optional[Dict]:
        """
        Dynamic JavaScript rendering with Selenium
        """
        try:
            self._init_selenium()
            
            if not self.selenium_driver:
                return None
            
            self.selenium_driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.selenium_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Scroll to load lazy content
            self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Get rendered HTML
            html = self.selenium_driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            page_data = self._extract_page_data(soup, url, html)
            
            print(f"[Scraper] ✓ Dynamic scrape: {len(page_data['text'])} chars")
            return page_data
            
        except Exception as e:
            print(f"[Scraper] ✗ Dynamic scrape failed for {url}: {e}")
            return None
    
    def _extract_page_data(self, soup: BeautifulSoup, url: str, raw_html: str) -> Dict:
        """
        Extract all useful data from parsed page
        """
        # Title
        title = ""
        if soup.title:
            title = soup.title.string.strip()
        
        # Meta description
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content']
        
        # Store original HTML before modification
        original_html = str(soup)
        
        # Remove noise but KEEP headers/footers (they have contact info!)
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'canvas']):
            tag.decompose()
        
        # Extract structured data (JSON-LD)
        structured_data = self._extract_structured_data(soup)
        
        # Get all visible text
        text = soup.get_text(separator=' ', strip=True)
        
        # Also get text from specific contact-heavy sections
        contact_sections = self._extract_contact_sections(soup)
        if contact_sections:
            text += "\n\n" + contact_sections
        
        # Extract all links
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if self._is_same_domain(full_url):
                links.append(full_url)
        
        # Extract all email/phone from HTML attributes
        attributes_data = self._extract_from_attributes(soup)
        
        # Extract visible contact info patterns
        visible_contacts = self._extract_visible_contacts(text)
        
        return {
            'url': url,
            'title': title,
            'meta_description': meta_desc,
            'text': text,
            'html': original_html,
            'links': list(set(links)),
            'structured_data': structured_data,
            'attributes_contacts': attributes_data,
            'visible_contacts': visible_contacts,
            'text_length': len(text)
        }
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Extract JSON-LD and microdata"""
        structured = {}
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Look for Organization data
                    if data.get('@type') == 'Organization':
                        structured['organization'] = data
                    # Look for contact point
                    if 'contactPoint' in data:
                        structured['contact_point'] = data['contactPoint']
            except:
                pass
        
        return structured
    
    def _extract_contact_sections(self, soup: BeautifulSoup) -> str:
        """Extract text from sections likely to have contact info"""
        contact_parts = []
        
        keywords = [
            'contact', 'footer', 'header', 'info', 'phone', 'email',
            'address', 'location', 'office', 'headquarters', 'reach',
            'connect', 'social', 'follow', 'touch', 'call', 'visit'
        ]
        
        # Search by class
        for keyword in keywords:
            elements = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
            for elem in elements[:3]:  # Limit per keyword
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:
                    contact_parts.append(text)
        
        # Search by id
        for keyword in keywords:
            elements = soup.find_all(id=lambda x: x and keyword in str(x).lower())
            for elem in elements[:3]:
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:
                    contact_parts.append(text)
        
        # Specific tags
        for tag_name in ['footer', 'header', 'address', 'aside']:
            for elem in soup.find_all(tag_name):
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:
                    contact_parts.append(text)
        
        return "\n\n".join(set(contact_parts))
    
    def _extract_from_attributes(self, soup: BeautifulSoup) -> Dict:
        """Extract contact info from HTML attributes"""
        emails = set()
        phones = set()
        
        # mailto: links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'mailto:' in href:
                email = href.split('mailto:')[-1].split('?')[0]
                emails.add(email)
        
        # tel: links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'tel:' in href:
                phone = href.split('tel:')[-1]
                phones.add(phone)
        
        # data-* attributes
        for tag in soup.find_all(attrs={'data-email': True}):
            emails.add(tag['data-email'])
        
        for tag in soup.find_all(attrs={'data-phone': True}):
            phones.add(tag['data-phone'])
        
        for tag in soup.find_all(attrs={'data-tel': True}):
            phones.add(tag['data-tel'])
        
        return {
            'emails': list(emails),
            'phones': list(phones)
        }
    
    def _extract_visible_contacts(self, text: str) -> Dict:
        """Quick extraction of visible contact patterns"""
        emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text, re.IGNORECASE))
        
        # Phone patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
            r'\b1800[-\s]?\d{3}[-\s]?\d{4}\b',
            r'\b\d{4}[-\s]?\d{3}[-\s]?\d{3}\b',
            r'\b\d{10}\b',
        ]
        phones = set()
        for pattern in phone_patterns:
            phones.update(re.findall(pattern, text))
        
        return {
            'emails': list(emails),
            'phones': list(phones)
        }
    
    def _discover_links(self, homepage_data: Dict) -> List[str]:
        """Discover all internal links"""
        all_links = set()
        
        for page in self.scraped_pages:
            all_links.update(page.get('links', []))
        
        # Remove anchors and query params for deduplication
        cleaned_links = set()
        for link in all_links:
            clean_link = link.split('#')[0].split('?')[0]
            if clean_link and self._is_valid_link(clean_link):
                cleaned_links.add(clean_link)
        
        return list(cleaned_links)
    
    def _is_valid_link(self, url: str) -> bool:
        """Check if link is worth scraping"""
        # Skip certain file types
        skip_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.css', '.js', '.xml', '.zip', '.doc', '.docx', '.xls',
            '.xlsx', '.ppt', '.pptx', '.mp4', '.mp3', '.avi', '.mov'
        ]
        
        url_lower = url.lower()
        return not any(url_lower.endswith(ext) for ext in skip_extensions)
    
    def _prioritize_contact_links(self, links: List[str]) -> List[str]:
        """Sort links by relevance to contact information"""
        scored_links = []
        
        # High priority keywords
        high_priority = [
            'contact', 'reach', 'get-in-touch', 'talk', 'connect'
        ]
        
        # Medium priority keywords
        medium_priority = [
            'about', 'team', 'people', 'company', 'who-we-are',
            'leadership', 'careers', 'jobs', 'location', 'office',
            'info', 'information', 'help', 'support', 'faq'
        ]
        
        for link in links:
            link_lower = link.lower()
            score = 0
            
            # Check high priority
            for keyword in high_priority:
                if keyword in link_lower:
                    score += 100
            
            # Check medium priority
            for keyword in medium_priority:
                if keyword in link_lower:
                    score += 10
            
            # Prefer shorter URLs (usually main pages)
            score -= len(link) * 0.01
            
            scored_links.append((score, link))
        
        # Sort by score descending
        scored_links.sort(reverse=True, key=lambda x: x[0])
        
        return [link for score, link in scored_links if score > 0]
    
    def _selenium_deep_scrape(self, urls: List[str]):
        """Deep scrape with Selenium for missed content"""
        self._init_selenium()
        
        if not self.selenium_driver:
            return
        
        for url in urls:
            if url in self.visited_urls:
                continue
            
            print(f"[Scraper] Deep Selenium scrape: {url}")
            self._dynamic_scrape(url)
            time.sleep(1)
    
    def _detect_contact_forms(self):
        """Detect contact forms in scraped pages"""
        for page in self.scraped_pages:
            soup = BeautifulSoup(page['html'], 'lxml')
            forms = soup.find_all('form')
            
            for form in forms:
                # Check if it's a contact form
                form_text = form.get_text().lower()
                form_html = str(form).lower()
                
                contact_indicators = [
                    'contact', 'message', 'inquiry', 'email',
                    'phone', 'reach', 'get in touch', 'name'
                ]
                
                if any(indicator in form_text or indicator in form_html for indicator in contact_indicators):
                    # Extract form details
                    action = form.get('action', '')
                    method = form.get('method', 'get')
                    
                    # Get input fields
                    inputs = []
                    for input_tag in form.find_all(['input', 'textarea', 'select']):
                        inputs.append({
                            'type': input_tag.get('type', 'text'),
                            'name': input_tag.get('name', ''),
                            'placeholder': input_tag.get('placeholder', ''),
                            'required': input_tag.has_attr('required')
                        })
                    
                    self.contact_forms.append({
                        'url': page['url'],
                        'action': action,
                        'method': method,
                        'fields': inputs
                    })
                    
                    print(f"[Scraper] ✓ Found contact form on {page['url']}")
    
    def _combine_text(self) -> str:
        """Combine all text from scraped pages"""
        parts = []
        
        for page in self.scraped_pages:
            parts.append(f"\n\n=== {page['title']} ({page['url']}) ===\n")
            parts.append(page['text'])
            
            # Add structured data if available
            if page.get('structured_data'):
                parts.append(f"\n\nStructured Data: {json.dumps(page['structured_data'], indent=2)}")
        
        return "\n".join(parts)
    
    def _combine_html(self) -> str:
        """Combine all HTML"""
        return "\n\n".join([page['html'] for page in self.scraped_pages])
    
    def _empty_result(self, error: str) -> Dict:
        """Return empty result"""
        return {
            'base_url': self.base_url,
            'pages': [],
            'combined_text': '',
            'combined_html': '',
            'pages_scraped': 0,
            'contact_forms': [],
            'error': error
        }


def scrape_website_ultimate(url: str, max_pages: int = 10, use_selenium: bool = True) -> Dict:
    """
    Main entry point for ultimate scraping
    """
    scraper = UltimateWebScraper(url, max_pages=max_pages, use_selenium=use_selenium)
    return scraper.scrape()
