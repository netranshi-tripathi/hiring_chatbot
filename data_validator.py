import re

class DataValidator:
    @staticmethod
    def validate_email(email):
        """Simple email validation using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Simple phone validation - accepts various formats"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it has 10-15 digits (international phone numbers)
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_name(name):
        """Validate name - at least 2 characters, letters and spaces only"""
        name = name.strip()
        return len(name) >= 2 and re.match(r'^[a-zA-Z\s]+$', name)
    
    @staticmethod
    def validate_experience(experience):
        """Validate years of experience"""
        try:
            years = float(experience)
            return 0 <= years <= 50
        except:
            return False
