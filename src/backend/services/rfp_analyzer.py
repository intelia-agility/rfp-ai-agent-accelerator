from .llm_client import LLMClient

class RFPAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_rfp(self, rfp_text: str):
        prompt = f"""
        Analyze the following RFP document text and provide a evaluation in JSON format.
        
        RFP TEXT:
        {rfp_text[:10000]}
        
        EVALUATE AGAINST:
        1. Business strategy and alignment.
        2. Core offerings fit.
        3. Resource availability.
        4. Risk and compliance.
        
        RETURN JSON ONLY:
        {{
            "score": (integer 0-100),
            "recommendation": "Pursue" or "No-Pursue",
            "criteria_scores": {{
                "strategy": (0-100),
                "offerings": (0-100),
                "resources": (0-100),
                "risks": (0-100)
            }},
            "reasoning": "Brief explanation of the score"
        }}
        """
        try:
            import json
            import re
            import logging
            logger = logging.getLogger(__name__)
            
            response = self.llm.generate_content(prompt)
            logger.info(f"LLM Response received: {response[:200]}...")
            
            # More robust JSON extraction - look for JSON block first
            json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL | re.IGNORECASE)
            if json_block_match:
                json_str = json_block_match.group(1)
            else:
                # Fallback to searching for any curly brace block
                json_match = re.search(r'(\{.*?\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    logger.error(f"No JSON found in LLM response: {response}")
                    return {"error": f"AI did not return a valid JSON format. Response started with: {response[:100]}"}

            try:
                data = json.loads(json_str)
                # Basic validation of required fields
                if "score" in data and "recommendation" in data:
                    return data
                else:
                    logger.error(f"JSON missing required fields: {data}")
                    return {"error": "AI response missing 'score' or 'recommendation'"}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}. Raw JSON str: {json_str}")
                return {"error": f"Failed to parse AI response as JSON: {str(e)}"}
                
        except Exception as e:
            logger.error(f"Analysis failed with exception: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
