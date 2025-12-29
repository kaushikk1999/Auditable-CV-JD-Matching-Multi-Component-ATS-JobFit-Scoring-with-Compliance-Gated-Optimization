import requests
import json
import re
from typing import Dict, List, Optional
from config.settings import PERPLEXITY_API_KEY, PERPLEXITY_MODEL

class PerplexityRewriter:
    """Handles Perplexity API calls for CV section rewriting."""
    
    def __init__(self, temperature: float = 0.3):
        """
        Args:
            temperature: Lower = more deterministic (0.0-1.0)
        """
        if not PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY not found")
        
        self.api_key = PERPLEXITY_API_KEY
        self.model = PERPLEXITY_MODEL
        self.temperature = temperature
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _call_api(self, prompt: str) -> Optional[str]:
        """Helper to call Perplexity API."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert CV writer and ATS optimization specialist."},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "top_p": 0.9,
            "return_citations": False,
            "return_images": False,
            "return_related_questions": False,
            "search_domain_filter": ["perplexity.ai"],
            "search_recency_filter": "month"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Perplexity API call failed: {e}")
            if response is not None:
                print(f"Response: {response.text}")
            return None

    def rewrite_summary(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Rewrite CV summary using Perplexity."""
        for attempt in range(max_retries):
            response_text = self._call_api(prompt)
            
            if not response_text:
                continue
            
            # Clean response
            rewritten = response_text.strip()
            print(f"DEBUG: Raw Summary Response: {rewritten[:50]}...")
            
            # Remove markdown formatting
            rewritten = re.sub(r'^```.*?\n', '', rewritten, flags=re.MULTILINE)
            rewritten = re.sub(r'\n```$', '', rewritten)
            rewritten = rewritten.strip()
            
            # Validate: 2-3 lines, reasonable length
            lines = [l.strip() for l in rewritten.split('\n') if l.strip()]
            if 2 <= len(lines) <= 3 and len(rewritten) <= 300:
                return rewritten
            
            # If validation fails, we might want to retry or just accept if it's close?
            # For now, strict validation as per Gemini rewriter
            print(f"Summary validation failed (lines={len(lines)}, len={len(rewritten)})")
            
        return None

    def rewrite_bullet(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Rewrite experience bullet using Perplexity."""
        for attempt in range(max_retries):
            response_text = self._call_api(prompt)
            
            if not response_text:
                continue
            
            # Clean response
            rewritten = response_text.strip()
            print(f"DEBUG: Raw Bullet Response: {rewritten[:50]}...")
            rewritten = re.sub(r'^```.*?\n', '', rewritten, flags=re.MULTILINE)
            rewritten = re.sub(r'\n```$', '', rewritten)
            rewritten = rewritten.strip()
            
            # Take first line only
            rewritten = rewritten.split('\n')[0].strip()
            
            # Validate: single line, reasonable length
            if len(rewritten) > 10 and len(rewritten) <= 200:
                return rewritten
                
        return None

    def rewrite_skills(self, prompt: str, max_retries: int = 2) -> Optional[Dict]:
        """Optimize skills section using Perplexity."""
        for attempt in range(max_retries):
            response_text = self._call_api(prompt)
            
            if not response_text:
                continue
            
            try:
                # Clean response
                text = response_text.strip()
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                # Parse JSON
                skills_dict = json.loads(text)
                
                # Unwrap "skills" key if present
                if "skills" in skills_dict and isinstance(skills_dict["skills"], dict):
                    skills_dict = skills_dict["skills"]
                
                # Validate structure
                if isinstance(skills_dict, dict) and len(skills_dict) > 0:
                    return skills_dict
                    
            except json.JSONDecodeError as e:
                print(f"Skills rewrite JSON parse failed: {e}")
                continue
                
        return None

    def rewrite_project(self, prompt: str, max_retries: int = 2) -> Optional[Dict]:
        """Optimize project description using Perplexity."""
        for attempt in range(max_retries):
            response_text = self._call_api(prompt)
            
            if not response_text:
                continue
            
            try:
                # Clean and parse JSON
                text = response_text.strip()
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                project_dict = json.loads(text)
                
                # Validate structure
                required_keys = {"project_name", "description", "technologies", "bullets"}
                if all(k in project_dict for k in required_keys):
                    return project_dict
                    
            except json.JSONDecodeError:
                continue
                
        return None

    def rewrite_certificates(self, prompt: str, max_retries: int = 2) -> Optional[List[Dict]]:
        """Optimize certificates section using Perplexity."""
        for attempt in range(max_retries):
            response_text = self._call_api(prompt)
            
            if not response_text:
                continue
            
            try:
                # Clean and parse JSON
                text = response_text.strip()
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                certs_list = json.loads(text)
                
                # Validate structure
                if isinstance(certs_list, list):
                    if not certs_list or isinstance(certs_list[0], dict):
                        return certs_list
                        
            except json.JSONDecodeError:
                continue
                
        return None
