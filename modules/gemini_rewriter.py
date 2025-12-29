import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from typing import Dict, List, Optional
import json
import re

class GeminiRewriter:
    """Handles Gemini API calls for CV section rewriting."""
    
    def __init__(self, temperature: float = 0.3):
        """
        Args:
            temperature: Lower = more deterministic (0.0-1.0)
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Configure generation parameters for consistency
        self.generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Safety settings (allow all content for CV rewriting to avoid false positives)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def rewrite_summary(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """
        Rewrite CV summary using Gemini.
        
        Returns:
            Rewritten summary text or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    continue
                
                # Clean response
                rewritten = response.text.strip()
                print(f"DEBUG: Raw Summary Response: {rewritten[:50]}...")
                
                # Remove markdown formatting if present
                rewritten = re.sub(r'^```.*?\n', '', rewritten, flags=re.MULTILINE)
                rewritten = re.sub(r'\n```$', '', rewritten)
                rewritten = rewritten.strip()
                
                # Validate: 2-3 lines, reasonable length
                lines = [l.strip() for l in rewritten.split('\n') if l.strip()]
                if 2 <= len(lines) <= 3 and len(rewritten) <= 300:
                    return rewritten
                
            except Exception as e:
                print(f"Summary rewrite attempt {attempt + 1} failed: {e}")
                continue
        
        print("DEBUG: Summary rewrite failed after retries")
        return None
    
    def rewrite_bullet(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """
        Rewrite experience bullet using Gemini.
        
        Returns:
            Rewritten bullet or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    continue
                
                # Clean response
                rewritten = response.text.strip()
                print(f"DEBUG: Raw Bullet Response: {rewritten[:50]}...")
                rewritten = re.sub(r'^```.*?\n', '', rewritten, flags=re.MULTILINE)
                rewritten = re.sub(r'\n```$', '', rewritten)
                rewritten = rewritten.strip()
                
                # Take first line only
                rewritten = rewritten.split('\n')[0].strip()
                
                # Validate: single line, reasonable length
                if len(rewritten) > 10 and len(rewritten) <= 200:
                    return rewritten
                
            except Exception as e:
                print(f"Bullet rewrite attempt {attempt + 1} failed: {e}")
                continue
        
        print("DEBUG: Bullet rewrite failed after retries")
        return None
    
    def rewrite_skills(self, prompt: str, max_retries: int = 2) -> Optional[Dict]:
        """
        Optimize skills section using Gemini.
        
        Returns:
            Dictionary of categorized skills or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    continue
                
                # Clean response
                text = response.text.strip()
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                # Parse JSON
                skills_dict = json.loads(text)
                
                # Unwrap "skills" key if present (Gemini often wraps it)
                if "skills" in skills_dict and isinstance(skills_dict["skills"], dict):
                    skills_dict = skills_dict["skills"]
                
                # Validate structure
                if isinstance(skills_dict, dict) and len(skills_dict) > 0:
                    return skills_dict
                
            except json.JSONDecodeError as e:
                print(f"Skills rewrite JSON parse failed (attempt {attempt + 1}): {e}")
                continue
            except Exception as e:
                print(f"Skills rewrite attempt {attempt + 1} failed: {e}")
                continue
        
        return None
    
    def rewrite_project(self, prompt: str, max_retries: int = 2) -> Optional[Dict]:
        """
        Optimize project description using Gemini.
        
        Returns:
            Project dictionary or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    continue
                
                # Clean and parse JSON
                text = response.text.strip()
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
            except Exception as e:
                print(f"Project rewrite attempt {attempt + 1} failed: {e}")
                continue
        
        return None

    def rewrite_certificates(self, prompt: str, max_retries: int = 2) -> Optional[List[Dict]]:
        """
        Optimize certificates section using Gemini.
        
        Returns:
            List of certificate dictionaries or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    continue
                
                # Clean and parse JSON
                text = response.text.strip()
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                certs_list = json.loads(text)
                
                # Validate structure
                if isinstance(certs_list, list):
                    # Basic check for first item if exists
                    if not certs_list or isinstance(certs_list[0], dict):
                        return certs_list
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Certificate rewrite attempt {attempt + 1} failed: {e}")
                continue
        
        return None
