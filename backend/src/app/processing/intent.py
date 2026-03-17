import os
import pickle
import nltk
from enum import Enum
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

class IntentTypes(Enum):
    AP = "ACCOUNTS_PAYABLE"     # Incoming Invoices to pay
    AR = "ACCOUNTS_RECEIVABLE"  # Payments received from our clients
    RECEIPT = "RECEIPT"         # Payment confirmations/Receipts
    NON_FINANCIAL = "NON_FINANCIAL" # Spam, standard talk, newsletters

class EmailIntentClassifier:
    """
    Lightweight NLP Engine to classify the context/intent of an email body
    to determine if the attachments should hit the OCR pipeline.
    """
    def __init__(self, model_path: str = "/tmp/intent_classifier.pkl"):
        self.model_path = model_path
        self.pipeline: Optional[Pipeline] = None
        
        # Download NLTK tokenizers if needed (usually handled in a setup script)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        self._load_or_init_model()

    def _load_or_init_model(self):
        """Loads a pre-trained SVM model or initializes a blank one."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                print("Email Intent Classifier Model loaded successfully.")
            except Exception as e:
                print(f"Error loading intent model: {e}")
                self.pipeline = self._create_blank_pipeline()
        else:
            self.pipeline = self._create_blank_pipeline()

    def _create_blank_pipeline(self) -> Pipeline:
        # A simple TF-IDF and Support Vector Classifier
        return Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
            ('clf', SVC(kernel='linear', probability=True))
        ])

    def tokenize_email_body(self, raw_text: str) -> str:
        """
        Cleans and tokenizes email body into a normalized string for the model.
        Removes heavy signatures, URLs, and artifacts.
        """
        # Lowercase
        text = raw_text.lower()
        # Basic NLTK tokenization
        tokens = nltk.word_tokenize(text)
        
        # We could apply lemmatization or stemming here
        # For lightweight implementation, alpha-num words only
        clean_tokens = [word for word in tokens if word.isalnum()]
        
        return " ".join(clean_tokens)

    def train_model(self, training_texts: List[str], labels: List[str]):
        """
        Trains the TF-IDF SVC model.
        Used primarily via a separate administrative script when dataset grows.
        """
        clean_texts = [self.tokenize_email_body(text) for text in training_texts]
        self.pipeline.fit(clean_texts, labels)
        
        # Save weights
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print("Intent Model trained and saved.")

    def predict_intent(self, email_body: str) -> IntentTypes:
        """
        Predicts if an email is AP, AR, Receipt, or Non-Financial.
        If the model isn't trained (blank Exception), uses a Zero-Shot heuristic fallback.
        """
        clean_text = self.tokenize_email_body(email_body)
        
        try:
            # Check if model has been fitted. 
            # sklearn pipelines raise NotFittedError if .predict() is called before .fit()
            # Since we can't easily catch NotFittedError without importing it, we'll try/except
            prediction = self.pipeline.predict([clean_text])[0]
            
            # Map string back to Enum
            for intent in IntentTypes:
                if intent.value == prediction:
                    return intent
            return IntentTypes.NON_FINANCIAL
            
        except Exception:
            # Heuristic Zero-Shot Fallback if model hasn't been trained yet
            return self._heuristic_fallback(clean_text)

    def _heuristic_fallback(self, clean_text: str) -> IntentTypes:
        """Heuristic rules to act as a zero-shot classifier until ML dataset is robust."""
        text = clean_text.lower()
        
        if any(kw in text for kw in ["invoice", "fatura", "cobrança", "boleto", "due", "payment required"]):
            return IntentTypes.AP
        elif any(kw in text for kw in ["comprovante", "receipt", "paid", "pago", "confirmation", "payment received"]):
            return IntentTypes.RECEIPT
        elif any(kw in text for kw in ["remittance", "pagamento enviado"]):
            return IntentTypes.AR
            
        # Standard spam/newsletter fallback
        return IntentTypes.NON_FINANCIAL
