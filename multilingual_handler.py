"""
Enhanced Multilingual Handler
Deep language support with cultural understanding
"""

import os
import logging
from typing import Dict, List, Optional
from groq import Groq

logger = logging.getLogger(__name__)

class MultilingualHandler:
    """Handles multilingual conversations with cultural awareness"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        
        self.supported_languages = {
            "en": {"name": "English", "emoji": "🇬🇧", "native_name": "English"},
            "ta": {"name": "Tamil", "emoji": "🇮🇳", "native_name": "தமிழ்"},  # Added Tamil
            "zh": {"name": "Chinese", "emoji": "🇨🇳", "native_name": "中文"},
            "ms": {"name": "Malay", "emoji": "🇲🇾", "native_name": "Bahasa Melayu"},  # Added Malay
            "ja": {"name": "Japanese", "emoji": "🇯🇵", "native_name": "日本語"},
            "ko": {"name": "Korean", "emoji": "🇰🇷", "native_name": "한국어"},
            "es": {"name": "Spanish", "emoji": "🇪🇸", "native_name": "Español"},
            "fr": {"name": "French", "emoji": "🇫🇷", "native_name": "Français"},
            "de": {"name": "German", "emoji": "🇩🇪", "native_name": "Deutsch"},
            "it": {"name": "Italian", "emoji": "🇮🇹", "native_name": "Italiano"},
            "pt": {"name": "Portuguese", "emoji": "🇵🇹", "native_name": "Português"},
            "th": {"name": "Thai", "emoji": "🇹🇭", "native_name": "ไทย"},
            "vi": {"name": "Vietnamese", "emoji": "🇻🇳", "native_name": "Tiếng Việt"},
            "id": {"name": "Indonesian", "emoji": "🇮🇩", "native_name": "Bahasa Indonesia"},
            "hi": {"name": "Hindi", "emoji": "🇮🇳", "native_name": "हिन्दी"},
            "ar": {"name": "Arabic", "emoji": "🇸🇦", "native_name": "العربية"},
            "ru": {"name": "Russian", "emoji": "🇷🇺", "native_name": "Русский"}
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language from text"""
        # Simple detection based on character patterns
        for lang_code, lang_info in self.supported_languages.items():
            if lang_code == "ja" and any(char in text for char in "あいうえお"):
                return lang_code
            elif lang_code == "zh" and any(char in text for char in "你好"):
                return lang_code
            elif lang_code == "ko" and any(char in text for char in "안녕"):
                return lang_code
            elif lang_code == "ar" and any(char in text for char in "مرحبا"):
                return lang_code
            elif lang_code == "ru" and any(char in text for char in "Привет"):
                return lang_code
        
        # Default to English
        return "en"
    
    async def translate(self, text: str, target_language: str, 
                       source_language: str = None, context: str = None) -> Dict:
        """Translate text with cultural context awareness"""
        
        if not source_language:
            source_language = self.detect_language(text)
        
        if source_language == target_language:
            return {
                "success": True,
                "original": text,
                "translated": text,
                "language": target_language
            }
        
        prompt = f"""Translate from {self.supported_languages.get(source_language, {}).get('name', source_language)} to {self.supported_languages.get(target_language, {}).get('name', target_language)}:

{text}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Translate the text exactly, keeping all formatting unchanged. Return only the translation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            translated = response.choices[0].message.content.strip()
            
            # Clean up any extra explanations the LLM added
            lines = translated.split('\n')
            cleaned_lines = []
            for line in lines:
                # Stop if we hit any explanatory text
                stripped = line.strip()
                if any(stripped.startswith(x) for x in [
                    '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 
                    'CRITICAL', 'முக்கிய', 'IMPORTANT', 'குறிப்பு', 'Note:', 'குறிப்பு:', 
                    'விதிகள்:', 'Rules:', '❌', '✅', 'Translation:', 'மொழிபெயர்ப்பு:'
                ]):
                    break
                cleaned_lines.append(line)
            translated = '\n'.join(cleaned_lines).strip()
            
            return {
                "success": True,
                "original": text,
                "translated": translated,
                "source_language": source_language,
                "target_language": target_language
            }
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "original": text,
                "error": str(e)
            }
    
    async def respond_in_language(self, response_text: str, user_language: str) -> str:
        """Ensure response is in user's preferred language"""
        
        detected = self.detect_language(response_text)
        
        if detected == user_language:
            return response_text
        
        # Translate if needed
        translation = await self.translate(
            response_text,
            target_language=user_language,
            source_language=detected,
            context="Travel insurance conversation"
        )
        
        if translation.get("success"):
            return translation["translated"]
        
        return response_text
    
    def get_cultural_context(self, language: str) -> Dict:
        """Get cultural context for language"""
        cultural_tips = {
            "ja": {
                "greeting": "こんにちは",
                "formality": "Use polite forms (です/ます) in business contexts",
                "communication_style": "Indirect, respectful"
            },
            "zh": {
                "greeting": "你好",
                "formality": "Use formal titles when appropriate",
                "communication_style": "Direct but polite"
            },
            "ko": {
                "greeting": "안녕하세요",
                "formality": "Honorific forms are important",
                "communication_style": "Respectful, hierarchical"
            },
            "es": {
                "greeting": "Hola",
                "formality": "Tú vs Usted depending on relationship",
                "communication_style": "Warm, expressive"
            },
            "fr": {
                "greeting": "Bonjour",
                "formality": "Vous for formal, tu for informal",
                "communication_style": "Polite, structured"
            }
        }
        
        return cultural_tips.get(language, {})
    
    def format_currency(self, amount: float, language: str) -> str:
        """Format currency based on language/locale"""
        currency_map = {
            "ja": ("JPY", "¥"),
            "zh": ("CNY", "¥"),
            "ko": ("KRW", "₩"),
            "th": ("THB", "฿"),
            "vi": ("VND", "₫"),
            "id": ("IDR", "Rp"),
            "en": ("USD", "$"),
            "es": ("EUR", "€"),
            "fr": ("EUR", "€"),
            "de": ("EUR", "€")
        }
        
        currency, symbol = currency_map.get(language, ("USD", "$"))
        
        if currency == "JPY" or currency == "KRW" or currency == "VND":
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.2f}"

