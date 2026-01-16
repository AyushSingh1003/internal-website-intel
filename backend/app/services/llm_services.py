import json
from typing import Dict, Any
import requests
from openai import OpenAI
from app.config import get_settings
from app.schemas.scan import ScanResult

settings = get_settings()


class LLMService:
    """Service for interacting with LLM to generate structured output"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        
        if self.provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set in environment")
            self.api_key = settings.GEMINI_API_KEY
            self.model_path = settings.LLM_MODEL_GEMINI
            self.endpoint = f"https://generativelanguage.googleapis.com/v1/{self.model_path}:generateContent"
            
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = settings.LLM_MODEL_OPENAI
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _build_prompt(self, website_url: str, scraped_text: str, extracted_contacts: Dict) -> str:
        """Build the prompt for LLM"""
        
        prompt = f"""You are a data extraction specialist. Analyze the following website content and extract structured company information.

Website URL: {website_url}

Scraped Content:
{scraped_text[:15000]}  

Already Extracted Contacts via Regex (USE THESE - they are from the actual page):
- Emails: {', '.join(extracted_contacts.get('emails', [])) or 'None found'}
- Phone Numbers: {', '.join(extracted_contacts.get('phone_numbers', [])) or 'None found'}
- Social Media: {', '.join([f"{s['platform']}: {s['url']}" for s in extracted_contacts.get('socials', [])]) or 'None found'}
- Addresses: {', '.join(extracted_contacts.get('addresses', [])) or 'None found'}

IMPORTANT INSTRUCTIONS:
1. ALWAYS include ALL emails, phone numbers, and addresses from the "Already Extracted Contacts" section above
2. If the regex extraction found contacts, you MUST include them in your response
3. Look for additional contacts in the scraped content that regex might have missed
4. Do NOT say "no contact information found" if regex extracted any - USE WHAT WAS FOUND
5. Identify the company name from the content
6. Write a concise 1-3 line summary of what the company does
7. List ALL social media links found
8. Add relevant notes about the company, services, locations, etc.
9. List the source URLs where information was found

CRITICAL: You must respond with ONLY a valid JSON object. No markdown, no code blocks, no explanation.

Required JSON structure:
{{
  "company_name": "string",
  "website": "{website_url}",
  "summary": "string (1-3 sentences about what the company does)",
  "emails": {extracted_contacts.get('emails', [])},
  "phone_numbers": {extracted_contacts.get('phone_numbers', [])},
  "socials": [
    {{"platform": "string", "url": "string"}}
  ],
  "addresses": {extracted_contacts.get('addresses', [])},
  "notes": "string with additional relevant information",
  "sources": ["{website_url}"]
}}

START YOUR RESPONSE WITH THE JSON OBJECT ONLY. Include AT MINIMUM the emails and phone numbers listed above."""
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        models = [
            self.model_path,
            "models/gemini-2.5-flash",
            "models/gemini-2.5-flash-lite",
            "models/gemini-2.0-flash",
            "models/gemini-2.0-flash-001",
        ]
        last_error = None
        for m in models:
            url = f"https://generativelanguage.googleapis.com/v1/{m}:generateContent?key={self.api_key}"
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "".join([p.get("text", "") for p in parts]).strip()
                if not text:
                    last_error = ValueError("Gemini returned empty content")
                    continue
                if text.startswith("```"):
                    segments = text.split("```", 2)
                    if len(segments) > 1:
                        text = segments[1]
                        if text.startswith("json"):
                            text = text[4:]
                        text = text.strip()
                try:
                    return json.loads(text)
                except Exception as e:
                    last_error = e
                    continue
            else:
                body = resp.text
                if resp.status_code in (404, 429):
                    last_error = ValueError(f"Gemini error {resp.status_code}: {body}")
                    continue
                last_error = ValueError(f"Gemini error {resp.status_code}: {body}")
                break
        if last_error:
            raise last_error
        raise ValueError("Gemini request failed")
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API with structured output"""
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction specialist. You always respond with valid JSON only, no markdown or explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
            json_text = json_text.strip()
        
        return json.loads(json_text)
    
    def generate_structured_output(
        self,
        website_url: str,
        scraped_text: str,
        extracted_contacts: Dict
    ) -> ScanResult:
        """
        Generate structured output from scraped content
        Returns validated ScanResult object
        """
        
        # Build prompt
        prompt = self._build_prompt(website_url, scraped_text, extracted_contacts)
        
        # Call appropriate LLM
        if self.provider == "gemini":
            raw_json = self._call_gemini(prompt)
        else:
            raw_json = self._call_openai(prompt)
        
        # Validate with Pydantic
        # This will raise ValidationError if JSON doesn't match schema
        structured_result = ScanResult(**raw_json)
        
        merged_emails = sorted(list({*(structured_result.emails or []), *map(str, extracted_contacts.get('emails', []))}))
        merged_phones = sorted(list({*(structured_result.phone_numbers or []), *map(str, extracted_contacts.get('phone_numbers', []))}))
        existing_socials = {s['url']: s for s in [{'platform': s.platform, 'url': s.url} for s in (structured_result.socials or [])]}
        for s in extracted_contacts.get('socials', []):
            u = s.get('url')
            if u and u not in existing_socials:
                existing_socials[u] = {'platform': s.get('platform', ''), 'url': u}
        merged_socials = [{'platform': v['platform'], 'url': v['url']} for v in existing_socials.values()]
        merged_addresses = sorted(list({*(structured_result.addresses or []), *map(str, extracted_contacts.get('addresses', []))}))
        data = structured_result.model_dump()
        data.update({
            'emails': merged_emails,
            'phone_numbers': merged_phones,
            'socials': merged_socials,
            'addresses': merged_addresses
        })
        return ScanResult(**data)


def process_with_llm(website_url: str, scraped_text: str, extracted_contacts: Dict) -> ScanResult:
    """
    Convenience function to process scraped content with LLM
    """
    llm_service = LLMService()
    return llm_service.generate_structured_output(website_url, scraped_text, extracted_contacts)
