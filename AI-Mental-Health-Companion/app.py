
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("Please set GEMINI_API_KEY in your environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Safety settings for mental health context
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# System prompt for mental health companion
SYSTEM_PROMPT = """
You are a compassionate, empathetic mental health companion. Your role is to:

1. Provide supportive, non-judgmental listening
2. Offer evidence-based coping strategies and mindfulness techniques
3. Help users identify and challenge negative thought patterns
4. Suggest relaxation and self-care practices
5. Provide psychoeducation about common mental health concerns

IMPORTANT GUIDELINES:
- Always maintain a warm, caring tone
- Never provide medical diagnoses or replace professional therapy
- Encourage seeking professional help when appropriate
- Focus on practical, actionable advice
- Validate feelings while promoting healthy coping mechanisms
- Avoid making promises of cures or guarantees
- Be culturally sensitive and inclusive

If a user expresses immediate crisis or suicidal thoughts, gently encourage them to contact emergency services or crisis hotlines.

Remember: You are a supportive companion, not a replacement for professional mental healthcare.
"""

def get_mental_health_response(user_message, conversation_history=[]):
    """Get response from Gemini AI for mental health support"""
    try:
        # Initialize the model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            safety_settings=safety_settings
        )
        
        # Prepare conversation context
        context = SYSTEM_PROMPT + "\n\nConversation History:\n"
        for msg in conversation_history[-6:]:  # Keep last 6 exchanges for context
            context += f"User: {msg['user']}\n"
            context += f"Assistant: {msg['assistant']}\n"
        
        context += f"\nCurrent User Message: {user_message}"
        
        # Generate response
        response = model.generate_content(context)
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble responding right now. Please try again in a moment. Remember, if you're in crisis, please contact a mental health professional or emergency services."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get AI response
        ai_response = get_mental_health_response(user_message, conversation_history)
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Sorry, something went wrong. Please try again.',
            'status': 'error'
        }), 500

@app.route('/crisis_resources')
def crisis_resources():
    """Provide crisis resources"""
    resources = {
        'emergency': '911 (or your local emergency number)',
        'crisis_text_line': 'Text HOME to 741741',
        'suicide_lifeline': '988 Suicide & Crisis Lifeline',
        'trevor_project': '1-866-488-7386 (LGBTQ youth)',
        'veterans_crisis': '1-800-273-8255, Press 1'
    }
    return jsonify(resources)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)