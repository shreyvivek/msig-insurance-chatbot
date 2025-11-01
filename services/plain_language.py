"""
Plain language service for policy simplification
"""
import logging
from typing import Dict, Optional
from groq import Groq
import os

logger = logging.getLogger(__name__)

class PlainLanguageService:
    """Generates human-friendly policy explanations"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
    
    async def simplify_policy_clause(self, clause_text: str, benefit_type: str = "general", 
                                     target_language: str = "en") -> Dict:
        """
        Simplify a policy clause into plain language
        
        Args:
            clause_text: Original policy clause text
            benefit_type: Type of benefit (medical, cancellation, baggage, etc.)
            target_language: Language code (en, ta, zh, ms)
            
        Returns:
            {
                "simplified": str,
                "key_points": List[str],
                "exclusions": List[str],
                "action_steps": List[str],
                "original": str
            }
        """
        if not self.client:
            return self._simple_simplification(clause_text, benefit_type)
        
        try:
            prompt = f"""Simplify this travel insurance policy clause into plain, friendly language for a general traveler.

Original clause:
{clause_text[:500]}

Benefit type: {benefit_type}

Provide:
1. A simplified explanation (2-3 sentences, max 40 words total)
2. Key points (3-4 bullet points)
3. Important exclusions (if any)
4. What the traveler should do (1-2 action steps)

Format as JSON:
{{
    "simplified": "short explanation",
    "key_points": ["point1", "point2"],
    "exclusions": ["exclusion1", "exclusion2"],
    "action_steps": ["step1", "step2"]
}}"""
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            result["original"] = clause_text
            return result
            
        except Exception as e:
            logger.error(f"Error simplifying clause: {e}")
            return self._simple_simplification(clause_text, benefit_type)
    
    def _simple_simplification(self, clause_text: str, benefit_type: str) -> Dict:
        """Fallback simple simplification without LLM"""
        # Extract key numbers and terms
        import re
        amounts = re.findall(r'\$?([\d,]+)', clause_text)
        
        simplified = f"This coverage protects you for {benefit_type}. "
        if amounts:
            simplified += f"Coverage amount: ${amounts[0]}"
        
        return {
            "simplified": simplified,
            "key_points": [
                "Coverage applies during your trip",
                "Claims must be filed within specified time",
                "Keep all receipts and documentation"
            ],
            "exclusions": [],
            "action_steps": [
                "Read full policy document",
                "Contact insurer for clarification if needed"
            ],
            "original": clause_text
        }
    
    async def simplify_policy_section(self, policy_name: str, section_name: str, 
                                     section_content: Dict, target_language: str = "en") -> Dict:
        """
        Simplify an entire policy section
        
        Args:
            policy_name: Name of the policy
            section_name: Name of section (e.g., "Medical Coverage")
            section_content: Policy section data
            target_language: Language code
            
        Returns:
            Simplified section with explanations
        """
        simplified_sections = {}
        
        # Simplify each benefit in the section
        for key, value in section_content.items():
            if isinstance(value, (int, float)):
                # Numeric coverage amount
                simplified_sections[key] = {
                    "value": value,
                    "explanation": f"Coverage up to ${value:,.0f} for {key.replace('_', ' ').title()}"
                }
            elif isinstance(value, dict):
                # Complex benefit structure
                clause_text = str(value)
                simplified = await self.simplify_policy_clause(clause_text, key, target_language)
                simplified_sections[key] = simplified
        
        return {
            "policy": policy_name,
            "section": section_name,
            "simplified": simplified_sections,
            "language": target_language
        }

