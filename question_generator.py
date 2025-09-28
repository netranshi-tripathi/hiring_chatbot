from perplexity import Perplexity
import os
from dotenv import load_dotenv

load_dotenv()

class TechnicalQuestionGenerator:
    def __init__(self):
        self.client = Perplexity()
    
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
                model="sonar-reasoning",
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
