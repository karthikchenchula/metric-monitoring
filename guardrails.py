# guardrails.py
from metrics import GUARDRAIL_REJECTIONS

class GuardrailSystem:
    def __init__(self):
        self.prohibited_keywords = ['hack', 'exploit', 'malware']
        self.max_prompt_length = 10000
    
    def check_input(self, text: str, model_name: str = "default"):
        # Check empty input
        if not text or not text.strip():
            GUARDRAIL_REJECTIONS.labels(
                guardrail_type='empty_input',
                model_name=model_name
            ).inc()
            return False
        
        # Check length limit
        if len(text) > self.max_prompt_length:
            GUARDRAIL_REJECTIONS.labels(
                guardrail_type='length_exceeded',
                model_name=model_name
            ).inc()
            return False
        
        # Check prohibited content
        text_lower = text.lower()
        for keyword in self.prohibited_keywords:
            if keyword in text_lower:
                GUARDRAIL_REJECTIONS.labels(
                    guardrail_type='prohibited_content',
                    model_name=model_name
                ).inc()
                return False
        
        return True
