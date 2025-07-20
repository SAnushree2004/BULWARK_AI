import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import os
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class EnhancedCyberbullyingDetector:
    def __init__(self, model_path, tokenizer_path, model_info_path, threshold=0.3):
        # Load the model
        self.model = tf.keras.models.load_model(model_path)
        
        # Load the tokenizer
        with open(tokenizer_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)
        
        # Load model parameters
        with open(model_info_path, 'rb') as handle:
            model_info = pickle.load(handle)
            self.max_words = model_info['max_words']
            self.max_length = model_info['max_length']
        
        # Set threshold
        self.threshold = threshold
        
        # Define bullying keywords that will boost the score
        self.severe_bullying_phrases = [
            "kill yourself", "die", "commit suicide", "kys", 
            "worthless", "ugly", "stupid", "idiot", "hate you", 
            "pathetic", "retard", "moron", "loser", "trash"
        ]
    
    def clean_text(self, text):
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove non-alphanumeric characters
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def predict_score(self, text):
        # Save original text for rule-based checks
        original_text = text.lower()
        
        # Clean the text for model prediction
        cleaned_text = self.clean_text(text)
        
        # Get model prediction
        sequences = self.tokenizer.texts_to_sequences([cleaned_text])
        padded = pad_sequences(sequences, maxlen=self.max_length, padding='post')
        base_score = float(self.model.predict(padded, verbose=0)[0][0])
        
        # Apply rule-based adjustments
        final_score = base_score
        
        # Check for severe bullying phrases
        for phrase in self.severe_bullying_phrases:
            if phrase in original_text or phrase in cleaned_text:
                # Boost the score, but ensure it doesn't exceed 1.0
                final_score = min(0.95, base_score + 0.1)
                break
                
        # Check for directed attacks (you are/you're + negative term)
        if ("you are" in original_text or "you're" in original_text) and any(term in original_text for term in ["stupid", "ugly", "idiot", "worthless", "pathetic"]):
            final_score = min(0.95, final_score + 0.2)
        
        return final_score
    
    def predict_label(self, text):
        score = self.predict_score(text)
        return 1 if score > self.threshold else 0

    def evaluate_performance(self, test_data):
        """
        Evaluate the detector's performance on labeled test data
        
        Args:
            test_data: list of dicts with 'text' and 'label' keys
                       where label is 1 for bullying, 0 for non-bullying
        
        Returns:
            dict with accuracy, precision, recall, f1 score, and confusion matrix
        """
        y_true = []
        y_pred = []
        scores = []
        
        # Generate predictions
        for item in test_data:
            score = self.predict_score(item['text'])
            predicted_label = 1 if score > self.threshold else 0
            
            y_true.append(item['label'])
            y_pred.append(predicted_label)
            scores.append(score)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)
        
        # Return metrics as dictionary
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm,
            'scores': scores
        }

def get_content_scores(text, cyberbullying_detector):
    try:
        # Get score from the enhanced detector
        score = cyberbullying_detector.predict_score(text)
        
        # Return a dictionary with just the average_score
        return {
            'average_score': score
        }
    except Exception as e:
        print(f"Error getting content score: {str(e)}")
        return {
            'average_score': 0.0
        }

