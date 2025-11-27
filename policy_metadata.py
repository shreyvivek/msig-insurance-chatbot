"""
Policy Metadata Extractor
Extracts structured cancellation and refund information from policy documents
"""

import logging
from typing import Dict, Optional, Any
from groq import Groq
import os

logger = logging.getLogger(__name__)

class PolicyMetadata:
    """Extracts and structures policy metadata, especially cancellation info"""
    
    def __init__(self, policy_intel):
        self.policy_intel = policy_intel
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self._cancellation_cache = {}  # Cache extracted cancellation data
    
    def get_active_policy(self, context_data: Dict, user_id: str = None) -> Optional[Dict]:
        """
        Determine the user's active policy from context
        
        Priority:
        1. Most recent quote in context_data
        2. Policy mentioned in question
        3. User's purchase history (if available)
        
        Returns:
            {
                "policy_id": str,
                "product_name": str,
                "insurer_name": str,  # Extracted from policy text
                "cancellation": {...}  # Structured cancellation data
            }
        """
        # Check for quotes in context
        quotes = context_data.get("quotes", [])
        if quotes and len(quotes) > 0:
            # Use the first/most recent quote
            active_quote = quotes[0]
            plan_name = active_quote.get("plan_name", "")
            if plan_name:
                return self._build_policy_metadata(plan_name)
        
        # Check for policy_id in context
        policy_id = context_data.get("policy_id") or context_data.get("selected_policy_id")
        if policy_id:
            return self._build_policy_metadata(policy_id)
        
        # Check for policy_name in trip_details
        trip_details = context_data.get("trip_details", {})
        policy_name = trip_details.get("policy_name")
        if policy_name:
            return self._build_policy_metadata(policy_name)
        
        return None
    
    def _build_policy_metadata(self, policy_name: str) -> Dict:
        """Build policy metadata structure from policy name"""
        # Normalize policy name
        normalized = self._normalize_policy_name(policy_name)
        
        # Get cancellation data (cached if available)
        if normalized in self._cancellation_cache:
            cancellation_data = self._cancellation_cache[normalized]
        else:
            cancellation_data = self._extract_cancellation_data(normalized)
            if cancellation_data:
                self._cancellation_cache[normalized] = cancellation_data
        
        # Extract insurer name from policy text
        insurer_name = self._extract_insurer_name(normalized)
        
        return {
            "policy_id": normalized,
            "product_name": normalized,
            "insurer_name": insurer_name,
            "cancellation": cancellation_data or {}
        }
    
    def _normalize_policy_name(self, name: str) -> str:
        """Normalize policy name to standard format"""
        name_lower = name.lower()
        
        if "scootsurance" in name_lower or "scoot" in name_lower:
            return "Scootsurance"
        elif "international travel" in name_lower or "international" in name_lower:
            return "INTERNATIONAL TRAVEL"
        elif "mhinsure" in name_lower or "mh insure" in name_lower:
            return "MHInsure Travel"
        else:
            # Return as-is, will be used to look up policy text
            return name
    
    def _extract_insurer_name(self, policy_name: str) -> str:
        """Extract insurer name from policy text"""
        policy_text = self.policy_intel.get_policy_text(policy_name)
        if not policy_text:
            return "Unknown"
        
        # Try to extract insurer name from first few paragraphs
        first_500 = policy_text[:500].lower()
        
        # Common patterns
        if "msig" in first_500:
            return "MSIG"
        elif "mh insurance" in first_500 or "mhinsure" in first_500:
            return "MH Insurance"
        elif "scoot" in first_500:
            return "Scoot"
        else:
            # Default based on policy name
            if "scootsurance" in policy_name.lower():
                return "Scoot"
            elif "mhinsure" in policy_name.lower():
                return "MH Insurance"
            else:
                return "MSIG"
    
    def _extract_cancellation_data(self, policy_name: str) -> Optional[Dict]:
        """Extract structured cancellation data from policy document"""
        policy_text = self.policy_intel.get_policy_text(policy_name)
        if not policy_text:
            logger.warning(f"No policy text found for {policy_name}")
            return None
        
        # Use LLM to extract structured cancellation data
        try:
            extraction_prompt = f"""Extract cancellation and refund information from this insurance policy document.

Policy Name: {policy_name}

Policy Text (excerpt):
{policy_text[:8000]}

Extract the following information and return as JSON:
{{
  "contact_methods": {{
    "phone": "phone number if mentioned, or null",
    "email": "email address if mentioned, or null",
    "portal_url": "online portal URL if mentioned, or null",
    "office_hours": "business hours if mentioned, or null"
  }},
  "required_information": ["list of required info like policy number, name, etc."],
  "cooling_off_days": number of days for cooling-off period, or null,
  "refund_rules": {{
    "full_refund_conditions": ["conditions for full refund"],
    "partial_refund_conditions": ["conditions for partial refund"],
    "no_refund_conditions": ["conditions where no refund is allowed"]
  }},
  "processing_time": {{
    "cancel_processing": "time to process cancellation (e.g., '5-7 business days')",
    "refund_credit": "time to credit refund (e.g., '10-14 business days')"
  }},
  "cancellation_fees": "information about fees, or null",
  "notes": "any other important notes about cancellation"
}}

IMPORTANT:
- Only extract information that is EXPLICITLY stated in the policy text
- If information is not found, use null or empty arrays
- Do not make up or assume information
- Return valid JSON only"""

            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from insurance policy documents. Always return valid JSON. Only extract information that is explicitly stated."},
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            import json
            extracted = json.loads(response.choices[0].message.content)
            
            logger.info(f"Extracted cancellation data for {policy_name}: {len(str(extracted))} chars")
            return extracted
            
        except Exception as e:
            logger.error(f"Failed to extract cancellation data for {policy_name}: {e}", exc_info=True)
            return None
    
    def format_cancellation_answer(self, policy_metadata: Dict, question: str) -> str:
        """
        Format a concise cancellation answer based on the question type
        
        Args:
            policy_metadata: Policy metadata from get_active_policy
            question: User's question
        
        Returns:
            Formatted answer string
        """
        question_lower = question.lower()
        cancellation = policy_metadata.get("cancellation", {})
        product_name = policy_metadata.get("product_name", "this policy")
        insurer_name = policy_metadata.get("insurer_name", "the insurer")
        
        # Specific follow-up questions
        if "cooling-off" in question_lower or "cooling off" in question_lower:
            cooling_days = cancellation.get("cooling_off_days")
            if cooling_days:
                refund_rules = cancellation.get("refund_rules", {})
                full_refund = refund_rules.get("full_refund_conditions", [])
                return f"""**Cooling-Off Period for {product_name}**

The cooling-off period is **{cooling_days} days** from the date of purchase.

During this period:
- You can cancel for a **full refund** if no claims have been made and your trip has not started
- After {cooling_days} days, different refund rules may apply

For specific conditions, please refer to your policy document or contact {insurer_name} customer service."""
            else:
                return f"""**Cooling-Off Period**

The cooling-off period for {product_name} is not explicitly specified in the available policy information.

Please refer to your policy document or contact {insurer_name} customer service for details about the cooling-off period and refund eligibility."""
        
        elif "how long" in question_lower and "refund" in question_lower:
            processing = cancellation.get("processing_time", {})
            cancel_time = processing.get("cancel_processing")
            refund_time = processing.get("refund_credit")
            
            if cancel_time or refund_time:
                answer = f"""**Refund Processing Time for {product_name}**\n\n"""
                if cancel_time:
                    answer += f"• **Cancellation processing**: {cancel_time}\n"
                if refund_time:
                    answer += f"• **Refund crediting**: {refund_time}\n"
                return answer
            else:
                return f"""**Refund Processing Time**

The exact refund processing time for {product_name} is not specified in the available policy information.

Please contact {insurer_name} customer service for specific timing details."""
        
        elif "trip has started" in question_lower or "trip started" in question_lower or "already started" in question_lower:
            refund_rules = cancellation.get("refund_rules", {})
            no_refund = refund_rules.get("no_refund_conditions", [])
            
            if no_refund:
                conditions = ", ".join(no_refund) if isinstance(no_refund, list) else str(no_refund)
                return f"""**Cancellation After Trip Starts**

For {product_name}, cancellation and refund are generally **not possible** once:
{conditions}

If your trip has already started, please contact {insurer_name} customer service to discuss your specific situation, as there may be exceptions in certain circumstances."""
            else:
                return f"""**Cancellation After Trip Starts**

For {product_name}, cancellation and refund policies after the trip has started are not explicitly detailed in the available information.

Please contact {insurer_name} customer service to discuss your specific situation."""
        
        # General cancellation question
        else:
            return self._format_full_cancellation_answer(policy_metadata)
    
    def _format_full_cancellation_answer(self, policy_metadata: Dict) -> str:
        """Format a complete cancellation answer"""
        cancellation = policy_metadata.get("cancellation", {})
        product_name = policy_metadata.get("product_name", "this policy")
        insurer_name = policy_metadata.get("insurer_name", "the insurer")
        
        answer_parts = [f"**How to Cancel Your {product_name} Policy**\n"]
        
        # Contact methods
        contact = cancellation.get("contact_methods", {})
        if contact.get("phone") or contact.get("email") or contact.get("portal_url"):
            answer_parts.append("**📞 Contact Methods:**")
            if contact.get("phone"):
                hours = f" ({contact['office_hours']})" if contact.get("office_hours") else ""
                answer_parts.append(f"1. **Phone**: {contact['phone']}{hours}")
            if contact.get("email"):
                answer_parts.append(f"2. **Email**: {contact['email']}")
            if contact.get("portal_url"):
                answer_parts.append(f"3. **Online**: {contact['portal_url']}")
            answer_parts.append("")
        
        # Required information
        required_info = cancellation.get("required_information", [])
        if required_info:
            answer_parts.append("**📋 Required Information:**")
            for info in required_info:
                answer_parts.append(f"- {info}")
            answer_parts.append("")
        
        # Refund policy
        refund_rules = cancellation.get("refund_rules", {})
        cooling_days = cancellation.get("cooling_off_days")
        
        if refund_rules or cooling_days:
            answer_parts.append("**💰 Refund Policy:**")
            if cooling_days:
                answer_parts.append(f"- **Full refund**: If cancelled within {cooling_days} days of purchase (cooling-off period)")
            if refund_rules.get("partial_refund_conditions"):
                answer_parts.append(f"- **Partial refund**: {', '.join(refund_rules['partial_refund_conditions'])}")
            if refund_rules.get("no_refund_conditions"):
                answer_parts.append(f"- **No refund**: {', '.join(refund_rules['no_refund_conditions'])}")
            answer_parts.append("")
        
        # Processing time
        processing = cancellation.get("processing_time", {})
        if processing.get("cancel_processing") or processing.get("refund_credit"):
            answer_parts.append("**⏰ Processing Time:**")
            if processing.get("cancel_processing"):
                answer_parts.append(f"- Cancellation processing: {processing['cancel_processing']}")
            if processing.get("refund_credit"):
                answer_parts.append(f"- Refund crediting: {processing['refund_credit']}")
            answer_parts.append("")
        
        # Notes
        notes = cancellation.get("notes")
        if notes:
            answer_parts.append(f"**⚠️ Important Notes:**\n{notes}")
        
        return "\n".join(answer_parts)

