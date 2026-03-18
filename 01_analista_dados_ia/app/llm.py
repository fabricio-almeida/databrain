from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("groq_api_key"))

prompt = "Me fale sobre o Brasil"

def chat(prompt):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
          {
            "role": "user",
            "content": prompt,
          }
        ],
        temperature=1,
        top_p=1,
        stream=True,
        stop=None,
        max_tokens=100,
    )

    print(completion.)
        
if __name__ == "__main__":
    chat(prompt)
        