def evaluate_model():
    """
    Function to evaluate the model and print performance metrics
    """
    model_path = "cyberbullying_model.h5"
    tokenizer_path = "cyberbullying_tokenizer.pickle"
    model_info_path = "cyberbullying_model_info.pickle"
    
    # Check if files exist
    for file_path in [model_path, tokenizer_path, model_info_path]:
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found")
            return
    
    # Create detector with desired threshold
    detector = EnhancedCyberbullyingDetector(model_path, tokenizer_path, model_info_path, threshold=0.3)
    
    # Create test dataset with ground truth labels
    test_data = [
        # Positive examples (non-bullying)
        {"text": "You're such a wonderful person, thank you for your help!", "label": 0},
        {"text": "I really appreciate your thoughtful feedback on my work.", "label": 0},
        {"text": "The weather is beautiful today, perfect for a walk!", "label": 0},
        {"text": "Congratulations on your achievement, well deserved!", "label": 0},
        {"text": "I'm so happy to hear about your promotion, great job!", "label": 0},
        {"text": "I disagree with your opinion but respect your perspective.", "label": 0},
        {"text": "Have a great day, looking forward to your next post.", "label": 0},
        {"text": "Thank you for sharing this interesting information.", "label": 0},
        {"text": "It was nice meeting you yesterday.", "label": 0},
        {"text": "This content is informative and well-presented.", "label": 0},
        
        # Negative examples (bullying)
        {"text": "You are so stupid and ugly, nobody likes you.", "label": 1},
        {"text": "Kill yourself you worthless piece of garbage.", "label": 1},
        {"text": "You're a complete idiot who knows nothing.", "label": 1},
        {"text": "Your content is absolute trash, just like you.", "label": 1},
        {"text": "You should just disappear, everyone hates you.", "label": 1},
        {"text": "Go die in a hole, no one would miss you.", "label": 1},
        {"text": "You're pathetic and will never amount to anything.", "label": 1},
        {"text": "What a loser, can't believe how dumb you are.", "label": 1},
        {"text": "Shut up you moron, nobody cares what you think.", "label": 1},
        {"text": "You're the most annoying person ever, just go away.", "label": 1}
    ]
    
    # Evaluate model on test data
    print("Evaluating cyberbullying detection model...")
    results = detector.evaluate_performance(test_data)
    
    # Print performance metrics
    print("\nPerformance Metrics:")
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall: {results['recall']:.4f}")
    print(f"F1 Score: {results['f1_score']:.4f}")
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    print(results['confusion_matrix'])
    print("\n[True Negatives, False Positives]")
    print("[False Negatives, True Positives]")
    
    # Print detailed results
    print("\nDetailed Results:\n")
    print(f"{'Text':<60} {'Actual':<10} {'Predicted':<10} {'Score':<10}")
    print("-" * 90)
    
    for i, item in enumerate(test_data):
        actual = "BULLYING" if item["label"] == 1 else "NOT BULLYING"
        score = results["scores"][i]
        predicted = "BULLYING" if score > detector.threshold else "NOT BULLYING"
        
        # Truncate text if too long
        text = item["text"]
        if len(text) > 55:
            text = text[:55] + "..."
        
        print(f"{text:<60} {actual:<10} {predicted:<10} {score:.4f}")
    
    return results

def test_detector():
    model_path = "cyberbullying_model.h5"
    tokenizer_path = "cyberbullying_tokenizer.pickle"
    model_info_path = "cyberbullying_model_info.pickle"
    
    # Create detector with lower threshold
    detector = EnhancedCyberbullyingDetector(model_path, tokenizer_path, model_info_path, threshold=0.3)
    
    # Test examples with expected bullying detection
    test_examples = [
        # Should be classified as NOT bullying
        "You're such a wonderful person, thank you for your help!",
        "I really appreciate your thoughtful feedback on my work.",
        "The weather is beautiful today, perfect for a walk!",
        
        # Should be classified as bullying
        "You are so stupid and ugly, nobody likes you.",
        "Kill yourself you worthless piece of garbage.",
        "You're a complete idiot who knows nothing.",
        "Your content is absolute trash, just like you.",
        "You should just disappear, everyone hates you."
    ]
    
    print("\nTesting Enhanced Cyberbullying Detector (Threshold: 0.3)")
    print("=" * 60)
    
    for text in test_examples:
        score = detector.predict_score(text)
        label = "BULLYING" if score > detector.threshold else "NOT BULLYING"
        
        print(f"Text: {text}")
        print(f"Score: {score:.4f}")
        print(f"Classification: {label}")
        print("-" * 60)

if __name__ == "__main__":
    # Run the evaluation to get metrics
    results = evaluate_model()
    
    # Run the sample test function
    test_detector()
    
    # Allow interactive testing
    print("\nEnter your own text to test (or type 'exit' to quit):")
    
    model_path = "cyberbullying_model.h5"
    tokenizer_path = "cyberbullying_tokenizer.pickle"
    model_info_path = "cyberbullying_model_info.pickle"
    
    if all(os.path.exists(p) for p in [model_path, tokenizer_path, model_info_path]):
        detector = EnhancedCyberbullyingDetector(model_path, tokenizer_path, model_info_path, threshold=0.2)
        
        while True:
            user_text = input("> ")
            if user_text.lower() == 'exit':
                break
            
            score = detector.predict_score(user_text)
            label = "BULLYING" if score > detector.threshold else "NOT BULLYING"
            
            print(f"Score: {score:.4f}")
            print(f"Classification: {label}")
    else:
        print("Model files not found. Cannot run interactive testing.")