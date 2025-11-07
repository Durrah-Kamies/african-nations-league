# email_service.py
# Handles email notifications for match completion
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_match_completion_email(match_data, result, db):
    """
    Send email notification to federations when a match is completed.
    
    Args:
        match_data: Dictionary containing match information (teams, round, etc.)
        result: Dictionary containing match result (goals, scorers, winner, etc.)
        db: Firestore database client to fetch team emails
    """
    try:
        # Email configuration from environment variables
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        # Skip if email not configured
        if not sender_email or not sender_password:
            print("⚠️  Email not configured. Skipping notification.")
            return False
        
        # Extract match information
        team1 = match_data.get('team1', {})
        team2 = match_data.get('team2', {})
        round_name = match_data.get('round', 'Match').capitalize()
        
        team1_name = team1.get('country', 'Team 1')
        team2_name = team2.get('country', 'Team 2')
        team1_goals = result.get('team1_goals', 0)
        team2_goals = result.get('team2_goals', 0)
        winner = result.get('winner', 'TBD')
        goal_scorers = result.get('goal_scorers', [])
        
        # Get federation emails from Firebase (teams that played in this match)
        federation_emails = []
        team1_email = team1.get('email')
        team2_email = team2.get('email')
        
        if team1_email:
            federation_emails.append(team1_email)
        if team2_email:
            federation_emails.append(team2_email)
        
        if not federation_emails:
            print("⚠️  No federation emails found for the teams. Skipping notification.")
            return False
        
        # Build scoreline text
        scoreline = f"{team1_name} {team1_goals} - {team2_goals} {team2_name}"
        
        # Build goal scorers text
        scorers_text = ""
        if goal_scorers:
            scorers_text = "\n\nGoal Scorers:\n"
            for scorer in goal_scorers:
                scorers_text += f"  • {scorer.get('player', 'Unknown')} ({scorer.get('team', 'Unknown')}) - {scorer.get('minute', '?')}'\n"
        
        # Penalty shootout info if applicable
        penalty_info = ""
        if result.get('decided_by') == 'penalties':
            penalty_score = result.get('penalty_score', {})
            penalty_info = f"\n\nDecided by penalties: {penalty_score.get('team1', 0)} - {penalty_score.get('team2', 0)}"
        
        # Create email content
        subject = f"Match Result: {team1_name} vs {team2_name} - {round_name}"
        
        body = f"""
African Nations League - Match Completion Notification

Round: {round_name}
Match: {scoreline}
Winner: {winner}
{penalty_info}
{scorers_text}

This is an automated notification from the African Nations League system.
"""
        
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(federation_emails)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        # Send email using Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print(f"✅ Match completion email sent to federations: {scoreline}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending match completion email: {e}")
        return False
