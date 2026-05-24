import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AutoFixAgent:
    def __init__(self):
        self.name = "AutoFixer AI"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ [Agent] Warning: GEMINI_API_KEY not found in .env. Running in mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')

    def analyze_error(self, error_log):
        print(f"🧠 [Agent] Analyzing stack trace...")
        if self.mock_mode:
            # Fallback mock logic
            file_match = re.search(r'File "(.*?)", line (\d+)', error_log)
            if file_match:
                return {"file": file_match.group(1), "line": file_match.group(2), "error": "MockError", "message": "Mock issue"}
            return None

        prompt = f"""
        Analyze this error log and return ONLY a valid JSON object with these exact keys:
        - file: the filepath where the root cause occurred
        - line: the line number
        - error: the type of error/exception
        - message: a brief human-readable summary of the crash

        Error Log:
        {error_log}
        """
        response = self.model.generate_content(prompt)
        try:
            # Clean up markdown JSON blocks if present
            cleaned = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            print(f"✅ [Agent] Root cause found in {data.get('file')} at line {data.get('line')}")
            return data
        except Exception as e:
            print(f"❌ [Agent] Failed to parse AI response: {e}")
            return None

    def generate_fix_code(self, analysis):
        print(f"💻 [Agent] Generating fix for {analysis['file']}...")
        if self.mock_mode:
            return f"# AutoFixer Agent added a safety check to prevent {analysis['error']}\n"
            
        prompt = f"""
        The following file ({analysis['file']}) crashed at line {analysis['line']} with this error:
        {analysis['error']}: {analysis['message']}

        Write a robust Python fix for this. Provide ONLY the full updated code for the file without any markdown wrappers or explanations. Just pure code.
        """
        response = self.model.generate_content(prompt)
        fixed_code = response.text.replace('```python', '').replace('```', '').strip()
        return fixed_code

