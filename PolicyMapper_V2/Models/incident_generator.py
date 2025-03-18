
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

# Function to analyze accident description
def analyze_accident(description):
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [
    {"role": "system", "content": "You are a professional report generator. Summarize the following accident report concisely: Incident Description: {description} "},
    {"role": "user", "name": "insurance_agent", "content": description}
    ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    for chunk in response:
        print(chunk.choices[0].delta.content or "", end="")
    
    output = response.choices[0].message.content
    return output
    
    
    






