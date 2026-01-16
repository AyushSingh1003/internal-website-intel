import re
from typing import List, Dict, Set
from bs4 import BeautifulSoup
import html as html_lib
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse


class UltimateContactExtractor:
    """
    Military-grade contact extraction with validation
    """
    
    def __init__(self, scraped_data: Dict):
        self.scraped_data = scraped_data
        self.pages = scraped_data.get('pages', [])
        self.combined_text = scraped_data.get('combined_text', '')
        self.combined_html = scraped_data.get('combined_html', '')
        self.base_url = scraped_data.get('base_url', '')
        self.default_region = self._infer_region()
    
    def _infer_region(self) -> str:
        url = self.base_url or (self.pages[0]['url'] if self.pages else '')
        host = urlparse(url).hostname or ''
        h = host.lower() if host else ''
        t = self.combined_text.lower()
        if h.endswith('.in') or h.endswith('.co.in'):
            return 'IN'
        indian_markers = [' india', ' mumbai', ' pune', ' delhi', ' bengaluru', ' bangalore', ' chennai', ' kolkata', ' maharashtra']
        if any(m in t for m in indian_markers):
            return 'IN'
        if ' 1800' in t or '+91' in t or 'whatsapp' in t:
            return 'IN'
        return 'US'
    
    def extract_all(self) -> Dict:
        """
        Extract everything
        """
        print(f"\n{'='*60}")
        print("[Extractor] ULTIMATE EXTRACTION STARTING")
        print(f"{'='*60}\n")
        
        emails = self._extract_emails()
        phones = self._extract_phones()
        socials = self._extract_socials()
        addresses = self._extract_addresses()
        
        print(f"\n{'='*60}")
        print("[Extractor] EXTRACTION COMPLETE")
        print(f"[Extractor] Emails: {len(emails)}")
        print(f"[Extractor] Phones: {len(phones)}")
        print(f"[Extractor] Socials: {len(socials)}")
        print(f"[Extractor] Addresses: {len(addresses)}")
        print(f"{'='*60}\n")
        
        return {
            'emails': emails,
            'phone_numbers': phones,
            'socials': socials,
            'addresses': addresses
        }
    
    def _extract_emails(self) -> List[str]:
        """
        Ultra-comprehensive email extraction
        """
        print("[Extractor] Extracting emails...")
        emails = set()
        
        # Strategy 1: From HTML attributes (most reliable)
        for page in self.pages:
            attr_emails = page.get('attributes_contacts', {}).get('emails', [])
            emails.update(attr_emails)
        print(f"[Extractor] Strategy 1 (attributes): {len(emails)} emails")
        
        # Strategy 2: From visible text
        for page in self.pages:
            visible = page.get('visible_contacts', {}).get('emails', [])
            emails.update(visible)
        print(f"[Extractor] Strategy 2 (visible): +{len(emails) - len(emails)} emails")
        
        # Strategy 3: Comprehensive regex on all text
        pattern = r'\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Z|a-z]{2,}\b'
        
        # Search in combined text
        found = set(re.findall(pattern, self.combined_text, re.IGNORECASE))
        emails.update(found)
        
        # Search in HTML
        found_html = set(re.findall(pattern, self.combined_html, re.IGNORECASE))
        emails.update(found_html)
        
        # Search in decoded text
        decoded = html_lib.unescape(self.combined_text)
        found_decoded = set(re.findall(pattern, decoded, re.IGNORECASE))
        emails.update(found_decoded)
        
        print(f"[Extractor] Strategy 3 (regex): +{len(found) + len(found_html) + len(found_decoded)} emails")
        
        # Strategy 4: Obfuscated patterns
        obfuscated = self.combined_text.lower()
        replacements = {
            ' at ': '@', ' dot ': '.', '[at]': '@', '[dot]': '.',
            '(at)': '@', '(dot)': '.', ' AT ': '@', ' DOT ': '.',
            '<at>': '@', '<dot>': '.', '{at}': '@', '{dot}': '.'
        }
        for old, new in replacements.items():
            obfuscated = obfuscated.replace(old, new)
        
        found_obf = set(re.findall(pattern, obfuscated, re.IGNORECASE))
        emails.update(found_obf)
        print(f"[Extractor] Strategy 4 (obfuscated): +{len(found_obf)} emails")
        
        # Strategy 5: From structured data
        for page in self.pages:
            structured = page.get('structured_data', {})
            if 'organization' in structured:
                org = structured['organization']
                if 'email' in org:
                    emails.add(org['email'])
                if 'contactPoint' in org:
                    cp = org['contactPoint']
                    if isinstance(cp, dict) and 'email' in cp:
                        emails.add(cp['email'])
                    elif isinstance(cp, list):
                        for item in cp:
                            if isinstance(item, dict) and 'email' in item:
                                emails.add(item['email'])
        
        # Validate and filter
        validated = self._validate_emails(emails)
        
        print(f"[Extractor] Total valid emails: {len(validated)}")
        return sorted(list(validated))
    
    def _validate_emails(self, emails: Set[str]) -> Set[str]:
        validated = set()
        blacklist = [
            'example.com', 'test.com', 'domain.com', 'yourcompany.com',
            'yourdomain.com', 'company.com', 'email.com', 'mail.com',
            'sentry.io', 'schema.org', 'wix.com', 'wordpress.com',
            'gravatar.com', 'w3.org', 'localhost', '127.0.0.1',
            'googleusercontent.com', 'googleapis.com',
            'noreply', 'no-reply', 'donotreply', 'mailer-daemon',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js'
        ]
        for email in emails:
            email_clean = email.lower().strip()
            if not (5 <= len(email_clean) <= 254):
                continue
            if any(bad in email_clean for bad in blacklist):
                continue
            if email_clean.count('@') != 1:
                continue
            try:
                valid = validate_email(email_clean, check_deliverability=False)
                validated.add(valid.email)
            except EmailNotValidError:
                continue
        return validated

    def _extract_phones(self) -> List[str]:
        print("[Extractor] Extracting phone numbers...")
        raw = set()
        source_scores = {}
        for page in self.pages:
            attr_phones = page.get('attributes_contacts', {}).get('phones', [])
            for p in attr_phones:
                raw.add(p)
                k = re.sub(r'[^\d+]', '', str(p))
                source_scores[k] = source_scores.get(k, 0) + 3
        for page in self.pages:
            visible = page.get('visible_contacts', {}).get('phones', [])
            for p in visible:
                raw.add(p)
                k = re.sub(r'[^\d+]', '', str(p))
                source_scores[k] = source_scores.get(k, 0) + 2
        search_text = self.combined_text + " " + html_lib.unescape(self.combined_text)
        india_patterns = [
            r'\b1800[-\s]?\d{3}[-\s]?\d{4}\b',
            r'\b\d{4}[-\s]?\d{3}[-\s]?\d{3}\b',
            r'\b\d{10}\b',
        ]
        us_patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
        ]
        patterns = india_patterns + us_patterns
        for pattern in patterns:
            for m in re.findall(pattern, search_text):
                raw.add(m)
                k = re.sub(r'[^\d+]', '', str(m))
                source_scores[k] = source_scores.get(k, 0) + 1
        context_raw = set()
        keywords = ['contact', 'call', 'phone', 'tel', 'support', 'care', 'customer', 'reach', 'help', 'whatsapp']
        for line in self.combined_text.splitlines():
            if any(k in line.lower() for k in keywords):
                for pattern in patterns:
                    for m in re.findall(pattern, line):
                        context_raw.add(m)
        if context_raw:
            raw.update(context_raw)
            for m in context_raw:
                k = re.sub(r'[^\d+]', '', str(m))
                source_scores[k] = source_scores.get(k, 0) + 2
        structured_phones = set()
        for page in self.pages:
            sd = page.get('structured_data', {})
            org = sd.get('organization') if isinstance(sd, dict) else {}
            if isinstance(org, dict):
                if 'telephone' in org and isinstance(org['telephone'], str):
                    structured_phones.add(org['telephone'])
                cp = org.get('contactPoint')
                if isinstance(cp, dict) and 'telephone' in cp:
                    structured_phones.add(cp['telephone'])
                if isinstance(cp, list):
                    for item in cp:
                        if isinstance(item, dict) and 'telephone' in item and isinstance(item['telephone'], str):
                            structured_phones.add(item['telephone'])
                            k = re.sub(r'[^\d+]', '', str(item['telephone']))
                            source_scores[k] = source_scores.get(k, 0) + 3
        raw.update(structured_phones)
        cleaned = set()
        for p in raw:
            s = re.sub(r'[^\d+]', '', str(p))
            if s.startswith('00'):
                s = '+' + s[2:]
            if 10 <= len(re.sub(r'[^\d]', '', s)) <= 15:
                cleaned.add(s)
        # Remove US-style duplicates of Indian 1800 numbers (e.g., 8002665300 when 18002665300 exists)
        try:
            digits_cleaned = {re.sub(r'[^0-9]', '', x) for x in cleaned}
            tollfree_suffixes = {d[1:] for d in digits_cleaned if d.startswith('1800') and len(d) == 11}
            if tollfree_suffixes:
                cleaned = {x for x in cleaned if re.sub(r'[^0-9]', '', x) not in tollfree_suffixes}
        except:
            pass
        validated = set()
        for phone in cleaned:
            if self._validate_phone(phone):
                try:
                    pr = phonenumbers.parse(phone, self.default_region)
                except:
                    try:
                        pr = phonenumbers.parse("+" + phone if not phone.startswith('+') else phone, None)
                    except:
                        pr = None
                if pr and phonenumbers.is_valid_number(pr):
                    e164 = phonenumbers.format_number(pr, phonenumbers.PhoneNumberFormat.E164)
                    digits_key = re.sub(r'[^0-9]', '', e164)
                    score = source_scores.get(digits_key, source_scores.get(re.sub(r'[^0-9]', '', phone), 0))
                    if score >= 2:
                        validated.add(e164)
        formatted = self._format_phones(validated)
        print(f"[Extractor] Total valid phones: {len(formatted)}")
        return formatted

    def _validate_phone(self, phone: str) -> bool:
        if not (10 <= len(phone) <= 15):
            return False
        if phone.isdigit():
            num = int(phone)
            if 1900 <= num <= 2100:
                return False
            if 10000 <= num <= 99999:
                return False
            if len(set(phone)) <= 2:
                return False
        try:
            parsed = phonenumbers.parse(phone, self.default_region)
            if phonenumbers.is_valid_number(parsed):
                return True
            parsed = phonenumbers.parse("+" + phone if not phone.startswith('+') else phone, None)
            return phonenumbers.is_valid_number(parsed)
        except:
            return True if 10 <= len(phone) <= 15 else False

    def _format_phones(self, phones: Set[str]) -> List[str]:
        formatted = []
        for phone in sorted(phones):
            try:
                parsed = phonenumbers.parse(phone, None)
                digits = re.sub(r'[^0-9]', '', phone)
                if digits.startswith('911800') and len(digits) == 13:
                    formatted.append(f"{digits[2:6]}-{digits[6:9]}-{digits[9:]}")
                elif digits.startswith('91') and len(digits) == 12:
                    formatted.append(f"{digits[2:6]}-{digits[6:9]}-{digits[9:]}")
                elif digits.startswith('1800') and len(digits) == 11:
                    formatted.append(f"{digits[:4]}-{digits[4:7]}-{digits[7:]}")
                elif self.default_region == 'IN' and len(digits) == 10:
                    formatted.append(f"{digits[:4]}-{digits[4:7]}-{digits[7:]}")
                else:
                    formatted.append(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL))
            except:
                if len(phone) == 10 and phone.isdigit():
                    formatted.append(f"({phone[:3]}) {phone[3:6]}-{phone[6:]}")
                else:
                    formatted.append(phone)
        return formatted

    def _extract_socials(self) -> List[Dict[str, str]]:
        print("[Extractor] Extracting social media...")
        socials = []
        seen = set()
        search_content = self.combined_text + ' ' + self.combined_html
        platforms = {
            'LinkedIn': [
                r'linkedin\.com/company/[^\s\"\'\)><\]]+',
                r'linkedin\.com/in/[^\s\"\'\)><\]]+',
                r'linkedin\.com/school/[^\s\"\'\)><\]]+'
            ],
            'Twitter': [
                r'twitter\.com/[^\s\"\'\)><\]]+',
                r'x\.com/[^\s\"\'\)><\]]+'
            ],
            'Facebook': [
                r'facebook\.com/[^\s\"\'\)><\]]+',
                r'fb\.com/[^\s\"\'\)><\]]+'
            ],
            'Instagram': [r'instagram\.com/[^\s\"\'\)><\]]+'],
            'YouTube': [
                r'youtube\.com/[^\s\"\'\)><\]]+',
                r'youtu\.be/[^\s\"\'\)><\]]+'
            ],
            'GitHub': [r'github\.com/[^\s\"\'\)><\]]+'],
            'TikTok': [r'tiktok\.com/@[^\s\"\'\)><\]]+'],
            'Pinterest': [r'pinterest\.com/[^\s\"\'\)><\]]+'],
        }
        for platform, patterns in platforms.items():
            for pattern in patterns:
                matches = re.finditer(pattern, search_content, re.IGNORECASE)
                for match in matches:
                    url = match.group(0)
                    url = url.rstrip('"\'>).,:;!?]')
                    if not url.startswith('http'):
                        url = 'https://' + url
                    if url not in seen and len(url) < 200:
                        socials.append({'platform': platform, 'url': url})
                        seen.add(url)
        print(f"[Extractor] Found {len(socials)} social links")
        return socials

    def _extract_addresses(self) -> List[str]:
        print("[Extractor] Extracting addresses...")
        addresses = set()
        patterns = [
            r'\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Court|Ct\.?|Way|Circle|Parkway|Plaza|Square),?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?',
            r'\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Court|Ct\.?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, self.combined_text, re.IGNORECASE)
            for match in matches:
                if 15 < len(match) < 300:
                    addresses.add(match.strip())
        for page in self.pages:
            soup = BeautifulSoup(page['html'], 'lxml')
            for tag in soup.find_all('address'):
                addr = tag.get_text(strip=True)
                if 10 < len(addr) < 300:
                    addresses.add(addr)
        for page in self.pages:
            structured = page.get('structured_data', {})
            if 'organization' in structured:
                org = structured['organization']
                if 'address' in org:
                    addr = org['address']
                    if isinstance(addr, dict):
                        street = addr.get('streetAddress', '')
                        city = addr.get('addressLocality', '')
                        state = addr.get('addressRegion', '')
                        zip_code = addr.get('postalCode', '')
                        full = f"{street}, {city}, {state} {zip_code}".strip()
                        if len(full) > 15:
                            addresses.add(full)
                    elif isinstance(addr, str):
                        addresses.add(addr)
        print(f"[Extractor] Found {len(addresses)} addresses")
        return sorted(list(addresses))
def extract_contacts_ultimate(scraped_data: Dict) -> Dict:
    """Main entry point for ultimate extraction"""
    try:
        extractor = UltimateContactExtractor(scraped_data)
        return extractor.extract_all()
    except Exception:
        text = scraped_data.get('combined_text', '') or ''
        html = scraped_data.get('combined_html', '') or ''
        # Minimal fallback using regex only
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phones = set()
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b\d{10,15}\b',
        ]
        search_text = ' '.join([text, html])
        for pat in phone_patterns:
            for m in re.findall(pat, search_text):
                cleaned = re.sub(r'[^\d+]', '', m)
                if 10 <= len(cleaned) <= 15:
                    phones.add(cleaned)
        emails = set(re.findall(email_pattern, search_text, re.IGNORECASE))
        socials = []
        for platform, pats in {
            'LinkedIn': [r'linkedin\.com/[^\s\"\'\)><]+'],
            'Facebook': [r'facebook\.com/[^\s\"\'\)><]+', r'fb\.com/[^\s\"\'\)><]+'],
            'Instagram': [r'instagram\.com/[^\s\"\'\)><]+'],
            'Twitter/X': [r'twitter\.com/[^\s\"\'\)><]+', r'x\.com/[^\s\"\'\)><]+'],
            'YouTube': [r'youtube\.com/[^\s\"\'\)><]+', r'youtu\.be/[^\s\"\'\)><]+'],
        }.items():
            for pat in pats:
                for m in re.finditer(pat, search_text, re.IGNORECASE):
                    url = m.group(0).rstrip('"\'>).,:;!?')
                    if not url.startswith('http'):
                        url = 'https://' + url
                    socials.append({'platform': platform, 'url': url})
        return {
            'emails': sorted(list(emails)),
            'phone_numbers': sorted(list(phones)),
            'socials': socials,
            'addresses': []
        }
