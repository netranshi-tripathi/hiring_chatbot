import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from data_validator import DataValidator

load_dotenv()

class TechnicalQuestionGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"
        )
    
    def generate_questions(self, tech_stack):
        """Generate 3-5 technical questions based on candidate's tech stack"""
        
        prompt = f"""
        You are an expert technical interviewer. Based on the candidate's tech stack: {', '.join(tech_stack)}, 
        generate exactly 5 technical interview questions that assess:
        
        1. Core programming concepts in their primary language
        2. Framework/library specific knowledge
        3. Database and data handling skills
        4. Problem-solving and algorithms
        5. Real-world application scenarios
        
        Format your response as a numbered list with clear, specific questions.
        Each question should be appropriate for assessing proficiency in the mentioned technologies.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online",
                messages=[
                    {"role": "system", "content": "You are a technical interviewer creating relevant assessment questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            questions = response.choices[0].message.content.strip()
            return self._parse_questions(questions)
            
        except Exception as e:
            print(f"API Error: {e}")
            return self._fallback_questions(tech_stack)
    
    def _parse_questions(self, questions_text):
        """Parse numbered questions from response"""
        lines = questions_text.split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.\s+', line):
                question = re.sub(r'^\d+\.\s+', '', line)
                questions.append(question)
        
        return questions[:5]  # Ensure max 5 questions
    
    def _fallback_questions(self, tech_stack):
        """Fallback questions when API fails"""
        base_questions = [
            f"Explain the key features and use cases of {tech_stack[0] if tech_stack else 'your primary technology'}.",
            "Describe a challenging project you've worked on and how you overcame technical obstacles.",
            "How do you approach debugging complex issues in your applications?",
            "What are the best practices you follow for code quality and maintainability?",
            "Explain how you would optimize the performance of a slow-running application."
        ]
        return base_questions


class CandidateScreeningBot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"
        )
        self.validator = DataValidator()
        self.question_generator = TechnicalQuestionGenerator()
        
        # Conversation stages
        self.stages = [
            "greeting",
            "collect_name",
            "collect_email", 
            "collect_phone",
            "collect_experience",
            "collect_position",
            "collect_location",
            "collect_tech_stack",
            "technical_questions",
            "conclusion"
        ]
        
        # Exit keywords
        self.exit_keywords = [
            "quit", "exit", "bye", "goodbye", "end", "stop", 
            "terminate", "close", "finish", "done"
        ]
        
        # Tech stack categories for better parsing
        self.tech_categories = {
            "Programming Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby", "swift", "kotlin"],
            "Frontend": ["react", "vue", "angular", "html", "css", "bootstrap", "tailwind"],
            "Backend": ["django", "flask", "fastapi", "express", "spring", "laravel", ".net"],
            "Databases": ["mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle"],
            "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git"],
            "AI/ML": ["tensorflow", "pytorch", "scikit-learn", "opencv", "pandas", "numpy"]
        }
    
    def check_exit_intent(self, user_input):
        """Check if user wants to exit conversation"""
        return any(keyword in user_input.lower() for keyword in self.exit_keywords)
    
    def get_greeting_message(self):
        """Initial greeting and overview"""
        return """
        🤖 **Welcome to AI Candidate Screening Assistant!**
        
        I'm here to help streamline your job application process. I'll be collecting some basic information about you and then conducting a brief technical assessment based on your skills.
        
        **What we'll cover:**
        ✅ Personal & Contact Information
        ✅ Professional Experience
        ✅ Technical Skills Assessment
        ✅ Tailored Technical Questions
        
        The entire process takes about 10-15 minutes. You can type 'exit' or 'quit' at any time to end the conversation.
        
        Let's get started! **What's your full name?**
        """
    
    def process_stage(self, stage, user_input, candidate_data):
        """Process each conversation stage"""
        
        if self.check_exit_intent(user_input):
            return self.get_goodbye_message(), "conclusion"
        
        if stage == "collect_name":
            if self.validator.validate_name(user_input):
                candidate_data["name"] = user_input.strip()
                return f"Nice to meet you, {candidate_data['name']}! **What's your email address?**", "collect_email"
            else:
                return "Please provide a valid full name (at least 2 characters, letters only).", "collect_name"
        
        elif stage == "collect_email":
            if self.validator.validate_email(user_input.strip()):
                candidate_data["email"] = user_input.strip()
                return "Great! **What's your phone number?**", "collect_phone"
            else:
                return "Please provide a valid email address.", "collect_email"
        
        elif stage == "collect_phone":
            if self.validator.validate_phone(user_input.strip()):
                candidate_data["phone"] = user_input.strip()
                return "Perfect! **How many years of professional experience do you have?** (Enter a number)", "collect_experience"
            else:
                return "Please provide a valid phone number.", "collect_phone"
        
        elif stage == "collect_experience":
            if self.validator.validate_experience(user_input.strip()):
                candidate_data["experience"] = float(user_input.strip())
                return "Thank you! **What position(s) are you interested in applying for?**", "collect_position"
            else:
                return "Please enter a valid number of years (0-50).", "collect_experience"
        
        elif stage == "collect_position":
            candidate_data["position"] = user_input.strip()
            return "Excellent! **What's your current location (City, State/Country)?**", "collect_location"
        
        elif stage == "collect_location":
            candidate_data["location"] = user_input.strip()
            return """
            **Now for the technical assessment part!**
            
            Please list your technical skills and tech stack. Include:
            • Programming languages
            • Frameworks and libraries  
            • Databases
            • Cloud platforms & tools
            • Any other relevant technologies
            

            """, "collect_tech_stack"
        
        elif stage == "collect_tech_stack":
            tech_stack = self._parse_tech_stack(user_input)
            candidate_data["tech_stack"] = tech_stack
            
            questions = self.question_generator.generate_questions(tech_stack)
            candidate_data["questions"] = questions
            
            response = f"""
            **Excellent! Based on your tech stack: {', '.join(tech_stack)}**
            
            I've generated {len(questions)} technical questions tailored to your skills. Here they are:
            
            """
            
            for i, question in enumerate(questions, 1):
                response += f"**{i}.** {question}\n\n"
            
            response += """
            These questions assess your proficiency in the technologies you've mentioned. 
            """
            
            return response, "technical_questions"
        
        elif stage == "technical_questions":
            user_response = user_input.lower().strip()
            if "more" in user_response:
                # Generate additional questions
                additional_questions = self.question_generator.generate_questions(candidate_data["tech_stack"])
                
                response = "**Here are 5 additional technical questions:**\n\n"
                for i, question in enumerate(additional_questions, 1):
                    response += f"**{i}.** {question}\n\n"
                
                response += "Ready to conclude? Type 'finish' when you're done."
                return response, "technical_questions"
            else:
                return self.get_conclusion_message(candidate_data), "conclusion"
        
        # Fallback for unexpected inputs
        return self.get_fallback_response(stage), stage
    
    def _parse_tech_stack(self, tech_input):
        """Parse and categorize technical skills from user input"""
        # Clean and split the input
        tech_items = [item.strip().lower() for item in re.split(r'[,;]', tech_input)]
        tech_items = [item for item in tech_items if len(item) > 1]
        
        # Match with known technologies
        matched_tech = []
        for item in tech_items:
            # Direct matching
            for category, techs in self.tech_categories.items():
                if item in techs:
                    matched_tech.append(item.title())
                    break
            else:
                # Partial matching for common variations
                matched_tech.append(item.title())
        
        return matched_tech[:10]  # Limit to 10 items
    
    def get_conclusion_message(self, candidate_data):
        """Final message with summary"""
        return f"""
        **🎉 Thank you, {candidate_data['name']}! Screening Complete!**
        
        **Here's a summary of your information:**
        • **Name:** {candidate_data['name']}
        • **Email:** {candidate_data['email']}
        • **Phone:** {candidate_data['phone']}
        • **Experience:** {candidate_data['experience']} years
        • **Position Interest:** {candidate_data['position']}
        • **Location:** {candidate_data['location']}
        • **Tech Stack:** {', '.join(candidate_data['tech_stack'])}
        
        **Next Steps:**
        1. Your information has been recorded for review
        2. Our technical team will evaluate your responses
        3. If selected, you'll receive an email within 3-5 business days
        4. The next step would be a detailed technical interview
        
        **Thank you for your time and interest in our company!** 
        
        Best of luck with your application! 🚀
        """
    
    def get_goodbye_message(self):
        """Message when user exits early"""
        return """
        **Thank you for your time!**
        
        If you'd like to complete the screening process later, please feel free to restart the conversation.
        
        Have a great day! 👋
        """
    
    def get_fallback_response(self, current_stage):
        """Handle unexpected inputs"""
        stage_prompts = {
            "collect_name": "I didn't quite catch that. Could you please provide your full name?",
            "collect_email": "Please provide a valid email address.",
            "collect_phone": "I need a valid phone number. Please try again.",
            "collect_experience": "Please enter your years of experience as a number (e.g., 2, 5.5, 0).",
            "collect_position": "What position or role are you interested in applying for?",
            "collect_location": "Please share your current location (City, State/Country).",
            "collect_tech_stack": "Please list your technical skills separated by commas.",
            "technical_questions": "Type 'more' for additional questions or 'finish' to conclude.",
        }
        
        return stage_prompts.get(current_stage, "I didn't understand that. Could you please try again?")
