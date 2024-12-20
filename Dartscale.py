import re
import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai
from datetime import datetime
from github import Github
from streamlit_shadcn_ui import tabs

# GitHub credentials
GITHUB_TOKEN = st.secrets["github_token"]
REPO_NAME = "scooter7/webscale"
SAVE_FOLDER = "Darts"

# Initialize GitHub
github = Github(GITHUB_TOKEN)
repo = github.get_repo(REPO_NAME)

def save_to_github(file_name, content):
    """
    Save a file to the specified GitHub repository and folder.
    """
    try:
        file_path = f"{SAVE_FOLDER}/{file_name}"
        repo.create_file(
            path=file_path,
            message=f"Add {file_name}",
            content=content,
            branch="main"
        )
        st.success(f"Saved {file_name} to GitHub.")
    except Exception as e:
        st.error(f"Error saving {file_name} to GitHub: {e}")

openai.api_key = st.secrets["openai_api_key"]

# Placeholder for color categories
placeholders = {
    "Purple - caring, encouraging": {
        "verbs": [
            "assist", "befriend", "care", "collaborate", "connect", "embrace", 
            "empower", "encourage", "foster", "give", "help", "nourish", 
            "nurture", "promote", "protect", "provide", "serve", "share", 
            "shepherd", "steward", "tend", "uplift", "value", "welcome"
        ],
        "adjectives": [
            "caring", "encouraging", "attentive", "compassionate", 
            "empathetic", "generous", "hospitable", "nurturing", 
            "protective", "selfless", "supportive", "welcoming"
        ],
        "beliefs": [
            "Believe people should be cared for and encouraged",
            "Desire to make others feel safe and supported",
            "Have a strong desire to mend and heal",
            "Become loyal teammates and trusted allies",
            "Are put off by aggression and selfish motivations"
        ]
    },
    "Green - adventurous, curious": {
        "verbs": [
            "analyze", "discover", "examine", "expand", "explore", "extend", 
            "inquire", "journey", "launch", "move", "pioneer", "pursue", 
            "question", "reach", "search", "uncover", "venture", "wonder"
        ],
        "adjectives": [
            "adventurous", "curious", "discerning", "examining", "experiential", 
            "exploratory", "inquisitive", "investigative", "intrepid", 
            "philosophical"
        ],
        "beliefs": [
            "The noblest pursuit is the quest for new knowledge",
            "Continually inquiring and examining everything",
            "Have an insatiable thirst for progress and discovery",
            "Cannot sit still or accept present realities",
            "Curiosity and possibility underpin their actions"
        ]
    },
    "Maroon - gritty, determined": {
        "verbs": [
            "accomplish", "achieve", "build", "challenge", "commit", 
            "compete", "contend", "dedicate", "defend", "devote", "drive", 
            "endeavor", "entrust", "endure", "fight", "grapple", "grow", 
            "improve", "increase", "overcome", "persevere", "persist", 
            "press on", "pursue", "resolve"
        ],
        "adjectives": [
            "competitive", "determined", "gritty", "industrious", 
            "persevering", "relentless", "resilient", "tenacious", "tough", 
            "unwavering"
        ],
        "beliefs": [
            "Value extreme and hard work",
            "Gritty and strong, they’re determined to overcome",
            "Have no tolerance for laziness or inability",
            "Highly competitive and intent on proving prowess",
            "Will not be outpaced or outworked"
        ]
    },
    "Orange - artistic, creative": {
        "verbs": [
            "compose", "conceptualize", "conceive", "craft", "create", 
            "design", "dream", "envision", "express", "fashion", "form", 
            "imagine", "interpret", "make", "originate", "paint", "perform", 
            "portray", "realize", "shape"
        ],
        "adjectives": [
            "artistic", "conceptual", "creative", "eclectic", "expressive", 
            "imaginative", "interpretive", "novel", "original", "whimsical"
        ],
        "beliefs": [
            "Intensely expressive",
            "Communicate in diverse ways",
            "A lack of imagination and rigidity may feel oppressive",
            "Constructive, conceptual, and adept storytellers",
            "Manifesting new and creative concepts is their end goal"
        ]
    },
    "Yellow - innovative, intelligent": {
        "verbs": [
            "accelerate", "advance", "change", "conceive", "create", 
            "engineer", "envision", "experiment", "dream", "ignite", 
            "illuminate", "imagine", "innovate", "inspire", "invent", 
            "pioneer", "progress", "shape", "spark", "solve", "transform", 
            "unleash", "unlock"
        ],
        "adjectives": [
            "advanced", "analytical", "brilliant", "experimental", 
            "forward-thinking", "innovative", "intelligent", "inventive", 
            "leading-edge", "visionary"
        ],
        "beliefs": [
            "Thrive on new concepts and experimentation",
            "Live to make things newer and better",
            "Work well in ambiguity or unknowns",
            "Feel stifled by established processes and the status quo",
            "See endless possibilities and opportunities to invent"
        ]
    },
    "Red - entertaining, humorous": {
        "verbs": [
            "animate", "amuse", "captivate", "cheer", "delight", "encourage", 
            "energize", "engage", "enjoy", "enliven", "entertain", "excite", 
            "express", "inspire", "joke", "motivate", "play", "stir", "uplift"
        ],
        "adjectives": [
            "dynamic", "energetic", "engaging", "entertaining", 
            "enthusiastic", "exciting", "fun", "lively", "magnetic", 
            "playful", "humorous"
        ],
        "beliefs": [
            "Energetic and uplifting",
            "Motivated to entertain and create excitement",
            "Magnetic and able to rally support for new concepts",
            "Often naturally talented presenters and speakers",
            "Sensitive to the mood and condition of others"
        ]
    },
    "Blue - confident, influential": {
        "verbs": [
            "accomplish", "achieve", "affect", "assert", "cause", "command", 
            "determine", "direct", "dominate", "drive", "empower", 
            "establish", "guide", "impact", "impress", "influence", "inspire", 
            "lead", "outpace", "outshine", "realize", "shape", "succeed", 
            "transform", "win"
        ],
        "adjectives": [
            "accomplished", "assertive", "confident", "decisive", "elite", 
            "influential", "powerful", "prominent", "proven", "strong"
        ],
        "beliefs": [
            "Achievement is paramount",
            "Highly tolerant of risk and stress",
            "Seeks influence and accomplishments",
            "Comfortable making decisions with incomplete information",
            "Set strategic visions and lead the way"
        ]
    },
    "Pink - charming, elegant": {
        "verbs": [
            "arise", "aspire", "detail", "dream", "elevate", "enchant", 
            "enrich", "envision", "exceed", "excel", "experience", "improve", 
            "idealize", "imagine", "inspire", "perfect", "poise", "polish", 
            "prepare", "refine", "uplift"
        ],
        "adjectives": [
            "aesthetic", "charming", "classic", "dignified", "idealistic", 
            "meticulous", "poised", "polished", "refined", "sophisticated", 
            "elegant"
        ],
        "beliefs": [
            "Hold high regard for tradition and excellence",
            "Dream up and pursue refinement, beauty, and vitality",
            "Typically highly detailed and very observant",
            "Mess and disorder only deflates their enthusiasm"
        ]
    },
    "Silver - rebellious, daring": {
        "verbs": [
            "activate", "campaign", "challenge", "commit", "confront", "dare", 
            "defy", "disrupting", "drive", "excite", "face", "ignite", "incite", 
            "influence", "inspire", "inspirit", "motivate", "move", "push", 
            "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", 
            "fight", "free"
        ],
        "adjectives": [
            "bold", "daring", "fearless", "independent", "non-conformist", 
            "radical", "rebellious", "resolute", "unconventional", "valiant"
        ],
        "beliefs": [
            "Rule breakers and establishment challengers",
            "Have a low need to fit in with the pack",
            "Value unconventional and independent thinking",
            "Value freedom, boldness, and defiant ideas",
            "Feel stifled by red tape and bureaucratic systems"
        ]
    },
    "Beige - dedicated, humble": {
        "verbs": [
            "dedicate", "humble", "collaborate", "empower", "inspire", 
            "empassion", "transform"
        ],
        "adjectives": [
            "dedicated", "collaborative", "consistent", "empowering", 
            "enterprising", "humble", "inspiring", "passionate", "proud", 
            "traditional", "transformative"
        ],
        "beliefs": [
            "There’s no need to differentiate from others",
            "All perspectives are equally worth holding",
            "Will not risk offending anyone",
            "Light opinions are held quite loosely",
            "Information tells enough of a story"
        ]
    }
}

