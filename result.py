import streamlit as st
import google.generativeai as genai
from google import genai as google_genai
from google.genai import types
import wave
import os
import re
import dotenv
from playsound import playsound
dotenv.load_dotenv()


# Streamlit UI - Title
st.title("🎙️ AI Podcast Generator")

# Set API key directly
gemini_key = os.getenv("gemini_key")
genai.configure(api_key=gemini_key)
google_genai_client = google_genai.Client(api_key=gemini_key)

    # Constants - Google AI Studio voice options
VOICE_POOL = ["Kore", "Puck", "Sage", "Coral"]
 
    # Functions
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

def generate_data(topic):
        prompt = f"I have to create podcast on topic: {topic}. Go through internet sources and give large informative paragraphs with references."
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        return response.text.strip()

def generate_script(num_people, data, topic):
        prompt = f"""You are pro podcast writer. Write humanised dialogue on topic: {topic}, based on data: {data}.
Total speakers = {num_people}. Length: 2-5 min.
Return in this format:
Person 1 : <line>
Person 2 : <line>
Person 3 : <line>...

Example:
Anya Sharma : Welcome to AI in EdTech! I'm your host Anya, and joining me is Mr. Ben Carter.
Ben Carter : Thanks Anya! Happy to be here.
Only return script.
"""
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
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
            voice = voice_map.get(name, "Kore")
            
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

    # Main App Inputs
topic = st.text_input("🎯 Enter podcast topic:", "AI in Education")
num_people = st.slider("👥 Number of speakers", 2, 4, 2)

if st.button("🎬 Generate Podcast"):
        with st.spinner("🔄 Generating script and audio..."):
            try:
                data = generate_data(topic)
                script = generate_script(num_people, data, topic)
                st.subheader("📜 Generated Script")
                st.text(script)

                script_lines = parse_script(script)
                unique_names = list({name for name, _ in script_lines})
                voice_map = assign_voices(unique_names)
                
                # Display voice assignments
                st.subheader("🎭 Voice Assignments")
                for name, voice in voice_map.items():
                    st.info(f"{name} → {voice}")

                st.info("🔊 Generating voice audio...")
                merged_audio = generate_audio_with_google_tts(script_lines, voice_map)

                if merged_audio:
                    st.success("✅ Podcast Ready!")
                    st.audio(merged_audio)

                    if st.button("▶️ Play Podcast"):
                        playsound(merged_audio)

            except Exception as e:
                st.error(f"Something went wrong: {e}")


                