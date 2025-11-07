# config.py
# NOTE: Centralized setup for Firebase (Firestore) and Gemini (Google Generative AI).
# The functions here return ready-to-use clients/models for the rest of the app.
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_firebase():
    """Create and return a Firestore client.
    Tries multiple credential sources so the app can run locally or in prod.
    """
    try:
        # Check if Firebase is already initialized
        if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
            print(" Firebase already initialized")
            return firestore.client()
        
        cred = None
        
        # Method 1: Try to load from serviceAccountKey.json
        # Easiest for local dev: drop the JSON file in project root.
        service_account_paths = [
            "serviceAccountKey.json",
            "./serviceAccountKey.json",
            "../serviceAccountKey.json"
        ]
        
        for path in service_account_paths:
            if os.path.exists(path):
                try:
                    cred = credentials.Certificate(path)
                    print(f" Loaded Firebase credentials from: {path}")
                    break
                except Exception as e:
                    print(f" Error loading {path}: {e}")
                    continue
        
        # Method 2: Try environment variable with JSON string
        # Useful in platforms where storing files is tricky.
        if not cred:
            firebase_config_json = os.environ.get('FIREBASE_CONFIG_JSON')
            if firebase_config_json:
                try:
                    # Write the JSON to a temporary file
                    config_data = json.loads(firebase_config_json)
                    with open('temp_service_account.json', 'w') as f:
                        json.dump(config_data, f)
                    cred = credentials.Certificate('temp_service_account.json')
                    print(" Loaded Firebase credentials from environment variable")
                except Exception as e:
                    print(f" Error loading from environment: {e}")
        
        # Method 3: Try individual environment variables
        # Last resort: assemble a service account dict from separate env vars.
        if not cred:
            try:
                project_id = os.environ.get('FIREBASE_PROJECT_ID')
                private_key = os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
                client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')
                private_key_id = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
                client_id = os.environ.get('FIREBASE_CLIENT_ID')
                
                if project_id and private_key and client_email:
                    service_account_info = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key_id": private_key_id,
                        "private_key": private_key,
                        "client_email": client_email,
                        "client_id": client_id,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
                        "universe_domain": "googleapis.com"
                    }
                    
                    # Write to temporary file
                    with open('temp_service_account.json', 'w') as f:
                        json.dump(service_account_info, f)
                    
                    cred = credentials.Certificate('temp_service_account.json')
                    print(" Loaded Firebase credentials from individual environment variables")
            except Exception as e:
                print(f" Error loading from individual env vars: {e}")
        
        if not cred:
            # Stop early with a helpful error if nothing worked.
            raise Exception("No valid Firebase credentials found. Please check your configuration.")
        
        # Initialize Firebase
        firebase_admin.initialize_app(cred)  # One-time global init for admin SDK
        print(" Firebase initialized successfully!")
        return firestore.client()
        
    except Exception as e:
        print(f" CRITICAL: Failed to initialize Firebase: {e}")
        print("\n TROUBLESHOOTING:")
        print("1. Download serviceAccountKey.json from Firebase Console")
        print("2. Place it in your project root folder")
        print("3. Make sure it's a valid JSON file")
        print("4. Check file permissions")
        raise e

def initialize_gemini():
    """Initialize Google Gemini AI
    Returns a GenerativeModel or None (fallback mode if no key).
    """
    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("  Warning: GEMINI_API_KEY not found in environment variables")
            print(" AI features will use fallback responses")
            return None
        
        genai.configure(api_key=api_key)  # Auth for Google Generative AI SDK
        
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        # Use a widely supported model name for v1beta and the SDK
        # and pass it with the correct parameter name.
        model = genai.GenerativeModel(
            model="gemini-1.0-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        print(" Gemini AI initialized successfully!")
        return model
        
    except Exception as e:
        print(f" Error initializing Gemini: {e}")
        return None