def clean_content(content):
    cleaned_content = re.sub(r"\*", "", content)
    cleaned_content = re.sub(r"[^\w\s,.\'\"!?-]", "", cleaned_content)
    return cleaned_content.strip()

def scrape_url_for_facts(url):
    """Scrapes the given URL for interesting facts."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description['content'] if meta_description else "No meta description found."

        # Extract headings (h1, h2, h3)
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]

        # Extract any bold or highlighted text as potential interesting facts
        highlights = [b.get_text(strip=True) for b in soup.find_all(['b', 'strong'])]

        # Combine the extracted data
        facts = f"Meta Description: {description}\n"
        facts += f"Headings: {', '.join(headings[:5])}\n"  # Limit to the top 5 headings
        facts += f"Highlights: {', '.join(highlights[:5])}\n"  # Limit to the top 5 highlights

        return facts
    except Exception as e:
        return f"Error scraping {url}: {e}"

def generate_revised_content(original_content, revision_request):
    """
    Generate revised content based on the original content and user-provided revision request.
    """
    prompt = f"""
    You are a professional editor tasked with revising content strictly according to the user's instructions.
    Start with the original content provided below and revise it following the specific revision request.
    Your response should contain ONLY the revised content, and it must:
    - Incorporate all specified changes from the revision request.
    - Preserve the meaning and structure of the original content unless explicitly stated otherwise.
    - Avoid meta-comments, explanations, or any text other than the revised content.

    Original Content:
    {original_content}

    Revision Request:
    {revision_request}

    Revised Content:
    """
    try:
        # Send the prompt to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract the revised content from the response
        revised_content = response.choices[0].message["content"]
        return clean_content(revised_content)
    except Exception as e:
        return f"Error generating revised content: {e}"

def generate_content(request, urls):
    user_prompt = request.get("user_prompt", "")
    keywords = request.get("keywords", "")
    audience = request.get("audience", "")
    specific_facts_stats = request.get("specific_facts_stats", "")
    call_to_action = request.get("call_to_action", "")
    user_content = request.get("user_content", "")
    rules = request.get("rules", "")
    writing_styles = request.get("writing_styles", [])
    style_weights = request.get("style_weights", [])
    
    # Scrape information from URLs
    url_facts = ""
    for url in urls:
        url_facts += f"Facts from {url}:\n{scrape_url_for_facts(url)}\n"

    styles_description = "\n".join(
        f"Style: {style} ({weight}% weight). Verbs: {', '.join(placeholders.get(style, {}).get('verbs', [])[:3])}, "
        f"Adjectives: {', '.join(placeholders.get(style, {}).get('adjectives', [])[:3])}, "
        f"Beliefs: {', '.join(placeholders.get(style, {}).get('beliefs', [])[:1])}"
        for style, weight in zip(writing_styles, style_weights)
    )

    prompt = f"""
    You are an expert content creator. Use the following inputs to guide the content creation:

    Prompt: {user_prompt}
    Keywords: {keywords}
    Audience: {audience}
    Specific Facts/Stats: {specific_facts_stats}
    Call to Action: {call_to_action}
    User Content: {user_content}
    Additional Rules: {rules}
    Writing Styles and Weights:
    {styles_description}
    Facts from URLs:
    {url_facts}

    Ensure the content is engaging, concise, and tailored to the audience described.
    Ensure the call to action (CTA) always appears at the bottom of the email, just above the signature section. This is critical - use the CTA verbatim as the user has entered it.
    Do not include paragraph numbering in the output. Use the verbs and adjectives for each color placeholder sparingly. 
    Do not use asterisks (*) or emojis in the response.
    Make sure to use apostrophes appropriately.
    Use proper word and line spacing.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message["content"]
    return clean_content(content)

