import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import CandidateScreeningBot

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Candidate Screening Bot", 
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "bot" not in st.session_state:
        st.session_state.bot = CandidateScreeningBot()
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "greeting"
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = {}
    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = True

def display_chat_interface():
    st.title("🤖 AI Candidate Screening Assistant")
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Initial greeting
    if len(st.session_state.messages) == 0:
        greeting = st.session_state.bot.get_greeting_message()
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(greeting)
        st.session_state.current_stage = "collect_name"
    
    # Chat input
    if st.session_state.conversation_active and st.session_state.current_stage != "conclusion":
        user_input = st.chat_input("Type your response here...")
        
        if user_input:
            # Display user message
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Process bot response
            with st.spinner("Processing..."):
                response, next_stage = st.session_state.bot.process_stage(
                    st.session_state.current_stage, 
                    user_input, 
                    st.session_state.candidate_data
                )
            
            # Display bot response
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Update stage
            st.session_state.current_stage = next_stage
            
            # End conversation if concluded
            if next_stage == "conclusion":
                st.session_state.conversation_active = False
                st.balloons()
    
    # Restart button
    if not st.session_state.conversation_active:
        if st.button("🔄 Start New Screening", type="primary"):
            # Reset session state
            for key in ["messages", "current_stage", "candidate_data", "conversation_active"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def display_sidebar():
    with st.sidebar:
        st.header("📋 Screening Progress")
        
        # Progress tracking
        stages_completed = {
            "greeting": "✅ Welcome",
            "collect_name": "📝 Name" + (" ✅" if "name" in st.session_state.candidate_data else ""),
            "collect_email": "📧 Email" + (" ✅" if "email" in st.session_state.candidate_data else ""),
            "collect_phone": "📱 Phone" + (" ✅" if "phone" in st.session_state.candidate_data else ""),
            "collect_experience": "💼 Experience" + (" ✅" if "experience" in st.session_state.candidate_data else ""),
            "collect_position": "🎯 Position" + (" ✅" if "position" in st.session_state.candidate_data else ""),
            "collect_location": "📍 Location" + (" ✅" if "location" in st.session_state.candidate_data else ""),
            "collect_tech_stack": "💻 Tech Stack" + (" ✅" if "tech_stack" in st.session_state.candidate_data else ""),
            "technical_questions": "❓ Questions" + (" ✅" if "questions" in st.session_state.candidate_data else ""),
            "conclusion": "🎉 Complete"
        }
        
        for stage, label in stages_completed.items():
            st.markdown(f"- {label}")
        
        st.markdown("---")
        
        # Current data preview
        if st.session_state.candidate_data:
            st.subheader("📊 Collected Information")
            for key, value in st.session_state.candidate_data.items():
                if key != "questions":
                    if isinstance(value, list):
                        st.text(f"{key.title()}: {', '.join(value)}")
                    else:
                        st.text(f"{key.title()}: {value}")
        
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Be specific with your tech stack")
        st.markdown("- Type 'exit' to quit anytime")
        st.markdown("- All information is processed securely")

def main():
    # Check for API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        st.error("⚠️ Perplexity API Key not found. Please set PERPLEXITY_API_KEY in your environment variables.")
        st.stop()
    
    # Initialize session state
    initialize_session_state()
    
    # Create layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        display_chat_interface()
    
    with col2:
        display_sidebar()

if __name__ == "__main__":
    main()
