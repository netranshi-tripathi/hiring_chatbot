# AI Candidate Screening Chatbot 🤖

## Project Overview
The AI Candidate Screening Chatbot is an automated tool designed to streamline the initial candidate screening process for technical roles. Built with Streamlit, it engages candidates in a conversational interface to collect personal and professional details, validate inputs in real-time, and generate tailored technical assessment questions using AI. The chatbot leverages the Perplexity API (via OpenAI client) to create relevant questions based on the candidate's declared tech stack, ensuring a consistent, efficient, and engaging screening experience. This reduces manual effort for interviewers while providing a standardized evaluation framework.

## Features
- **Information Collection:** Gathers and validates candidate details including name, email, phone, years of experience, desired position, location, and tech stack.
- **Tech Stack Assessment:** Dynamically generates 5 technical questions per session, categorized to assess core concepts, frameworks, databases, problem-solving, and real-world applications.
- **Smart Validation:** Uses regex and libraries for real-time validation of emails, phones, names, and experience levels.
- **Conversation Management:** Guides users through stages with context-aware responses, supports early exit via keywords like 'exit' or 'quit', and handles unexpected inputs gracefully.
- **Summary & Next Steps:** Provides a comprehensive summary upon completion and outlines follow-up steps.
- **Fallback Mechanisms:** Includes generic questions if the API fails, ensuring the process continues smoothly.

## Installation Instructions

1. **Prerequisites**
 - Ensure Python 3.11.11 is installed (as specified in [runtime.txt](runtime.txt)).
 - Obtain a Perplexity API key from their platform.

2. **Clone the Repository**
 ```sh
 git clone https://github.com/netranshi-tripathi/hiring_chatbot.git
 cd hiring_chatbot
 ```

3. **Set Up Virtual Environment (Recommended)**
 ```sh
 python3 -m venv venv
 source venv/bin/activate # On Windows: venv\Scripts\activate
 ```

4. **Install Dependencies**
 ```sh
 pip install -r requirements.txt
 ```
 Key libraries include Streamlit for the UI, OpenAI for API integration, and email-validator for input checks (see [`requirements.txt`](requirements.txt ) for full list).

5. **Configure Environment Variables**
 - Create a `.env` file in the project root.
 - Add your API key:
 ```
 PERPLEXITY_API_KEY=your_api_key_here
 ```
 - The app loads this via `python-dotenv`.

6. **Run the Application**
 ```sh
 streamlit run [`app.py`](app.py )
 ```
 - Open the provided local URL in your browser to start the chatbot.

## Usage Guide

- **Starting the Chat:** Launch the app via Streamlit. The chatbot begins with a greeting and prompts for your name.
- **Navigation:** Respond to each prompt sequentially. The sidebar tracks progress and displays collected data.
- **Tech Stack Input:** When prompted, list skills (e.g., "Python, React, MySQL"). The bot parses and categorizes them for question generation.
- **Technical Questions:** After info collection, the bot generates and displays 5 questions. Type 'more' for additional questions or 'finish' to conclude.
- **Exiting:** Type 'exit', 'quit', or similar keywords at any stage to end early.
- **Restarting:** Use the "Start New Screening" button after completion to reset.
- **Tips:** Be specific with tech stack for better questions; all data is handled in-session (no persistent storage).

## Technical Details

- **Libraries Used:**
 - `streamlit` (UI framework for chat interface and layout).
 - `openai` (client for Perplexity API calls).
 - `python-dotenv` (environment variable loading).
 - `requests` (HTTP handling, though primarily used via OpenAI).
 - `pandas` (data manipulation, for potential future extensibility).
 - `email-validator` (email validation).
 - `re` (regex for phone, name, and question parsing).
 - `tiktoken` (token counting, if needed for API limits).

- **Model Details:**
 - Utilizes Perplexity's `llama-3.1-sonar-large-128k-online` model for generating technical questions.
 - API calls are made via OpenAI client configured with Perplexity's base URL.
 - Fallback to generic questions if API fails (handled in [`TechnicalQuestionGenerator`](chatbot.py)).

- **Architecture:**
 - **Modular Structure:** Code is split into files for separation of concerns:
 - [app.py](app.py): Main Streamlit app, handles UI, session state, and layout.
 - [chatbot.py](chatbot.py): Core logic for conversation stages, validation, and question generation (includes [`CandidateScreeningBot`](chatbot.py) and [`TechnicalQuestionGenerator`](chatbot.py)).
 - [data_validator.py](data_validator.py): Input validation functions (e.g., [`DataValidator.validate_email`](data_validator.py)).
 - [question_generator.py](question_generator.py): Duplicate question generation logic (note: primarily used via [chatbot.py](chatbot.py); consider consolidating for maintainability).
 - **Session Management:** Uses Streamlit's session state for conversation flow, messages, and data persistence during the session.
 - **Error Handling:** API exceptions trigger fallbacks; invalid inputs prompt re-entry.
 - **Security:** API key loaded from environment; no data stored beyond session.

## Prompt Design

- **System and User Prompts:** Crafted to position the AI as an expert interviewer. System prompts set context (e.g., "You are a technical interviewer creating relevant assessment questions."). User prompts specify tech stack and request exactly 5 numbered questions covering key areas: core language concepts, frameworks, databases, algorithms, and scenarios.
- **Formatting Requirements:** Prompts enforce numbered lists for easy parsing via regex in [`_parse_questions`](chatbot.py).
- **Information Gathering:** Prompts are concise, stage-specific, and include validation feedback to guide users smoothly.
- **Enhancements:** Partial matching in tech stack parsing (via [`_parse_tech_stack`](chatbot.py)) ensures flexibility for varied inputs, improving question relevance.

## Challenges & Solutions

- **API Reliability and Errors:** The Perplexity API may fail due to rate limits or connectivity. Solution: Implemented robust fallback logic in [`_fallback_questions`](chatbot.py) to provide generic, relevant questions, ensuring the screening continues without interruption.
- **Input Validation and User Errors:** Handling diverse formats for emails, phones, and names. Solution: Used regex patterns in [`DataValidator`](data_validator.py) for strict checks, with clear error messages prompting corrections.
- **Tech Stack Parsing:** Users enter skills in varied ways (e.g., abbreviations). Solution: Categorized matching against predefined lists in [`tech_categories`](chatbot.py), with partial matching and title casing for standardization.
- **Conversation Flow Management:** Maintaining state across stages in a stateless web app. Solution: Leveraged Streamlit session state for tracking stages, messages, and data, enabling seamless transitions and restarts.
- **Prompt Engineering for Relevance:** Initial questions were too generic. Solution: Iteratively refined prompts to include specific categories and tech stack integration, resulting in more targeted assessments.
- **Code Duplication:** [`TechnicalQuestionGenerator`](question_generator.py) mirrors logic in [chatbot.py](chatbot.py). Solution: Recommend refactoring to import from a single module for better maintainability.

---
