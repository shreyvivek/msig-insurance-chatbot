"""
Block 1: Policy Intelligence
Extract, normalize, and understand insurance policy documents
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import PyPDF2
import pdfplumber
from groq import Groq

logger = logging.getLogger(__name__)

class PolicyIntelligence:
    """Handles policy extraction, normalization, and comparison"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.policy_dir = Path(__file__).parent / "Policy_Wordings"
        self.taxonomy_path = Path(__file__).parent / "Taxonomy" / "Taxonomy_Hackathon.json"
        self.normalized_data = {}
        self.policy_texts = {}
        
        # Try to initialize Ancileo API integration
        self.ancileo_api = None
        try:
            from ancileo_api import AncileoAPI
            self.ancileo_api = AncileoAPI()
            logger.info("Ancileo API integration available")
        except Exception as e:
            logger.warning(f"Ancileo API not available: {e}")
            self.ancileo_api = None
        
        self._load_taxonomy()
        self._extract_policies()
    
    def _load_taxonomy(self):
        """Load the taxonomy structure"""
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                self.taxonomy = json.load(f)
            logger.info("Taxonomy loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            self.taxonomy = {}
    
    def _extract_policies(self):
        """Extract text from all PDF policy documents"""
        if not self.policy_dir.exists():
            logger.warning(f"Policy directory not found: {self.policy_dir}")
            return
        
        for pdf_file in self.policy_dir.glob("*.pdf"):
            try:
                policy_name = pdf_file.stem
                text_content = []
                
                # Try pdfplumber first (better for tables)
                try:
                    with pdfplumber.open(pdf_file) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                text_content.append(text)
                except:
                    # Fallback to PyPDF2
                    with open(pdf_file, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                text_content.append(text)
                
                full_text = "\n\n".join(text_content)
                self.policy_texts[policy_name] = {
                    "id": policy_name,
                    "name": policy_name,
                    "text": full_text,
                    "pages": len(text_content)
                }
                logger.info(f"Extracted {len(full_text)} characters from {policy_name}")
                
            except Exception as e:
                logger.error(f"Failed to extract {pdf_file}: {e}")
        
        # Normalize policies after extraction
        self._normalize_policies()
    
    def _normalize_policies(self):
        """Normalize policy text to taxonomy structure using Groq"""
        logger.info("Normalizing policies to taxonomy...")
        
        # Map policy names - UPDATED to use new policies
        policy_mapping = {
            "INTERNATIONAL TRAVEL": "Product A",
            "MHInsure Travel": "Product B",
            "Scootsurance": "Product C"
        }
        
        # Get taxonomy structure
        taxonomy_prompt = json.dumps(self.taxonomy, indent=2)[:2000]  # First 2000 chars
        
        for policy_name, policy_data in self.policy_texts.items():
            product_name = policy_mapping.get(policy_name, "Product A")
            policy_text = policy_data["text"][:10000]  # Use first 10k chars for normalization
            
            # Use Groq to extract structured data
            extraction_prompt = f"""Extract insurance policy information and normalize it to match this taxonomy structure:

Taxonomy Structure:
{taxonomy_prompt}

Policy Text (excerpt):
{policy_text[:5000]}

Extract and normalize:
1. Age eligibility (min_age, max_age)
2. Medical coverage limits
3. Trip cancellation coverage
4. Baggage protection limits
5. Pre-existing conditions rules
6. Exclusions
7. Deductibles

Return JSON matching the taxonomy structure for {product_name}."""

            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert at extracting and normalizing insurance policy data. Always return valid JSON."},
                        {"role": "user", "content": extraction_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                
                extracted_data = json.loads(response.choices[0].message.content)
                self.normalized_data[policy_name] = {
                    "product_name": product_name,
                    "original_name": policy_name,
                    "extracted_data": extracted_data
                }
                
            except Exception as e:
                logger.error(f"Failed to normalize {policy_name}: {e}")
                # Store basic structure
                self.normalized_data[policy_name] = {
                    "product_name": product_name,
                    "original_name": policy_name,
                    "extracted_data": {}
                }
        
        logger.info("Policy normalization complete")
    
    async def get_policy_list(self, include_ancileo: bool = True) -> List[Dict]:
        """Get list of available policies (local + Ancileo API if available)"""
        policies = list(self.policy_texts.values())
        
        # If Ancileo API is available, fetch additional policies
        if include_ancileo and self.ancileo_api:
            try:
                ancileo_policies = await self.ancileo_api.get_available_policies()
                for ancileo_policy in ancileo_policies:
                    # Convert Ancileo policy format to our format
                    policy_entry = {
                        "id": ancileo_policy.get("product_code", f"ancileo_{ancileo_policy.get('offer_id')}"),
                        "name": ancileo_policy.get("product_name", "Ancileo Policy"),
                        "source": "ancileo",
                        "price": ancileo_policy.get("price"),
                        "currency": ancileo_policy.get("currency", "SGD"),
                        "description": ancileo_policy.get("description", ""),
                        "coverage": ancileo_policy.get("coverage", {}),
                        "raw_data": ancileo_policy
                    }
                    policies.append(policy_entry)
                logger.info(f"Added {len(ancileo_policies)} policies from Ancileo API")
            except Exception as e:
                logger.error(f"Failed to fetch Ancileo policies: {e}")
        
        return policies
    
    def get_policy_text(self, policy_id: str) -> Optional[str]:
        """Get full text of a policy"""
        return self.policy_texts.get(policy_id, {}).get("text")
    
    def get_normalized_data(self) -> Dict:
        """Get normalized policy data"""
        return self.normalized_data
    
    async def compare_policies(self, criteria: str, policies: List[str] = None) -> Dict:
        """Compare policies on specific criteria"""
        if not policies:
            policies = list(self.normalized_data.keys())
        
        # Get relevant policy data
        policy_data = {}
        for policy_name in policies:
            if policy_name in self.normalized_data:
                policy_data[policy_name] = {
                    "normalized": self.normalized_data[policy_name],
                    "text": self.policy_texts.get(policy_name, {}).get("text", "")[:5000]
                }
        
        # Use Groq to compare
        comparison_prompt = f"""Compare these insurance policies on: {criteria}

Available policies:
{json.dumps({k: v['normalized'] for k, v in policy_data.items()}, indent=2)[:3000]}

Create a detailed comparison showing:
1. Differences in {criteria}
2. Which policy offers better coverage
3. Specific limits and conditions
4. Any important caveats

Return a clear, structured comparison."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert insurance advisor. Provide clear, accurate comparisons with specific numbers and details."},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=0.3
            )
            
            comparison_text = response.choices[0].message.content
            
            return {
                "criteria": criteria,
                "policies_compared": policies,
                "comparison": comparison_text,
                "normalized_data": policy_data
            }
        
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {
                "criteria": criteria,
                "error": str(e)
            }
    
    async def explain_coverage(self, topic: str, policy: str = None, scenario: str = None) -> str:
        """Explain coverage with citations"""
        relevant_policies = [policy] if policy else list(self.policy_texts.keys())
        
        explanations = []
        for policy_name in relevant_policies:
            policy_text = self.policy_texts.get(policy_name, {}).get("text", "")
            if not policy_text:
                continue
            
            # Find relevant sections
            explanation_prompt = f"""Explain {topic} from this insurance policy.

Policy: {policy_name}
Topic: {topic}
{"Scenario: " + scenario if scenario else ""}

Policy Text (excerpt):
{policy_text[:8000]}

Provide:
1. Clear explanation of what's covered
2. Specific limits and amounts
3. Any exclusions or conditions
4. Exact quotes from the policy (with page references if available)
5. How this applies to the scenario (if provided)

Format your response with citations in [Policy: {policy_name}, Section: X] format."""

            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert at explaining insurance coverage. Always cite exact policy text."},
                        {"role": "user", "content": explanation_prompt}
                    ],
                    temperature=0.2
                )
                
                explanation = response.choices[0].message.content
                explanations.append(f"**{policy_name}**\n\n{explanation}\n")
                
            except Exception as e:
                logger.error(f"Failed to explain {topic} for {policy_name}: {e}")
                explanations.append(f"**{policy_name}**: Unable to extract information. {str(e)}")
        
        return "\n\n---\n\n".join(explanations)
    
    async def check_eligibility(self, policy: str, age: int = None, 
                               has_pre_existing: bool = None, 
                               trip_duration: int = None) -> str:
        """Check user eligibility for a policy"""
        policy_text = self.policy_texts.get(policy, {}).get("text", "")
        if not policy_text:
            return f"Policy '{policy}' not found."
        
        eligibility_prompt = f"""Check eligibility for this insurance policy.

Policy: {policy}
User Details:
{"Age: " + str(age) if age else ""}
{"Has pre-existing conditions: " + str(has_pre_existing) if has_pre_existing is not None else ""}
{"Trip duration: " + str(trip_duration) + " days" if trip_duration else ""}

Policy Text:
{policy_text[:8000]}

Determine:
1. Is the user eligible? (Yes/No/Partial)
2. Age restrictions
3. Pre-existing condition rules
4. Trip duration limits
5. Any other eligibility requirements

Provide clear, specific answers with policy citations."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at checking insurance eligibility. Be precise and cite policy text."},
                    {"role": "user", "content": eligibility_prompt}
                ],
                temperature=0.1
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Eligibility check failed: {e}")
            return f"Error checking eligibility: {str(e)}"

