"""
Memory distillation service - Extract structured facts from raw text
"""

import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.core.config import get_settings

settings = get_settings()

# Distillation prompt template
DISTILLATION_PROMPT = """You are an AI memory system. Given a conversation turn or user statement, extract structured facts about the user.

Input: "{content}"

Extract all relevant facts, preferences, entities, and experiences. For each fact, determine:
1. Type: preference, fact, entity, intent, experience, relationship
2. Value: The specific information
3. Confidence: 0.0-1.0 based on clarity of the statement
4. Context: Any relevant context (e.g., "Italian" for food preferences)

Output JSON format:
{{
  "facts": [
    {{
      "type": "preference",
      "value": "loves Italian food",
      "confidence": 0.95,
      "context": "cuisine"
    }},
    {{
      "type": "fact",
      "value": "gluten-free diet",
      "confidence": 0.98,
      "context": "dietary restriction"
    }},
    {{
      "type": "experience",
      "value": "got sick from pasta",
      "confidence": 0.9,
      "context": "Italian food, negative"
    }}
  ]
}}

Guidelines:
- Extract multiple facts if present
- Be specific, not vague
- Include negative experiences (what user dislikes)
- Capture entities (people, places, products mentioned)
- Note intents (what user wants to do)
- Handle code-switching (Malay/Indonesian mixed with English)

Respond ONLY with valid JSON."""


class DistillationService:
    """Service for distilling raw text into structured memories"""
    
    def __init__(self, db=None):
        self.db = db
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def distill_memory(
        self,
        content: str,
        context: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Distill raw content into structured memory facts.
        
        Returns list of extracted memory objects with type, value, confidence.
        """
        # Prepare prompt
        prompt = DISTILLATION_PROMPT.format(content=content)
        
        if context:
            prompt += f"\n\nAdditional context: {json.dumps(context)}"
        
        # Call Gemini
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
                response_mime_type="application/json",
            ),
        )
        
        # Parse response
        try:
            result = json.loads(response.text)
            facts = result.get("facts", [])
            
            # Convert to memory format
            memories = []
            for fact in facts:
                memory = {
                    "type": fact.get("type", "fact"),
                    "text": self._format_memory_text(fact),
                    "confidence": fact.get("confidence", 0.8),
                    "context": fact.get("context", ""),
                    "raw_value": fact.get("value", ""),
                    "extracted_at": datetime_now_iso(),
                }
                memories.append(memory)
            
            # If no facts extracted, store the raw content as a single memory
            if not memories:
                memories = [{
                    "type": "fact",
                    "text": content,
                    "confidence": 0.7,
                    "context": "",
                    "raw_value": content,
                    "extracted_at": datetime_now_iso(),
                }]
            
            return memories
            
        except json.JSONDecodeError:
            # Fallback: store raw content
            return [{
                "type": "fact",
                "text": content,
                "confidence": 0.6,
                "context": "",
                "raw_value": content,
                "extracted_at": datetime_now_iso(),
                "extraction_error": "json_parse_failed",
            }]
    
    def _format_memory_text(self, fact: Dict) -> str:
        """Format a fact into natural language memory text"""
        fact_type = fact.get("type", "fact")
        value = fact.get("value", "")
        context = fact.get("context", "")
        
        templates = {
            "preference": f"User prefers: {value}",
            "fact": f"User fact: {value}",
            "entity": f"User mentioned: {value}",
            "intent": f"User wants to: {value}",
            "experience": f"User experienced: {value}",
            "relationship": f"User relationship: {value}",
        }
        
        base = templates.get(fact_type, f"{fact_type}: {value}")
        
        if context:
            base += f" (context: {context})"
        
        return base
    
    async def detect_conflict(
        self,
        memory1: Dict[str, Any],
        memory2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect if two memories conflict and suggest resolution.
        
        Returns conflict analysis with resolution strategy.
        """
        prompt = f"""Compare these two memory statements and determine if they conflict:

Memory 1: "{memory1.get('text', '')}"
Memory 2: "{memory2.get('text', '')}"

Do these conflict? If yes:
1. What is the conflict?
2. Which is more recent/relevant?
3. Resolution strategy: keep_both, replace_old, or merge?

Output JSON:
{{
  "conflicts": true/false,
  "reason": "explanation",
  "resolution": "keep_both/replace_old/merge",
  "confidence": 0.0-1.0
}}"""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=200,
                response_mime_type="application/json",
            ),
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "conflicts": False,
                "reason": "parse_error",
                "resolution": "keep_both",
                "confidence": 0.5,
            }


def datetime_now_iso() -> str:
    """Get current datetime in ISO format"""
    from datetime import datetime
    return datetime.utcnow().isoformat()
