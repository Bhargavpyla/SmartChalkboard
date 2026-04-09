import os
import io
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.genai as genai
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="CalCam")
templates = Jinja2Templates(directory="templates")

current_chat = None

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables. Please set it in a .env file.")

client = genai.Client(api_key=api_key)

# The prompt assigned for the persona
PROMPT = (
    "Act as an encouraging, patient, and friendly math tutor who wants the student to truly "
    "understand the concepts, not just memorize them. Look closely at the handwritten image.\n\n"
    
    "🧠 YOUR TEACHING LOGIC:\n"
    "1. First, clearly state the math problem you see.\n"
    "2. Check if the student wrote down an attempted answer.\n"
    "3. If they wrote a wrong answer: Kindly explain exactly where their logic went wrong. "
    "Never make them feel bad. Guide them to the correct answer step-by-step.\n"
    "4. If they wrote the correct answer: Enthusiastically congratulate them!\n"
    "5. If there is no answer: Solve it step-by-step. Focus on clarity first and depth second. "
    "Use clear analogies from everyday life to explain abstract technical steps so they build confidence.\n\n"
    
    "💻 CRITICAL FORMATTING RULES FOR TERMINAL:\n"
    "1. Do NOT use complex LaTeX (like $$ or \\frac). Many terminals cannot render them.\n"
    "2. Use clear ASCII math or simple Markdown. For example:\n"
    "   - Use ^ for exponents: x^2\n"
    "   - Use / for fractions: (x+1)/(x-1)\n"
    "   - Use d/dx for derivatives\n"
    "   - Use 'integral of ... dx' for integrals\n"
    "   - Use SQRT() for square roots\n"
    "3. Use **bold** for key mathematical terms and the final answer.\n"
    "4. Keep your sentences conversational, structured, and easy to read in a narrow console window.\n\n"
    "⚠️ RETURN FORMAT:\n"
    "You must return ONLY a raw JSON object with two keys: 'topic' (a short 1-3 word classification like 'Linear Algebra' or 'Calculus') and 'markdown' (your complete response text formatted with Markdown as requested above)."
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/solve")
async def solve_math_problem(file: UploadFile = File(...)):
    global current_chat
    try:
        # Load the image using PIL from the uploaded file bytes
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        
        # Use simple Generation Config to enforce JSON
        import json
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[PROMPT, img],
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        try:
            # Strip markdown formatting that Gemma might wrap the JSON string with
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            data = json.loads(raw_text.strip())
            topic = data.get("topic", "General Math")
            clean_text = data.get("markdown", "")
            
            if not clean_text and topic:
                # If the json structure didn't have markdown but failed fallback
                clean_text = response.text
                
        except Exception as e:
            # If parsing truly failed, simply pass the raw text to the frontend
            topic = "General Math"
            clean_text = response.text
                
        # Clean up any accidental LaTeX/MathJax delimiters if AI still uses them
        clean_text = clean_text.replace("$$", "").replace("$", "")
        
        # Initialize the stateful Chat memory without an extra API call
        from google.genai import types
        
        fallback_prompt = (
            f"{PROMPT}\n\n"
            f"[SYSTEM NOTE: The user provided an image. You successfully processed it. "
            f"Here is your own generated step-by-step response to use as active context for their follow-up questions:]\n\n"
            f"{clean_text}"
        )
        
        history = [
            types.Content(role="user", parts=[types.Part.from_text(text=fallback_prompt)]),
            types.Content(role="model", parts=[types.Part.from_text(text=response.text)])
        ]
        
        current_chat = client.chats.create(
            model='gemini-2.5-flash',
            history=history
        )
        
        return JSONResponse(content={"markdown": clean_text, "topic": topic})
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
async def send_chat_message(msg: ChatMessage):
    global current_chat
    if not current_chat:
        return JSONResponse(content={"error": "Start by capturing a problem first!"}, status_code=400)
    
    try:
        response = current_chat.send_message(msg.message)
        
        # Try to parse the response if the model is still returning JSON dict instances natively!
        import json
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        try:
            data = json.loads(raw_text.strip())
            clean_text = data.get("markdown", "")
            if not clean_text:
                clean_text = response.text
        except:
            clean_text = response.text

        clean_text = clean_text.replace("$$", "").replace("$", "")
        return JSONResponse(content={"markdown": clean_text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
