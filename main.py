import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types as genai_types
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY)

ORT_TUTOR_PROMPT = """
You are an expert Mathematics tutor specializing in the Kyrgyz Republic's ORT (Общереспубликанское тестирование) and school curriculum for grades 5-11.

LANGUAGES:
- Automatically detect the language (Russian or Kyrgyz) and respond STRICTLY in that language.

STRICT FORMATTING RULES (CRITICAL):
- DO NOT use any Markdown, HTML, or Telegram special characters.
- NEVER use asterisks (*), double asterisks (**), hashtags (#), triple hashtags (###), underscores (_), or backticks (`).
- DO NOT use raw LaTeX symbols like $, $$, or \\frac{}{}. Write math formulas using plain text and standard keyboard symbols (e.g., use "1/4", "sqrt(x)", "pi", "T = (t1 * t2) / (t1 + t2)").
- Present your answer as clean, readable paragraphs of plain text. You can use standard dashes (-) for lists, but no special formatting.

ROLE & GUIDELINES:
1. Explain the concept step-by-step so the student can learn, do not just give the final answer.
2. For ORT questions (Quantitative Comparisons / Чоңдуктарды салыштыруу): Explain the logic, teach shortcuts/estimation to save time.
3. Use correct math terminology in the respective language.
"""

@app.get("/", response_class=HTMLResponse)
async def get_site():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>Файл index.html не найден в корневой папке проекта! Проверьте загрузку на GitHub.</h3>"

@app.post("/ask-math")
async def ask_math(question: str = Body(embed=True)):
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config={
                "system_instruction": ORT_TUTOR_PROMPT,
                "temperature": 0.3
            }
        )
        return {"status": "success", "answer": response.text}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка: {str(e)}"}