if "content_requests" not in st.session_state:
    st.session_state.content_requests = []
if "generated_contents" not in st.session_state:
    st.session_state.generated_contents = []
if "urls" not in st.session_state:
    st.session_state.urls = []

st.title("DartScale")

# Tab Navigation
tabs_options = ["Create Content", "Generated Content", "Revisions"]
active_tab = tabs(options=tabs_options, default_value="Create Content", key="main_tabs", container_class="tabs-container")

if active_tab == "Create Content":
    st.subheader("Create Content Requests")
    
    # Number of Requests
    num_requests = st.number_input("How many pieces of content to create?", min_value=1, step=1, key="num_requests")
    
    # Generate Form Button
    if st.button("Generate Form"):
        st.session_state.content_requests = [{} for _ in range(num_requests)]
        st.session_state.urls = [[] for _ in range(num_requests)]
    
    # Render Content Creation Forms
    if st.session_state.content_requests:
        for idx, _ in enumerate(st.session_state.content_requests):
            st.markdown(f"### Content Request {idx + 1}")
            
            user_prompt = st.text_area("Enter your prompt:", key=f"prompt_{idx}")
            keywords = st.text_area("Enter optional keywords:", key=f"keywords_{idx}")
            audience = st.text_input("Define the audience:", key=f"audience_{idx}")
            specific_facts_stats = st.text_area("Enter specific facts/stats:", key=f"facts_{idx}")
            call_to_action = st.text_input("Enter a call to action:", key=f"cta_{idx}")
            user_content = st.text_area("Paste existing content (if modifying):", key=f"content_{idx}")
            rules = st.text_area("Specify additional writing style guidelines (e.g., avoid certain words):", key=f"rules_{idx}")
            
            # URL Handling
            st.markdown("#### Add URLs")
            urls = st.session_state.urls[idx]
            for url_idx, url in enumerate(urls):
                urls[url_idx] = st.text_input(f"URL {url_idx + 1}:", value=url, key=f"url_{idx}_{url_idx}")
            if st.button(f"Add URL for Request {idx + 1}", key=f"add_url_{idx}"):
                urls.append("")
            st.session_state.urls[idx] = urls
            
            # Writing Styles
            writing_styles = st.multiselect(
                label=f"Select Writing Styles for Request {idx + 1}:",
                options=list(placeholders.keys()),
                key=f"styles_{idx}",
            )
            style_weights = []
            if writing_styles:
                st.markdown("### Set Weights for Selected Writing Styles")
                for style in writing_styles:
                    weight = st.slider(
                        label=f"Weight for {style}:",
                        min_value=0,
                        max_value=100,
                        value=50,
                        step=1,
                        key=f"weight_{idx}_{style}",
                    )
                    style_weights.append(weight)
            st.session_state.content_requests[idx] = {
                "user_prompt": user_prompt,
                "keywords": keywords,
                "audience": audience,
                "specific_facts_stats": specific_facts_stats,
                "call_to_action": call_to_action,
                "user_content": user_content,
                "rules": rules,
                "writing_styles": writing_styles,
                "style_weights": style_weights,
            }
    
    # Generate All Content Button
