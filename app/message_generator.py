import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_message(business_name):
    """Generate English cold outreach message"""
    
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "gsk_your_api_key_here":
        return fallback_message(business_name)
    
    prompt = f"""
    Write a short cold outreach message for a business named "{business_name}".
    
    Offer automation services to help them get more customers.
    
    Requirements:
    - Professional and polite tone
    - Maximum 40 words
    - Include a clear call-to-action (ask for 5 minutes chat)
    - English language only
    
    Example: "Hi {business_name}, we help businesses like yours get more customers through smart automation. Can we schedule a quick 5-min chat to explain?"
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Model terbaru
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=120
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  ⚠️ API error: {e}")
        return fallback_message(business_name)

def fallback_message(name):
    templates = [
        f"Hi {name}, we help businesses get more customers through automation. Would you be open to a 5-min chat to learn more?",
        f"Hello {name}, we offer automation solutions to boost your customer acquisition. Quick 5-min discussion?",
        f"Dear {name}, our automation services can help grow your customer base. Interested in a brief chat?"
    ]
    import random
    return random.choice(templates)