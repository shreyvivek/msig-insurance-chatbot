"""
Policy Simplifier - Makes insurance jargon accessible to regular users
Translates complex terms into simple, understandable language
"""

import os
import logging
from typing import Dict, List, Optional, Any
from groq import Groq

logger = logging.getLogger(__name__)

class PolicySimplifier:
    """Simplifies insurance policy wordings for non-expert users"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        
        # Common insurance jargon mapping
        self.jargon_map = {
            "deductible": "The amount you pay before insurance kicks in",
            "premium": "The price you pay for insurance",
            "coverage": "What the insurance pays for",
            "exclusion": "What the insurance does NOT cover",
            "claim": "When you ask insurance to pay for something",
            "beneficiary": "Person who gets paid if something happens",
            "underwriter": "The insurance company",
            "policyholder": "You - the person who bought the insurance",
            "sum insured": "Maximum amount insurance will pay",
            "pre-existing condition": "Health issue you had before buying insurance"
        }
    
    def simplify_term(self, term: str) -> str:
        """Simplify a single insurance term"""
        return self.jargon_map.get(term.lower(), term)
    
    async def simplify_policy_section(
        self,
        policy_text: str,
        section_name: str = None
    ) -> Dict:
        """
        Simplify a section of policy text for non-expert users
        Removes jargon, explains complex concepts, makes it accessible
        """
        
        simplification_prompt = f"""Simplify this insurance policy text to make it easy for someone with NO insurance knowledge to understand.

Original Text:
{policy_text[:4000]}

Instructions:
1. Replace ALL insurance jargon with simple, everyday words
2. Use short sentences (max 15 words)
3. Use bullet points for lists
4. Add simple examples where helpful
5. Explain what things MEAN in practical terms
6. Keep the important information but make it friendly
7. Remove legal boilerplate unless it's critical
8. Use "you" instead of "the insured" or "policyholder"
9. Explain numbers clearly (e.g., "$50,000 = fifty thousand dollars")

Focus on:
- What IS covered
- What is NOT covered (clearly!)
- How much money you can get
- When you can claim
- Any important limits or restrictions

Return the simplified text that a regular person can actually understand."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at explaining complex insurance terms in simple, friendly language. Make everything accessible to people with no insurance knowledge."
                    },
                    {"role": "user", "content": simplification_prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            simplified = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "original_length": len(policy_text),
                "simplified_length": len(simplified),
                "simplified_text": simplified,
                "section": section_name or "General"
            }
        
        except Exception as e:
            logger.error(f"Policy simplification failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "simplified_text": policy_text  # Return original on error
            }
    
    async def explain_coverage_in_plain_english(
        self,
        coverage_type: str,
        policy_name: str,
        policy_text: str = None
    ) -> str:
        """
        Explain a specific type of coverage in plain English
        e.g., "Medical Expenses", "Trip Cancellation", etc.
        """
        
        if not policy_text:
            try:
                from policy_intelligence import PolicyIntelligence
                policy_intel = PolicyIntelligence()
                policy_text = policy_intel.get_policy_text(policy_name) or ""
            except:
                policy_text = ""
        
        explain_prompt = f"""Explain what "{coverage_type}" means in this travel insurance policy.

Policy: {policy_name}
Policy Text (excerpt):
{policy_text[:3000]}

Explain in simple, friendly language:
1. What is {coverage_type}?
2. When does it pay out?
3. How much money can you get?
4. Give a real-world example
5. Any important things to watch out for?

Make it so a regular person (not an insurance expert) can understand it completely."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You explain insurance in simple, friendly terms. Use examples and avoid jargon."
                    },
                    {"role": "user", "content": explain_prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Coverage explanation failed: {e}")
            return f"{coverage_type} is a type of coverage in your travel insurance policy. Please check the policy document for specific details."

