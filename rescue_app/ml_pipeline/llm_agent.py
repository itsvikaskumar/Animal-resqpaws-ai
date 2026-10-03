from django.conf import settings
from google import genai


class LLMInformationAgent:
    """
    ResQPaws AI Information Agent.

    Uses Google Gemini for:
    - General AI chat
    - Animal emergency questions
    - First-aid guidance
    - ResQPaws system questions
    - Conversation-aware responses

    Falls back to a local knowledge base if Gemini is unavailable.
    """

    # =========================================================
    # RESQPaws AI SYSTEM PROMPT
    # =========================================================

    SYSTEM_PROMPT = """
You are ResQPaws AI Assistant.

ResQPaws is an animal emergency rescue management system.

Your job is to help users with:
- Animal emergency questions
- Basic animal first-aid information
- Animal symptoms and general health information
- Rescue procedures
- Rescue center information
- Ambulance tracking explanations
- Hospital treatment workflow
- ResQPaws website features
- General questions when appropriate

IMPORTANT RULES:

1. Give clear, simple and useful answers.
2. Understand the user's current question using the conversation context.
3. If the user asks a general question, answer it normally.
4. If the user asks about an animal emergency, prioritize safety.
5. Encourage contacting a qualified veterinarian for serious or uncertain conditions.
6. Do not claim that an ambulance has been dispatched unless the application actually dispatched one.
7. Do not invent Case IDs, ambulance locations, rescue center availability,
   hospital availability or rescue status.
8. If real application data is not provided, clearly say that you cannot
   see the live application data.
9. Do not provide dangerous or unnecessarily risky instructions.
10. Keep answers easy to understand.
11. Do not repeatedly introduce yourself unless the user asks who you are.
12. Remember relevant information from the conversation context.
"""


    # =========================================================
    # LOCAL FALLBACK KNOWLEDGE BASE
    # =========================================================

    KNOWLEDGE_BASE = {

        'dog': {
            'bleeding': (
                "Keep the dog calm and minimize movement. "
                "Apply gentle pressure with a clean cloth or sterile gauze "
                "and seek veterinary help as soon as possible."
            ),

            'fracture': (
                "Do not try to straighten the injured limb. "
                "Keep the dog as still as possible and arrange veterinary "
                "care immediately."
            ),

            'burn': (
                "Cool the affected area with clean, cool running water. "
                "Do not apply butter, oil or other household substances. "
                "Contact a veterinarian for further care."
            ),
        },

        'cat': {
            'bleeding': (
                "Keep the cat calm and minimize movement. "
                "Use clean gauze or cloth to apply gentle pressure "
                "and seek veterinary assistance."
            ),

            'fracture': (
                "Handle the cat carefully and minimize movement. "
                "Keep it in a secure padded carrier and contact a veterinarian."
            ),
        },

        'cow': {
            'bleeding': (
                "Keep the cow calm and away from traffic or other hazards. "
                "Apply gentle pressure with a clean cloth if safe to do so "
                "and contact a veterinary service."
            ),

            'fracture': (
                "Do not force the cow to walk. Keep the animal calm in a "
                "safe area and contact a large-animal veterinarian."
            ),
        },
    }


    # =========================================================
    # GEMINI CLIENT
    # =========================================================

    @staticmethod
    def get_gemini_client():

        gemini_key = getattr(settings, 'GEMINI_API_KEY', '')

        if not gemini_key:
            return None

        try:
            return genai.Client(api_key=gemini_key)

        except Exception as e:
            print(f"[Gemini Client Error] {e}")
            return None


    # =========================================================
    # GEMINI CHAT
    # =========================================================

    @staticmethod
    def ask_gemini(prompt):

        client = LLMInformationAgent.get_gemini_client()

        if client is None:
            return None

        try:

            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )

            if response and response.text:
                return response.text.strip()

            return None

        except Exception as e:

            error_text = str(e).lower()

            # ---------------------------------------------
            # Gemini Free Tier / Rate Limit
            # ---------------------------------------------

            if (
                '429' in error_text
                or 'resource_exhausted' in error_text
                or 'quota' in error_text
                or 'rate limit' in error_text
            ):
                print("[Gemini] Free Tier/API limit reached.")

                return None

            # ---------------------------------------------
            # Authentication
            # ---------------------------------------------

            if '401' in error_text or '403' in error_text:
                print("[Gemini] API key/authentication problem.")
                return None

            # ---------------------------------------------
            # Model/API error
            # ---------------------------------------------

            print(f"[Gemini API Error] {e}")

            return None


    # =========================================================
    # FIRST AID
    # =========================================================

    @staticmethod
    def generate_first_aid(animal_type, injury_type, severity):

        prompt = f"""
{LLMInformationAgent.SYSTEM_PROMPT}

A user has reported an animal emergency.

Animal:
{animal_type}

Detected injury:
{injury_type}

Severity:
{severity}

Provide short, safe first-aid guidance for the person currently with
the animal.

Use 3-5 clear bullet points.

Do not suggest risky procedures.

End by recommending veterinary/emergency professional help when appropriate.
"""

        # Try Gemini first
        gemini_response = LLMInformationAgent.ask_gemini(prompt)

        if gemini_response:
            return gemini_response


        # =====================================================
        # LOCAL FALLBACK
        # =====================================================

        animal_text = str(animal_type).lower()
        injury_text = str(injury_type).lower()

        animal_key = 'dog'

        for animal in [
            'cat',
            'cow',
            'goat',
            'horse',
        ]:

            if animal in animal_text:
                animal_key = animal
                break


        if (
            'fracture' in injury_text
            or 'broken' in injury_text
            or 'limb' in injury_text
        ):
            injury_key = 'fracture'

        elif 'burn' in injury_text:
            injury_key = 'burn'

        else:
            injury_key = 'bleeding'


        knowledge = LLMInformationAgent.KNOWLEDGE_BASE.get(
            animal_key,
            LLMInformationAgent.KNOWLEDGE_BASE['dog']
        )

        guide = knowledge.get(
            injury_key,
            knowledge.get('bleeding')
        )

        return (
            f"🩺 ResQPaws AI First-Aid Guidance\n\n"
            f"Animal: {animal_type}\n"
            f"Severity: {severity}\n\n"
            f"{guide}\n\n"
            f"⚠️ For serious or worsening conditions, contact a "
            f"qualified veterinarian or emergency animal service."
        )


    # =========================================================
    # CHAT RESPONSE
    # =========================================================

    @staticmethod
    def chat_response(user_message, context=""):

        user_message = str(user_message).strip()

        if not user_message:
            return "Please enter a message so I can help you."


        prompt = f"""
{LLMInformationAgent.SYSTEM_PROMPT}

CONVERSATION CONTEXT:
{context}

LATEST USER MESSAGE:
{user_message}

Answer ONLY the user's latest message.

Use the conversation context when it is relevant.

Do not repeat the generic ResQPaws introduction.

If the user changes the topic, follow the new topic.

Answer naturally like a helpful AI assistant.
"""

        # =====================================================
        # GEMINI
        # =====================================================

        gemini_response = LLMInformationAgent.ask_gemini(prompt)

        if gemini_response:
            return gemini_response


        # =====================================================
        # FALLBACK
        # =====================================================

        msg = user_message.lower()


        if 'ambulance' in msg or 'tracking' in msg:

            return (
                "ResQPaws can provide ambulance tracking after an ambulance "
                "has actually been assigned to a rescue case. "
                "For live status, please use the Track Report section."
            )


        if (
            'poison' in msg
            or 'toxic' in msg
            or 'swallowed' in msg
        ):

            return (
                "If an animal may have swallowed something harmful, "
                "do not give home remedies or induce vomiting unless a "
                "qualified veterinarian specifically tells you to. "
                "Contact a veterinarian or emergency animal service."
            )


        if (
            'first aid' in msg
            or 'injured' in msg
            or 'injury' in msg
        ):

            return (
                "Keep the injured animal calm and minimize movement. "
                "Avoid attempting complicated treatment yourself and "
                "contact a qualified veterinarian or animal rescue service."
            )


        if 'hello' in msg or 'hi' in msg or 'hey' in msg:

            return (
                "Hello! 👋 I'm ResQPaws AI Assistant. "
                "How can I help you?"
            )


        return (
            "I'm temporarily unable to connect to Gemini AI. "
            "Please try again in a moment."
        )