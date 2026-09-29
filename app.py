import random
import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EcoAssist",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ============================================================
# ANIMATED ECO BACKGROUND
# ============================================================

def apply_background():

    # Fixed random positions so icons don't jump on rerun
    rng = random.Random(7)

    icons = [
        "♻️",
        "🍃",
        "🌱",
        "🌍",
        "🍀",
        "💧"
    ]

    floaters = ""

    for i in range(18):

        left = rng.randint(2, 96)
        size = rng.randint(22, 46)
        duration = rng.randint(14, 28)
        delay = rng.randint(0, 20)

        icon = icons[i % len(icons)]

        floaters += (
            f'<span class="eco-float" '
            f'style="left:{left}%; '
            f'font-size:{size}px; '
            f'animation-duration:{duration}s; '
            f'animation-delay:-{delay}s;">'
            f'{icon}'
            f'</span>'
        )

    st.markdown(
        f"""
        <style>

        /* ==================================================
           ANIMATED GRADIENT BACKGROUND
           ================================================== */

        .stApp {{
            background: linear-gradient(
                -45deg,
                #eaf7ef,
                #d5f0e0,
                #e6f6f3,
                #f3fbe9
            );

            background-size: 400% 400%;

            animation:
                ecoGradient 18s ease infinite;
        }}

        @keyframes ecoGradient {{

            0% {{
                background-position: 0% 50%;
            }}

            50% {{
                background-position: 100% 50%;
            }}

            100% {{
                background-position: 0% 50%;
            }}

        }}


        /* ==================================================
           STREAMLIT TOP BAR
           ================================================== */

        [data-testid="stHeader"] {{
            background: transparent;
        }}


        /* ==================================================
           FLOATING ECO ICONS
           ================================================== */

        .eco-float {{

            position: fixed;

            bottom: -60px;

            opacity: 0;

            z-index: 0;

            pointer-events: none;

            animation-name: ecoRise;

            animation-timing-function: linear;

            animation-iteration-count: infinite;
        }}

        @keyframes ecoRise {{

            0% {{
                transform:
                    translateY(0)
                    rotate(0deg);

                opacity: 0;
            }}

            10% {{
                opacity: 0.55;
            }}

            90% {{
                opacity: 0.55;
            }}

            100% {{
                transform:
                    translateY(-115vh)
                    rotate(360deg);

                opacity: 0;
            }}

        }}


        /* ==================================================
           CONTENT LAYER
           ================================================== */

        [data-testid="stAppViewContainer"] .main,
        [data-testid="stSidebar"] {{

            position: relative;

            z-index: 1;
        }}


        /* ==================================================
           MAIN FROSTED GLASS CARD
           ================================================== */

        .block-container {{

            max-width: 900px;

            padding:
                2rem 3rem !important;

            margin-top: 1.5rem;

            margin-bottom: 1.5rem;

            background:
                rgba(255, 255, 255, 0.60);

            backdrop-filter:
                blur(10px);

            -webkit-backdrop-filter:
                blur(10px);

            border-radius: 24px;

            border:
                1px solid
                rgba(255, 255, 255, 0.7);

            box-shadow:
                0 8px 32px
                rgba(46, 158, 107, 0.15);
        }}


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {{

            background:
                linear-gradient(
                    180deg,
                    #d9f2e4 0%,
                    #bfe6d0 100%
                );
        }}


        /* ==================================================
           ECO HEADER
           ================================================== */

        .eco-header {{

            text-align: center;

            padding:
                10px 0 20px 0;
        }}

        .eco-title {{

            font-size: 3rem;

            font-weight: 800;

            margin-bottom: 5px;

            color: #26352e;
        }}

        .eco-subtitle {{

            font-size: 1.15rem;

            color: #52615a;
        }}


        /* ==================================================
           INFORMATION BOX
           ================================================== */

        .info-box {{

            padding:
                15px 20px;

            border-radius: 14px;

            background:
                rgba(232, 247, 238, 0.88);

            border:
                1px solid
                #b9e6ca;

            margin-bottom: 20px;

            box-shadow:
                0 4px 15px
                rgba(46, 158, 107, 0.08);
        }}


        /* ==================================================
           RESPONSE BOX
           ================================================== */

        .response-box {{

            padding:
                20px;

            border-radius: 16px;

            background:
                rgba(255, 255, 255, 0.88);

            border:
                1px solid
                #dfe8e2;

            margin-top: 15px;

            box-shadow:
                0 5px 20px
                rgba(0, 0, 0, 0.05);
        }}


        /* ==================================================
           TEXT AREA
           ================================================== */

        .stTextArea textarea {{

            background:
                #ffffff;

            border:
                1.5px solid
                #cfe8da;

            border-radius:
                14px;

            transition:
                all 0.25s ease;
        }}

        .stTextArea textarea:hover {{

            border-color:
                #2E9E6B;
        }}

        .stTextArea textarea:focus {{

            border-color:
                #2E9E6B;

            box-shadow:
                0 0 0 4px
                rgba(46, 158, 107, 0.20);
        }}


        /* ==================================================
           FILE UPLOADER
           ================================================== */

        [data-testid="stFileUploader"] section {{

            border:
                2px dashed
                #9fd6b8;

            border-radius:
                14px;

            background:
                rgba(255, 255, 255, 0.70);

            transition:
                all 0.25s ease;
        }}

        [data-testid="stFileUploader"] section:hover {{

            border-color:
                #2E9E6B;

            background:
                rgba(230, 248, 238, 0.95);

            transform:
                translateY(-2px);
        }}


        /* ==================================================
           BUTTON
           ================================================== */

        .stButton > button {{

            background:
                linear-gradient(
                    90deg,
                    #2E9E6B,
                    #4cc38a
                );

            color:
                white;

            border:
                none;

            border-radius:
                14px;

            font-weight:
                600;

            padding:
                0.7rem 1rem;

            transition:
                all 0.25s ease;
        }}

        .stButton > button:hover {{

            transform:
                translateY(-3px)
                scale(1.01);

            box-shadow:
                0 10px 22px
                rgba(46, 158, 107, 0.40);

            color:
                white;
        }}

        .stButton > button:active {{

            transform:
                translateY(0)
                scale(0.99);
        }}


        /* ==================================================
           IMAGE PREVIEW
           ================================================== */

        [data-testid="stImage"] img {{

            border-radius:
                14px;

            border:
                1px solid
                #dfe8e2;

            box-shadow:
                0 5px 20px
                rgba(46, 158, 107, 0.10);
        }}


        /* ==================================================
           FOOTER
           ================================================== */

        footer {{
            visibility: hidden;
        }}

        </style>

        <div>
            {floaters}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Apply background
apply_background()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="eco-header">
    <div class="eco-title">♻️ EcoAssist</div>
    <div class="eco-subtitle">AI Waste &amp; Recycling Assistant</div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("♻️ About EcoAssist")

    st.write(
        """
        EcoAssist is an AI-powered assistant designed to help users
        understand waste, recycling, disposal practices, and
        environmental topics.
        """
    )

    st.divider()

    st.subheader("You can ask about")

    st.markdown(
        """
        - ♻️ Recycling
        - 🗑️ Waste classification
        - 🧴 Plastic waste
        - 📦 Packaging
        - 📄 Paper & cardboard
        - 🍾 Glass
        - 🥫 Metal
        - 🌱 Organic waste
        - 🔋 E-waste
        - 🌍 Environmental awareness
        - 🖼️ Waste identification from images
        """
    )

    st.divider()

    st.caption(
        "EcoAssist provides general guidance. "
        "Local recycling and disposal rules may differ."
    )


# ============================================================
# GEMINI API KEY
# ============================================================

# Local development:
# Add GEMINI_API_KEY to:
# .streamlit/secrets.toml

# Streamlit Cloud:
# Add GEMINI_API_KEY through:
# App Settings → Secrets

try:

    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

except Exception:

    GEMINI_API_KEY = ""


if not GEMINI_API_KEY:

    st.error(
        "Gemini API key is not configured. "
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )

    st.stop()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are EcoAssist, an AI assistant focused on waste management,
recycling, environmental awareness, and sustainable waste practices.

Your main responsibilities are:

1. Help users understand different types of waste.
2. Explain whether an item appears recyclable, reusable,
   compostable, or general waste.
3. Analyze uploaded images and identify waste items when possible.
4. Provide practical disposal and recycling guidance.
5. Explain waste reduction and environmentally responsible practices.
6. Answer questions about recycling, plastic, paper, cardboard,
   glass, metal, organic waste, e-waste, packaging, and
   environmental awareness.

IMAGE ANALYSIS:

When analyzing an image:

- Identify what the item appears to be.
- Explain the likely material or waste category.
- State uncertainty when the image is unclear.
- Never claim perfect identification.
- Use phrases such as "appears to be" when appropriate.
- If recycling symbols or material labels are visible,
  use them as supporting evidence.
- Do not invent recycling symbols or material information.

LOCAL RULES:

Recycling and disposal rules vary by location.

Do not claim that an item is definitely recyclable everywhere.
Recommend checking local municipal or recycling guidelines when
specific local rules are required.

SAFETY:

Do not provide dangerous instructions for handling hazardous
materials, chemicals, medical waste, batteries, or other dangerous
materials.

Instead, recommend contacting appropriate local authorities,
waste-management services, or hazardous-waste facilities.

SCOPE:

If the user asks about unrelated topics, politely explain that
EcoAssist focuses on waste management, recycling, and environmental
topics and redirect the conversation toward those areas.

Be clear, concise, helpful, and environmentally responsible.
"""


# ============================================================
# GEMINI RESPONSE FUNCTION
# ============================================================

def generate_response(user_message, uploaded_image=None):

    parts = []

    # --------------------------------------------------------
    # Add user text
    # --------------------------------------------------------

    if user_message:

        parts.append(
            types.Part.from_text(
                text=user_message
            )
        )


    # --------------------------------------------------------
    # Add image
    # --------------------------------------------------------

    if uploaded_image is not None:

        image_bytes = uploaded_image.getvalue()

        mime_type = uploaded_image.type

        parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )


    # --------------------------------------------------------
    # Gemini model fallback
    # --------------------------------------------------------

    models_to_try = [

        "gemini-3.8-flash",

        "gemini-3.7-flash",

        "gemini-3.6-flash",

        "gemini-3.5-flash-lite"

    ]

    last_error = None


    # --------------------------------------------------------
    # Try each model
    # --------------------------------------------------------

    for model_name in models_to_try:

        try:

            with st.spinner(
                "EcoAssist is analyzing your request..."
            ):

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


            # ------------------------------------------------
            # Successful response
            # ------------------------------------------------

            if response and response.text:

                return response.text, model_name


        except Exception as error:

            last_error = error

            error_text = str(error)


            # -----------------------------------------------
            # Temporary service unavailable
            # -----------------------------------------------

            if (
                "503" in error_text
                or
                "UNAVAILABLE" in error_text
            ):

                continue


            # -----------------------------------------------
            # Rate limit / quota
            # -----------------------------------------------

            if (
                "429" in error_text
                or
                "RESOURCE_EXHAUSTED" in error_text
            ):

                continue


            # -----------------------------------------------
            # Other errors
            # -----------------------------------------------

            continue


    # --------------------------------------------------------
    # All models failed
    # --------------------------------------------------------

    raise RuntimeError(
        "All Gemini models are currently unavailable. "
        f"Last error: {last_error}"
    )


