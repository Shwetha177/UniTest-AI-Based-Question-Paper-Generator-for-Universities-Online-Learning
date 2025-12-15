import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_questions(text, q_type="mcq", num=5, difficulty="easy", show_answers=False):
    ans_instruction = "Include answer key." if show_answers else "Do NOT include answers."

    prompt = f"""
    You are an AI exam question generator.

    Syllabus / Notes Content:
    {text}

    Generate {num} {q_type.upper()} questions.
    Difficulty Level: {difficulty.upper()}
    {ans_instruction}

    Rules:
    - If MCQ: provide exactly 4 options.
    - If ONE-WORD: give short direct answers (only if answer key is ON).
    - If LONG: generate descriptive questions only.
    - Do not add extra explanation unless asked.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
