JD_EXTRACTION_PROMPT = """
You are an expert HR analyst. Extract structured information from the following job description.

Return a JSON object with these exact keys (use "Not specified" if information is missing):

{{
  "job_title": "",
  "company_name": "",
  "location": "",
  "work_type": "",
  "experience_required": "",
  "company_overview": "",
  "role_summary": "",
  "key_responsibilities": [],
  "required_skills": [],
  "preferred_skills": [],
  "education": "",
  "soft_skills": [],
  "diversity_statement": "",
  "recruiter_contact": "",
  "ats_keywords": []
}}

Guidelines:
- key_responsibilities: list of 4-8 main duties
- required_skills: hard technical skills only
- preferred_skills: nice-to-have or bonus skills
- soft_skills: communication, leadership, etc.
- ats_keywords: all critical terms an ATS would scan for (20-30 terms)

Job Description:
{jd_text}

Return ONLY valid JSON, no markdown formatting.
"""

CV_STRUCTURE_EXTRACTION_PROMPT = """
You are an expert CV parser. Extract structured information from the following CV text.

Return a JSON object matching this EXACT schema:

{{
  "contact_info": {{
    "full_name": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "github": "",
    "portfolio": "",
    "location": ""
  }},
  "summary": {{
    "text": ""
  }},
  "skills": [
    {{
      "category_name": "Programming Languages",
      "skills": ["Python", "JavaScript"]
    }}
  ],
  "experience": [
    {{
      "job_title": "",
      "company_name": "",
      "location": "",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "bullets": [
        {{"text": "Achievement description with metrics"}}
      ]
    }}
  ],
  "projects": [
    {{
      "project_name": "",
      "description": "",
      "technologies": ["Tech1", "Tech2"],
      "start_date": "",
      "end_date": "",
      "bullets": [
        {{"text": "Project achievement"}}
      ]
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "location": "",
      "graduation_date": "",
      "gpa": "",
      "relevant_coursework": []
    }}
  ],
  "certifications": [
    {{
      "name": "",
      "issuer": "",
      "date_obtained": "",
      "credential_id": ""
    }}
  ]
}}

CRITICAL RULES:
1. Extract ALL bullet points from experience and projects exactly as written
2. Preserve metrics and numbers exactly
3. Categorize skills into logical groups (e.g., "Programming Languages", "Frameworks", "Tools", "Cloud Platforms")
4. If a section is missing, return empty list [] or null
5. Use "Present" for current positions
6. Format dates consistently as "Mon YYYY" (e.g., "Jan 2020")
7. Do NOT add, modify, or enhance any content - extract only

CV Text:
{cv_text}

Return ONLY valid JSON, no markdown formatting.
"""

JD_KEYWORD_TAXONOMY_PROMPT = """
You are an expert ATS keyword analyst. Analyze the following job description and extract a detailed keyword taxonomy.

Return a JSON object matching this schema:

{{
  "keyword_taxonomy": {{
    "technical_skills": ["Python", "Machine Learning", "SQL"],
    "tools_technologies": ["AWS", "Docker", "Kubernetes"],
    "soft_skills": ["Communication", "Leadership"],
    "domain_knowledge": ["Healthcare", "Finance", "E-commerce"],
    "certifications": ["AWS Certified", "PMP"]
  }},
  "must_have_requirements": [
    {{
      "text": "5+ years of Python experience",
      "is_required": true,
      "keywords": ["Python", "5 years"]
    }}
  ],
  "nice_to_have_requirements": [
    {{
      "text": "Familiarity with Agile methodology",
      "is_required": false,
      "keywords": ["Agile"]
    }}
  ]
}}

EXTRACTION RULES:
1. Identify requirements with phrases like "must have", "required", "essential" as must_have_requirements
2. Identify requirements with "preferred", "nice to have", "bonus", "plus" as nice_to_have_requirements
3. Extract distinct keyword categories:
   - technical_skills: programming languages, frameworks, methodologies
   - tools_technologies: software, platforms, services
   - soft_skills: interpersonal abilities (communication, leadership, etc.)
   - domain_knowledge: industry-specific expertise
   - certifications: required or preferred certifications
4. Each requirement should list its component keywords
5. Avoid duplicates across categories

Job Description:
{jd_text}

Return ONLY valid JSON, no markdown.
"""
