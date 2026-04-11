import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLMGenerator:
    def __init__(self):
        print("🧠 Loading Groq (Llama 3) Engine with Memory...")
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
        else:
            self.client = None
            print("⚠️ WARNING: GROQ_API_KEY not found.")

    def generate_response(self, query: str, context_list: list, history: list = None) -> str:
        if not self.client:
            return "Here is what I found:\n- " + "\n- ".join(context_list)

        # 1. Format the Database Facts
        context_str = "\n".join([f"- {c}" for c in context_list])
        
        # 2. Format the Conversation History (Memory)
        history_str = ""
        if history:
            history_str = "PREVIOUS CONVERSATION HISTORY:\n"
            for chat in history:
                history_str += f"Student: {chat['user']}\nAssistant: {chat['assistant']}\n"
            history_str += "\n"

        # 3. The New System Prompt (Now with Memory!)
        system_prompt = f"""
        You are an expert Academic Assistant for SRM Institute of Science and Technology.
        
        {history_str}
        
        OFFICIAL UNIVERSITY DOCUMENTS RECOVERED:
        =========================================
        {context_str}
        =========================================
        
        CRITICAL INSTRUCTIONS:
        1. You must answer the student's question using ONLY the facts provided in the "OFFICIAL UNIVERSITY DOCUMENTS" section above.
        2. Do NOT use outside knowledge. Do NOT guess. 
        3. If the answer is not contained exactly within the documents above, you must say: "I apologize, but I cannot find that specific information in the uploaded university documents."
        4. Be polite, concise, and format your answer clearly.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while thinking: {str(e)}"

llm_engine = LLMGenerator()