if st.button("Generate All Content"):
    if st.session_state.content_requests:
        st.session_state.generated_contents = []
        all_requests = []

        for idx, request in enumerate(st.session_state.content_requests):
            generated_content = generate_content(request, st.session_state.urls[idx])
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
            all_requests.append({
                "Request Number": idx + 1,
                "User Prompt": request.get("user_prompt", ""),
                "Keywords": request.get("keywords", ""),
                "Audience": request.get("audience", ""),
                "Specific Facts/Stats": request.get("specific_facts_stats", ""),
                "Call to Action": request.get("call_to_action", ""),
                "User Content": request.get("user_content", ""),
                "Rules": request.get("rules", ""),
                "Writing Styles": ", ".join(request.get("writing_styles", [])),
            })
        
        # Convert requests and content to a formatted string for saving
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        requests_file_name = f"user_requests_{timestamp}.txt"
        generated_file_name = f"generated_content_{timestamp}.txt"

        requests_content = "\n\n".join(
            f"Request {r['Request Number']}:\n"
            f"User Prompt: {r['User Prompt']}\n"
            f"Keywords: {r['Keywords']}\n"
            f"Audience: {r['Audience']}\n"
            f"Specific Facts/Stats: {r['Specific Facts/Stats']}\n"
            f"Call to Action: {r['Call to Action']}\n"
            f"User Content: {r['User Content']}\n"
            f"Rules: {r['Rules']}\n"
            f"Writing Styles: {r['Writing Styles']}\n"
            for r in all_requests
        )
        generated_content = "\n\n".join([c["Content"] for c in st.session_state.generated_contents])

        # Save both files to GitHub
        save_to_github(requests_file_name, requests_content)
        save_to_github(generated_file_name, generated_content)

        st.success("All user requests and generated content have been saved to GitHub.")
    else:
        st.warning("No content requests found. Please create content requests first.")

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            content = content_data["Content"]
            st.text_area(f"Content {idx + 1}", value=content, height=300, key=f"generated_content_{idx}")
            st.download_button(f"Download Content {idx + 1}", content, f"content_{idx + 1}.txt")
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Revise Content")
    
    # Input fields for original content and revision request
    original_content = st.text_area("Paste content to revise:", height=200, key="original_content")
    revision_request = st.text_area("Describe the revisions needed:", height=200, key="revision_request")
    
    # Button to trigger content revision
    if st.button("Revise Content"):
        if original_content.strip() and revision_request.strip():
            try:
                # Call the function to generate revised content
                revised_content = generate_revised_content(original_content, revision_request)
                
                # Display the revised content
                st.text_area("Revised Content", value=revised_content, height=300, key="revised_output")
                
                # Save the revised content to GitHub
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                revision_file_name = f"revised_content_{timestamp}.txt"
                save_to_github(revision_file_name, revised_content)
                
                # Download option for the revised content
                st.download_button(
                    label="Download Revised Content",
                    data=revised_content,
                    file_name="revised_content.txt",
                    mime="text/plain",
                )
                st.success(f"Revised content saved to GitHub as {revision_file_name}.")
            except Exception as e:
                st.error(f"An error occurred during revision: {e}")
        else:
            st.error("Please provide both the original content and the revision request.")
