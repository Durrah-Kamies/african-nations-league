# test_firebase.py
# NOTE: Quick sanity check to verify Firebase credentials and Firestore access.
from config import initialize_firebase

try:
    db = initialize_firebase()  # Get Firestore client
    print(" Firebase connection successful!")
    
    # Test if we can access Firestore
    teams_ref = db.collection('teams')  # Simple read to confirm permissions
    teams = list(teams_ref.stream())
    print(f" Found {len(teams)} teams in database")
    
except Exception as e:
    print(f" Firebase test failed: {e}")