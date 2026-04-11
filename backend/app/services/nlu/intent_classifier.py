from transformers import pipeline

class IntentClassifier:
    def __init__(self):
        print("Loading AI Model for Intent Classification... (This takes a moment on startup)")
        # We use a lightweight model to keep things fast
        self.classifier = pipeline(
            "zero-shot-classification", 
            model="cross-encoder/nli-distilroberta-base"
        )
        
        # The categories your University Assistant should understand
        self.categories = [
            "exam_schedule", 
            "course_information", 
            "university_policy", 
            "department_events",
            "general_greeting"
        ]

    def classify(self, text: str):
        # Ask the AI to classify the user's text into one of our categories
        result = self.classifier(text, self.categories)
        
        # Get the top matching category and its confidence score
        top_intent = result['labels'][0]
        confidence_score = result['scores'][0]
        
        return top_intent, confidence_score

# Create a single instance to be used across the app
nlu_classifier = IntentClassifier()