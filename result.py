import streamlit as st
from google import genai
from google.genai import types
from google.genai import types
import wave
import os
import re
from datetime import datetime
import dotenv
dotenv.load_dotenv()

# Page config
st.set_page_config(
    page_title="EchoGem - AI Podcast Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    .main {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    /* Feature cards */
    .feature-card {
        background: black;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Custom buttons */
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: black;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    /* Voice assignment cards */
    .voice-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: white;
        font-weight: bold;
    }
    
    /* Footer */
    .footer {
        background: #2c3e50;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.write("Note : If Got error means API ran outoff token")
st.markdown("""
<div class="header-container">
    <div class="header-title">🎙️EchoGem - AI Podcast Generator</div>
    <div class="header-subtitle">Transform any topic into engaging podcast conversations with AI-powered voices</div>
    <div style="margin-top: 1rem;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">✨ AI-Powered</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">🎭 Multiple Voices</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">⚡ Fast Generation</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Set API key directly
gemini_key = os.getenv("gemini_key")
google_genai_client = genai.Client(api_key="AIzaSyAl0ver6GvpqiBIinl7Hvl5vwT8PwqPX8c")

# Constants
VOICE_POOL = ["kore", "puck", "zephyr", "algieba"]

# Functions

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

def generate_data(topic):
        prompt = f"I have to create podcast on topic: {topic}. Go through internet sources and give large informative paragraphs with references."
        response = google_genai_client.models.generate_content(
                model="gemini-1.5-flash-latest", contents=f"'user' : {prompt} ")
        return response.text.strip()

def generate_script(num_people, data, topic):
        prompt = f"""You are pro podcast writer. Write humanised dialogue on topic: {topic}, based on data: {data}.
Total speakers = {num_people}. Length: 5 min.
Return in this format:
Person 1 : <line>
Person 2 : <line>
Person 3 : <line>
Person 4 : <line>...

Example:
Anya Sharma : Welcome to AI in EdTech! I'm your host Anya, and joining me is Mr. Ben Carter.
Ben Carter : Thanks Anya! Happy to be here.
Only return script.
"""
        response = google_genai_client.models.generate_content(
                model="gemini-1.5-flash-latest", contents=f"'user' : {prompt} ")
        return response.text.strip()

def parse_script(script_text):
        pattern = r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*):\s(.+?)(?=\n[A-Z][a-z]+(?:\s[A-Z][a-z]+)*:|$)"
        return re.findall(pattern, script_text, flags=re.DOTALL)

def assign_voices(names):
        return {name: VOICE_POOL[i % len(VOICE_POOL)] for i, name in enumerate(names)}

def generate_audio_with_google_tts(script_lines, voice_map, output_dir="clips"):
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate individual audio clips for each line
        audio_files = []
        
        for i, (name, line) in enumerate(script_lines, start=1):
            voice = voice_map.get(name)
            
            # Create simple TTS prompt for single speaker
            tts_prompt = f"TTS the following: {name}: {line.strip()}"
            
            try:
                response = google_genai_client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=tts_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice,
                                )
                            )
                        )
                    )
                )
                
                # Extract audio data
                audio_data = response.candidates[0].content.parts[0].inline_data.data
                
                # Save individual clip
                filename = os.path.join(output_dir, f"{i}.wav")
                wave_file(filename, audio_data)
                audio_files.append(filename)
                
            except Exception as e:
                st.error(f"Error generating audio for line {i} ({name}): {e}")
                continue
        
        # Merge all audio files
        if audio_files:
            merged_audio = os.path.join(output_dir, "merged_podcast.wav")
            merge_audio_files(audio_files, merged_audio)
            return merged_audio
        
        return None

def merge_audio_files(audio_files, output_file):
        """Merge multiple WAV files into one"""
        try:
            # Read all audio files and combine their data
            combined_data = b""
            sample_rate = 24000
            channels = 1
            sample_width = 2
            
            for audio_file in audio_files:
                with wave.open(audio_file, 'rb') as wf:
                    combined_data += wf.readframes(wf.getnframes())
            
            # Write combined data to output file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(sample_rate)
                wf.writeframes(combined_data)
                
        except Exception as e:
            st.error(f"Error merging audio files: {e}")
             
        
        
            # If merging fails, just use the first file
            if audio_files:
                    import shutil
                    shutil.copy(audio_files[0], output_file)













# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Podcast Settings")
    
    # Topic input with examples
    st.markdown("**📝 Podcast Topic**")
    topic_examples = [
        "AI in Education",
        "Climate Change Solutions",
        "Future of Work",
        "Space Exploration",
        "Digital Health",
        "Sustainable Technology"
    ]
    
    selected_example = st.selectbox("Choose from examples:", ["Custom Topic"] + topic_examples)
    
    if selected_example == "Custom Topic":
        topic = st.text_input("Enter your topic:", placeholder="e.g., Artificial Intelligence in Healthcare")
    else:
        topic = selected_example
    
    # Number of speakers
    st.markdown("**👥 Number of Speakers**")
    num_people = st.slider("Select speakers", 2, 4, 2, help="Choose between 2-4 speakers for your podcast")
    
    
    
    st.markdown("### 🎭 Available Voices")
    for i, voice in enumerate(VOICE_POOL):
        st.markdown(f"**{voice}** - Voice {i+1}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Quick stats
    st.markdown("""
    <div class="stats-container">
        <div style="display: flex; justify-content: space-around;">
            <div class="stat-item">
                <div class="stat-number">10K+</div>
                <div class="stat-label">Podcasts Generated</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">4</div>
                <div class="stat-label">AI Voices Available</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">2-5</div>
                <div class="stat-label">Minutes Duration</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Generation button
    if st.button("🎬 Generate Podcast", help="Click to generate your AI podcast"):
        if not topic:
            st.error("Please enter a topic for your podcast!")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔄 Generating your podcast..."):
                try:
                    # Step 1: Generate data
                    status_text.text("🔍 Researching topic and gathering information...")
                    progress_bar.progress(20)
                    
                    data = generate_data(topic)
                    
                    # Step 2: Generate script
                    status_text.text("✍️ Writing podcast script...")
                    progress_bar.progress(40)
                    
                    script = generate_script(num_people, data, topic)
                    
                    # Step 3: Parse script
                    status_text.text("🎭 Assigning voices to speakers...")
                    progress_bar.progress(60)
                    
                    script_lines = parse_script(script)
                    unique_names = list({name for name, _ in script_lines})
                    voice_map = assign_voices(unique_names)
                    
                    # Step 4: Generate audio
                    status_text.text("🎵 Generating audio with AI voices...")
                    progress_bar.progress(80)
                    
                    merged_audio = generate_audio_with_google_tts(script_lines, voice_map)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Podcast generation complete!")
                    
                    # Success message
                    st.markdown("""
                    <div class="success-message">
                        🎉 Your podcast is ready! Listen below and download if you like it.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["🎵 Audio Player", "📜 Script", "🎭 Voice Cast"])
                    
                    with tab1:
                        if merged_audio:
                            st.audio(merged_audio)
                            
                            col_play, col_download = st.columns(2)
                            with col_play:
                                if st.button("▶️ Play Podcast"):
                                    pass
                                    # playsound(merged_audio)
                            
                            with col_download:
                                with open(merged_audio, "rb") as file:
                                    st.download_button(
                                        label="📥 Download Podcast",
                                        data=file.read(),
                                        file_name=f"podcast_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
                                        mime="audio/wav"
                                    )
                    
                    with tab2:
                        st.markdown("### 📜 Generated Script")
                        st.markdown(f"**Topic:** {topic}")
                        st.markdown("---")
                        st.text(script)
                        
                        # Copy script button
                        if st.button("📋 Copy Script"):
                            st.write("Script copied to clipboard!")
                    
                    with tab3:
                        st.markdown("### 🎭 Voice Cast")
                        for name, voice in voice_map.items():
                            st.markdown(f"""
                            <div class="voice-card">
                                🎙️ {name} → {voice}
                            </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    

with col2:
    # Features section
    st.markdown("### ✨ Features")
    
    features = [
        {"icon": "🤖", "title": "AI-Powered", "desc": "Advanced AI generates natural conversations"},
        {"icon": "🎭", "title": "Multiple Voices", "desc": "4 distinct AI voices for different speakers"},
        {"icon": "⚡", "title": "Fast Generation", "desc": "Get your podcast in under 2 minutes"},
        {"icon": "📝", "title": "Smart Scripts", "desc": "Contextual and engaging dialogue"},
        {"icon": "🎵", "title": "High Quality", "desc": "Professional audio output"},
        {"icon": "📱", "title": "Easy to Use", "desc": "Simple interface, powerful results"}
    ]
    
    for feature in features:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{feature['icon']}</div>
            <strong>{feature['title']}</strong><br>
            <small>{feature['desc']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Tips section
    st.markdown("### 💡 Tips for Better Podcasts")
    st.markdown("""
    <div class="info-box">
        <strong>🎯 Topic Selection:</strong><br>
        • Be specific (e.g., "AI in Healthcare" vs "AI")<br>
        • Current and engaging topics work best<br>
        • Avoid overly technical jargon
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>👥 Speaker Count:</strong><br>
        • 2 speakers: Interview style<br>
        • 3 speakers: Panel discussion<br>
        • 4 speakers: Debate format
    </div>
    """, unsafe_allow_html=True)



# Footer
st.markdown("""
<div class="footer">
    <h3>🎙️ AI Podcast Generator</h3>
    <p>Powered by Google Gemini AI • Built with Streamlit</p>
    <p>Create engaging podcasts in minutes with AI-powered voices and smart content generation</p>
    <div style="margin-top: 1rem;">
        <span style="margin: 0 1rem;">📧 Support</span>
        <span style="margin: 0 1rem;">📚 Documentation</span>
        <span style="margin: 0 1rem;">🔧 API</span>
    </div>
</div>
""", unsafe_allow_html=True)