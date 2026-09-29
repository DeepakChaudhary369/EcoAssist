import os

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Create a .env file inside the backend folder."
    )


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="EcoAssist API",
    description="AI-powered waste and recycling assistant",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# EcoAssist system instructions
# --------------------------------------------------

SYSTEM_INSTRUCTION = """
You are EcoAssist, an AI assistant focused on
waste management, recycling, and environmental awareness.

Your responsibilities:

1. Answer questions related to:
   - waste management
   - recycling
   - reuse
   - waste reduction
   - composting
   - pollution
   - environmental awareness
   - sustainability
   - plastic waste
   - paper and cardboard
   - glass
   - metal
   - organic waste
   - electronic waste
   - batteries
   - hazardous waste
   - textiles

2. Help users understand different waste categories.

3. Provide practical and general recycling or disposal guidance.

4. When an image is provided, analyze the visible object
   and explain what type of waste it appears to be.

5. Never claim certainty when the image is unclear.
   Use phrases such as:
   "This appears to be..."
   or
   "This may be..."

6. Waste-management rules can differ between locations.
   When appropriate, tell users to check their local
   municipal recycling or waste-management guidelines.

7. Do not provide dangerous instructions for handling
   hazardous chemicals, medical waste, batteries, or
   other potentially dangerous materials.

8. Do not pretend to be a local government authority.

9. If the user's question is unrelated to waste,
   recycling, or environmental topics, politely explain
   that EcoAssist is designed for environmental questions.

10. Keep responses clear, practical, and easy to understand.

11. Avoid making unsupported environmental claims.

12. Do not unnecessarily request or store personal information.
"""


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "application": "EcoAssist",
        "message": "AI Waste & Recycling Assistant API"
    }


# --------------------------------------------------
# Chat endpoint
# --------------------------------------------------

@app.post("/chat")
async def chat(
    message: str = Form(...),
    image: UploadFile | None = File(default=None)
):

    message = message.strip()

    # --------------------------------------------------
    # Validate input
    # --------------------------------------------------

    if not message and image is None:
        raise HTTPException(
            status_code=400,
            detail="Please provide a question or upload an image."
        )

    parts = []

    # --------------------------------------------------
    # Add user text
    # --------------------------------------------------

    if message:

        parts.append(
            types.Part.from_text(
                text=message
            )
        )

    else:

        parts.append(
            types.Part.from_text(
                text=(
                    "Analyze this image from a waste-management "
                    "and recycling perspective. Explain what the "
                    "object appears to be and provide appropriate "
                    "general guidance."
                )
            )
        )

    # --------------------------------------------------
    # Add image
    # --------------------------------------------------

    if image is not None:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG, and WEBP images are supported."
            )

        image_data = await image.read()

        if len(image_data) > 5 * 1024 * 1024:

            raise HTTPException(
                status_code=400,
                detail="Image size must be smaller than 5 MB."
            )

        parts.append(
            types.Part.from_bytes(
                data=image_data,
                mime_type=image.content_type
            )
        )

    # --------------------------------------------------
    # Generate Gemini response
    # --------------------------------------------------

    try:

        # Try multiple Gemini models.
        # The Google GenAI SDK handles its own transient retries.

        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite"
        ]

        response = None

        for model_name in models_to_try:

            print(
                f"Trying Gemini model: {model_name}"
            )

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Content(
                            role="user",
                            parts=parts
                        )
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )

                if response and response.text:

                    print(
                        f"Success with model: {model_name}"
                    )

                    break

            except Exception as error:

                error_text = str(error)

                print(
                    f"Model {model_name} failed: "
                    f"{error_text}"
                )

                response = None

                # Try the next model
                continue

        # --------------------------------------------------
        # Final response check
        # --------------------------------------------------

        if response is None or not response.text:

            raise HTTPException(
                status_code=503,
                detail=(
                    "EcoAssist AI is temporarily unavailable. "
                    "The Gemini service is currently busy. "
                    "Please try again in a few moments."
                )
            )

        # --------------------------------------------------
        # Return successful response
        # --------------------------------------------------

        return {
            "success": True,
            "response": response.text
        }

    # --------------------------------------------------
    # Preserve HTTP exceptions
    # --------------------------------------------------

    except HTTPException:
        raise

    # --------------------------------------------------
    # Handle unexpected errors
    # --------------------------------------------------

    except Exception as error:

        print(
            "Gemini API error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate an AI response right now."
        )