# ============================================================
# USER INPUT SECTION
# ============================================================

st.markdown(
    """
<div class="info-box">
    💡 <b>Ask EcoAssist a question or upload an image of a waste item.</b>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# QUESTION INPUT
# ============================================================

user_message = st.text_area(
    "💬 Your question",
    placeholder="Example: Can this plastic bottle be recycled?",
    height=120
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_image = st.file_uploader(
    "🖼️ Upload a waste image (optional)",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)


# ============================================================
# IMAGE PREVIEW
# ============================================================

if uploaded_image is not None:

    st.image(
        uploaded_image,
        caption="Uploaded image",
        use_container_width=True
    )


# ============================================================
# ASK ECOASSIST BUTTON
# ============================================================

if st.button(
    "♻️ Ask EcoAssist",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not user_message and uploaded_image is None:

        st.warning(
            "Please enter a question or upload an image."
        )

    else:

        try:

            # ------------------------------------------------
            # Generate AI response
            # ------------------------------------------------

            response_text, model_used = generate_response(
                user_message,
                uploaded_image
            )


            # ------------------------------------------------
            # Response container
            # ------------------------------------------------

            st.markdown(
                '<div class="response-box">',
                unsafe_allow_html=True
            )

            st.subheader("🤖 EcoAssist")

            st.markdown(response_text)

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # Technical information
            # ------------------------------------------------

            with st.expander("Technical details"):

                st.write(
                    f"Gemini model used: `{model_used}`"
                )


        except Exception as error:

            # ------------------------------------------------
            # User-friendly error
            # ------------------------------------------------

            st.error(
                "EcoAssist could not generate a response right now."
            )


            # ------------------------------------------------
            # Technical error
            # ------------------------------------------------

            with st.expander("Technical error"):

                st.code(
                    str(error)
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "♻️ EcoAssist — AI Waste & Recycling Assistant"
)