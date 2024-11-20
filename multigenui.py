import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import input, textarea, button, tabs, card
import openai

# Initialize OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

# Styling
st.markdown(
    """
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo-container img {
        width: 300px;
    }
    .app-container {
        border-left: 5px solid #58258b;
        border-right: 5px solid #58258b;
        padding-left: 15px;
        padding-right: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="logo-container">
        <img src="https://seeklogo.com/images/E/east-carolina-university-logo-D87F964E5D-seeklogo.com.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Initialize placeholders
placeholders = {
    "Purple - caring, encouraging": {
        "verbs": ["assist", "befriend", "care", "collaborate", "connect", "embrace", "empower", "encourage", "foster", "give", "help", "nourish", "nurture", "promote", "protect", "provide", "serve", "share", "shepherd", "steward", "tend", "uplift", "value", "welcome"],
        "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"],
        "beliefs": ["Believe people should be cared for and encouraged", "Desire to make others feel safe and supported", "Have a strong desire to mend and heal", "Become loyal teammates and trusted allies", "Are put off by aggression and selfish motivations"]
    },
    "Green - adventurous, curious": {
        "verbs": ["analyze", "discover", "examine", "expand", "explore", "extend", "inquire", "journey", "launch", "move", "pioneer", "pursue", "question", "reach", "search", "uncover", "venture", "wonder"],
        "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"],
        "beliefs": ["The noblest pursuit is the quest for new knowledge", "Continually inquiring and examining everything", "Have an insatiable thirst for progress and discovery", "Cannot sit still or accept present realities", "Curiosity and possibility underpin their actions"]
    },
    "Maroon - gritty, determined": {
        "verbs": ["accomplish", "achieve", "build", "challenge", "commit", "compete", "contend", "dedicate", "defend", "devote", "drive", "endeavor", "entrust", "endure", "fight", "grapple", "grow", "improve", "increase", "overcome", "persevere", "persist", "press on", "pursue", "resolve"],
        "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"],
        "beliefs": ["Value extreme and hard work", "Gritty and strong, they’re determined to overcome", "Have no tolerance for laziness or inability", "Highly competitive and intent on proving prowess", "Will not be outpaced or outworked"]
    },
    "Orange - artistic, creative": {
        "verbs": ["compose", "conceptualize", "conceive", "craft", "create", "design", "dream", "envision", "express", "fashion", "form", "imagine", "interpret", "make", "originate", "paint", "perform", "portray", "realize", "shape"],
        "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"],
        "beliefs": ["Intensely expressive", "Communicate in diverse ways", "A lack of imagination and rigidity may feel oppressive", "Constructive, conceptual, and adept storytellers", "Manifesting new and creative concepts is their end goal"]
    },
    "Yellow - innovative, intelligent": {
        "verbs": ["accelerate", "advance", "change", "conceive", "create", "engineer", "envision", "experiment", "dream", "ignite", "illuminate", "imagine", "innovate", "inspire", "invent", "pioneer", "progress", "shape", "spark", "solve", "transform", "unleash", "unlock"],
        "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"],
        "beliefs": ["Thrive on new concepts and experimentation", "Live to make things newer and better", "Work well in ambiguity or unknowns", "Feel stifled by established processes and the status quo", "See endless possibilities and opportunities to invent"]
    },
    "Red - entertaining, humorous": {
        "verbs": ["animate", "amuse", "captivate", "cheer", "delight", "encourage", "energize", "engage", "enjoy", "enliven", "entertain", "excite", "express", "inspire", "joke", "motivate", "play", "stir", "uplift"],
        "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"],
        "beliefs": ["Energetic and uplifting", "Motivated to entertain and create excitement", "Magnetic and able to rally support for new concepts", "Often naturally talented presenters and speakers", "Sensitive to the mood and condition of others"]
    },
    "Blue - confident, influential": {
        "verbs": ["accomplish", "achieve", "affect", "assert", "cause", "command", "determine", "direct", "dominate", "drive", "empower", "establish", "guide", "impact", "impress", "influence", "inspire", "lead", "outpace", "outshine", "realize", "shape", "succeed", "transform", "win"],
        "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"],
        "beliefs": ["Achievement is paramount", "Highly tolerant of risk and stress", "Seeks influence and accomplishments", "Comfortable making decisions with incomplete information", "Set strategic visions and lead the way"]
    },
    "Pink - charming, elegant": {
        "verbs": ["arise", "aspire", "detail", "dream", "elevate", "enchant", "enrich", "envision", "exceed", "excel", "experience", "improve", "idealize", "imagine", "inspire", "perfect", "poise", "polish", "prepare", "refine", "uplift"],
        "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated", "elegant"],
        "beliefs": ["Hold high regard for tradition and excellence", "Dream up and pursue refinement, beauty, and vitality", "Typically highly detailed and very observant", "Mess and disorder only deflates their enthusiasm"]
    },
    "Silver - rebellious, daring": {
        "verbs": ["activate", "campaign", "challenge", "commit", "confront", "dare", "defy", "disrupt", "drive", "excite", "face", "ignite", "incite", "influence", "inspire", "motivate", "move", "push", "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", "fight", "free"],
        "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"],
        "beliefs": ["Rule breakers and establishment challengers", "Have a low need to fit in with the pack", "Value unconventional and independent thinking", "Value freedom, boldness, and defiant ideas", "Feel stifled by red tape and bureaucratic systems"]
    },
    "Beige - dedicated, humble": {
        "verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "transform"],
        "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "traditional", "transformative"],
        "beliefs": ["There’s no need to differentiate from others", "All perspectives are equally worth holding", "Will not risk offending anyone", "Light opinions are held quite loosely", "Information tells enough of a story"]
    },
}

# Initialize session state variables
if "content_requests" not in st.session_state:
    st.session_state.content_requests = []
if "generated_contents" not in st.session_state:
    st.session_state.generated_contents = []

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars, call_to_action):
    prompt = f"{user_prompt}\n\nKeywords: {keywords}\nAudience: {audience}\nFacts/Stats: {specific_facts_stats}\nCall to Action: {call_to_action}\nMinimum Characters: {min_chars}\nMaximum Characters: {max_chars}\nContent:\n{content}"
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        attributes = placeholders[style]
        verbs = ", ".join(attributes["verbs"][:3])
        adjectives = ", ".join(attributes["adjectives"][:3])
        beliefs = "; ".join(attributes["beliefs"][:1])
        prompt += f"\nStyle: {style} - Incorporate verbs ({verbs}), adjectives ({adjectives}), and beliefs ({beliefs}) in {weight}% of the content."
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message["content"].strip()

# Tabs for navigation
tabs_options = ["Create Content", "Generated Content", "Revisions"]
active_tab = tabs(options=tabs_options, default_value="Create Content", key="main_tabs")

# Create Content Tab
if active_tab == "Create Content":
    st.subheader("Create Content Requests")

    # Number of content requests
    num_requests = input(
        default_value="1",
        type="number",
        placeholder="How many pieces of content to create?",
        key="num_requests",
    )

    if button(text="Generate Form", key="generate_form"):
        st.session_state.content_requests = [{} for _ in range(int(num_requests))]

    if st.session_state.content_requests:
        for idx, _ in enumerate(st.session_state.content_requests):
            st.markdown(f"### Content Request {idx + 1}")

            # Input fields
            user_prompt = textarea(default_value="", placeholder="Enter your prompt...", key=f"prompt_{idx}")
            keywords = textarea(default_value="", placeholder="Enter optional keywords...", key=f"keywords_{idx}")
            audience = input(default_value="", placeholder="Define the audience...", key=f"audience_{idx}")
            specific_facts_stats = textarea(default_value="", placeholder="Enter specific facts/stats...", key=f"facts_{idx}")
            call_to_action = input(default_value="", placeholder="Enter a call to action...", key=f"cta_{idx}")
            user_content = textarea(default_value="", placeholder="Paste existing content (if modifying)...", key=f"content_{idx}")
            min_chars = input(default_value="", placeholder="Enter minimum character count...", key=f"min_chars_{idx}")
            max_chars = input(default_value="", placeholder="Enter maximum character count...", key=f"max_chars_{idx}")
            writing_styles = st.multiselect(label=f"Select Writing Styles for Request {idx + 1}:", options=list(placeholders.keys()), default=[], key=f"styles_{idx}")
            style_weights = []
            if writing_styles:
                st.markdown("### Set Weights for Selected Writing Styles")
                for style in writing_styles:
                    weight = st.slider(label=f"Weight for {style}:", min_value=0, max_value=100, value=50, step=1, key=f"weight_{idx}_{style}")
                    style_weights.append(weight)

            # Save request data
            st.session_state.content_requests[idx] = {
                "user_prompt": user_prompt,
                "keywords": keywords,
                "audience": audience,
                "specific_facts_stats": specific_facts_stats,
                "call_to_action": call_to_action,
                "user_content": user_content,
                "min_chars": min_chars,
                "max_chars": max_chars,
                "writing_styles": writing_styles,
                "style_weights": style_weights,
            }

    if button(text="Generate All Content", key="generate_all"):
        st.session_state.generated_contents = []
        for idx, request in enumerate(st.session_state.content_requests):
            generated_content = generate_article(
                request["user_content"],
                request["writing_styles"],
                request["style_weights"],
                request["user_prompt"],
                request["keywords"],
                request["audience"],
                request["specific_facts_stats"],
                request["min_chars"],
                request["max_chars"],
                request["call_to_action"],
            )
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")

# Generated Content Tab
elif active_tab == "Generated Content":
    st.subheader("Generated Content")

    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            card(
                title=f"Generated Content {content_data['Request']}",
                content=content_data["Content"],
                description="Generated based on user input.",
                key=f"card_{idx}",
            )
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

# Revisions Tab
elif active_tab == "Revisions":
    st.subheader("Make Revisions")

    revision_content = textarea(default_value="", placeholder="Paste the generated content to revise...", key="revision_content")
    revision_request = textarea(default_value="", placeholder="Describe your revision requests...", key="revision_request")

    if button(text="Revise Content", key="revise"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": revision_content},
            {"role": "user", "content": revision_request},
        ]
        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
        revised_content = response.choices[0].message["content"].strip()
        card(title="Revised Content", content=revised_content, description="Updated based on your revision request.", key="revised_card")

st.markdown('</div>', unsafe_allow_html=True)
