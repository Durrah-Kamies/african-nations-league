# ai_commentary.py
# NOTE: Wrapper around Gemini to generate football previews, live commentary,
# post-match analysis, and player analysis. Falls back to simple text if AI is off.
import google.generativeai as genai
import os
import random
from datetime import datetime

class GeminiCommentaryGenerator:
    def __init__(self, model):
        self.model = model  # May be None if GEMINI_API_KEY is missing
        self.commentary_styles = [
            "energetic football commentator",
            "analytical sports analyst", 
            "dramatic play-by-play announcer",
            "enthusiastic African football expert"
        ]
    
    def generate_match_preview(self, team1, team2):
        """Generate match preview using Gemini
        Inputs: two team dicts with at least country/manager/rating/squad
        Output: short HTML-ready text (string)
        """
        if not self.model:
            return self._fallback_preview(team1, team2)
        
        prompt = f"""
        Generate an exciting match preview for a football match between {team1['country']} and {team2['country']} in the African Nations League.
        
        Team {team1['country']}:
        - Manager: {team1['manager']}
        - Team Rating: {team1['rating']}/100
        - Key Players: {', '.join([p['name'] for p in team1['squad'][:3]])}
        
        Team {team2['country']}:
        - Manager: {team2['manager']}
        - Team Rating: {team2['rating']}/100  
        - Key Players: {', '.join([p['name'] for p in team2['squad'][:3]])}
        
        Write a compelling 2-3 paragraph preview that:
        1. Builds excitement for the match
        2. Highlights the strengths of each team
        3. Mentions key players to watch
        4. Creates anticipation for the African football spectacle
        
        Style: Professional sports journalism with African football passion.
        """
        
        try:
            # Ask the model to produce an article-style preview
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating preview: {e}")
            return self._fallback_preview(team1, team2)
    
    def generate_live_commentary(self, match_events, team1, team2, current_score):
        """Generate realistic live commentary for match events
        Turns a list of event dicts into broadcast-style commentary lines.
        """
        if not self.model:
            return self._fallback_commentary(match_events)
        
        events_text = "\n".join([
            f"Minute {event['minute']}: {event['type'].upper()} - {event['player']} ({event['team']})"
            for event in match_events
        ])
        
        prompt = f"""
        You are {random.choice(self.commentary_styles)} providing live commentary for an African Nations League match between {team1} and {team2}.
        
        CURRENT SCORE: {current_score}
        
        MATCH EVENTS SO FAR:
        {events_text}
        
        Generate realistic, exciting football commentary for these match events. For each major event (goals, saves, chances), provide:
        
        1. A dramatic, emotional call of the action
        2. Brief analysis of what happened
        3. The impact on the match
        4. Some cultural African football flavor
        
        Format as a continuous commentary script with timestamps. Make it sound like a real African football broadcast - passionate, energetic, and knowledgeable.
        
        Include crowd reactions, player emotions, and tactical insights where appropriate.
        """
        
        try:
            # Model returns a multi-line script; split into an array for the UI
            response = self.model.generate_content(prompt)
            commentary_lines = response.text.strip().split('\n')
            return [line for line in commentary_lines if line.strip()]
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return self._fallback_commentary(match_events)
    
    def generate_post_match_analysis(self, match_result, team1, team2):
        """Generate post-match analysis and summary
        Uses score, winner, and goal scorers to craft an article-style recap.
        """
        if not self.model:
            return self._fallback_analysis(match_result)
        
        prompt = f"""
        Provide comprehensive post-match analysis for the African Nations League match between {team1} and {team2}.
        
        FINAL SCORE: {match_result['score']}
        WINNER: {match_result['winner']}
        
        Goal Scorers:
        {chr(10).join([f"- {goal['player']} ({goal['team']}) - {goal['minute']}'" for goal in match_result.get('goal_scorers', [])])}
        
        Write a detailed 3-4 paragraph analysis covering:
        
        1. Match summary and key moments
        2. Analysis of the winning team's performance
        3. Standout players and key contributions
        4. Tactical insights and turning points
        5. Implications for the African Nations League tournament
        
        Style: Professional football analysis with African football expertise and passion.
        Include specific observations about playing styles, individual performances, and tournament context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating post-match analysis: {e}")
            return self._fallback_analysis(match_result)
    
    def generate_player_performance_analysis(self, player, match_events):
        """Generate analysis of a player's performance
        Filters the match events by player and summarizes their impact.
        """
        if not self.model:
            return self._fallback_player_analysis(player, match_events)
        
        player_events = [event for event in match_events if event['player'] == player['name']]
        
        prompt = f"""
        Analyze the performance of {player['name']} ({player['natural_position']}) in today's African Nations League match.
        
        Player Actions in Match:
        {chr(10).join([f"- Minute {event['minute']}: {event['type']}" for event in player_events])}
        
        Provide a brief but insightful analysis (2-3 paragraphs) of:
        - Their impact on the match
        - Key contributions and moments
        - How they performed in their position
        - Overall rating of their performance
        
        Be specific and analytical while maintaining an engaging tone suitable for football fans.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return self._fallback_player_analysis(player, match_events)
    
    def _fallback_preview(self, team1, team2):
        """Fallback match preview when AI is unavailable
        Keep it friendly and generic so the UI still looks good.
        """
        return f"""
        Welcome to the African Nations League clash between {team1['country']} and {team2['country']}!
        
        This promises to be an exciting encounter between two talented African sides. {team1['country']}, managed by {team1['manager']}, brings a team rating of {team1['rating']} into this match. They'll face a determined {team2['country']} side led by {team2['manager']} with a rating of {team2['rating']}.
        
        The atmosphere is electric as these African giants prepare for battle. Who will emerge victorious and advance in this prestigious tournament?
        """
    
    def _fallback_commentary(self, match_events):
        """Fallback commentary when AI is unavailable
        Convert events into short broadcaster-style lines.
        """
        commentary = []
        for event in match_events:
            if event['type'] == 'goal':
                commentary.append(f"{event['minute']}' - GOAL! {event['player']} scores for {event['team']}! The crowd erupts!")
            elif event['type'] == 'save':
                commentary.append(f"{event['minute']}' - What a save by {event['player']}! Incredible reflexes!")
            elif event['type'] == 'chance':
                commentary.append(f"{event['minute']}' - Great opportunity for {event['team']}! {event['player']} with the chance...")
            elif event['type'] == 'foul':
                commentary.append(f"{event['minute']}' - Free kick given after a foul by {event['player']}.")
        return commentary
    
    def _fallback_analysis(self, match_result):
        """Fallback analysis when AI is unavailable
        Provide a minimal but readable summary for the UI.
        """
        return f"""
        Match Analysis: {match_result['team1']} {match_result['score']} {match_result['team2']}
        
        {match_result['winner']} emerged victorious in this African Nations League encounter. The match featured several key moments that determined the outcome.
        
        The goal scorers made the difference today, with both teams showing moments of quality. This result will have significant implications for the tournament progression.
        """

    def _fallback_player_analysis(self, player, match_events):
        """Fallback per-player analysis when AI is unavailable
        Quick scoring of impact based on simple event counts.
        """
        name = player.get('name', 'The player')
        pos = player.get('natural_position', 'Player')
        events = [e for e in match_events if e.get('player') == name]
        goals = sum(1 for e in events if e.get('type') == 'goal')
        saves = sum(1 for e in events if e.get('type') == 'save')
        chances = sum(1 for e in events if e.get('type') == 'chance')
        fouls = sum(1 for e in events if e.get('type') == 'foul')
        moments = ", ".join([f"{e.get('minute', '?')}′ {e.get('type')}" for e in events]) or "no notable recorded events"

        rating_hint = 6.5 + goals*0.8 + saves*0.4 + chances*0.2 - fouls*0.1
        rating = max(5.0, min(9.5, round(rating_hint, 1)))

        return (
            f"{name} ({pos}) delivered a steady performance. Key moments: {moments}.\n\n"
            f"Impact: {('clinical in front of goal' if goals>0 else 'worked to create openings' if chances>0 else 'disciplined off the ball')}. "
            f"{('Important interventions between the posts.' if saves>0 else '')} "
            f"{('Needs more composure; gave away fouls.' if fouls>0 else '')}\n\n"
            f"Overall performance rating: {rating}/10."
        )