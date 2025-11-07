# app.py - JSON API Version
# NOTE: This file defines the Flask backend for the African Nations League app.
# It exposes JSON APIs used by the React frontend, simulates matches, and
# integrates optional AI commentary via Gemini. Comments are kept brief/human.
from flask import Flask, request, jsonify, send_from_directory
from backend.config import initialize_firebase, initialize_gemini
from backend.ai_commentary import GeminiCommentaryGenerator
from backend.email_service import send_match_completion_email
import random
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env (e.g., API keys, secrets)

app = Flask(__name__)  # Create the Flask app instance
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-2025')  # Used for session/signing

# Initialize Firebase and Gemini
# Firebase (Firestore) stores teams and matches; Gemini (optional) powers AI text.
db = initialize_firebase()
gemini_model = initialize_gemini()
commentary_generator = GeminiCommentaryGenerator(gemini_model)

# (Countries list removed; React handles form options client-side.)

# Player name generator
# Small helper to create plausible names for generated squads.
def generate_player_name():
    first_names = ["John", "David", "Michael", "James", "Robert", "Mohamed", "Ahmed", "Ibrahim", 
                  "Kofi", "Kwame", "Chukwu", "Adebayo", "Musa", "Sekou", "Jabari", "Tendai"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Traore", "Diallo", "Kamara",
                 "Nkrumah", "Mensah", "Okoro", "Adeyemi", "Sow", "Diop", "Ndlovu", "Mbeki"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Player rating generator
# Give higher stats in natural position, lower in others to feel realistic.
def generate_player_ratings(natural_position):
    ratings = {}
    positions = ['GK', 'DF', 'MD', 'AT']
    
    for position in positions:
        if position == natural_position:
            ratings[position] = random.randint(70, 95)
        else:
            ratings[position] = random.randint(15, 65)
    
    return ratings

# Generate complete squad
# Builds a 23-player squad with a simple position distribution and random captain.
def generate_squad():
    squad = []
    positions_distribution = {
        'GK': 3,
        'DF': 8, 
        'MD': 8,
        'AT': 4
    }
    
    for position, count in positions_distribution.items():
        for i in range(count):
            player = {
                'id': f"player_{len(squad) + 1}",
                'name': generate_player_name(),
                'natural_position': position,
                'ratings': generate_player_ratings(position),
                'jersey_number': len(squad) + 1
            }
            squad.append(player)
    
    # Assign captain
    captain = random.choice(squad)
    captain['is_captain'] = True
    
    return squad

# Calculate team rating
# Average the players' ratings in their natural roles to get a team strength.
def calculate_team_rating(squad):
    if not squad:
        return 0
    
    total_rating = 0
    for player in squad:
        total_rating += player['ratings'][player['natural_position']]
    
    return round(total_rating / len(squad), 2)

# Simple Poisson approximation using standard library
# We avoid extra libs; normal approximation gives a quick goal count feel.
def poisson_approx(lambda_param):
    """Approximate Poisson distribution using normal approximation"""
    if lambda_param <= 0:
        return 0
    # Normal approximation: mean = lambda, variance = lambda
    result = round(random.gauss(lambda_param, (lambda_param ** 0.5)))
    return max(0, int(result))

# Match simulation
# Core simulator. Uses team ratings to bias expected goals, generates events,
# and handles knockout rules (ET, penalties). Detailed mode creates timelines.
def simulate_match(team1_data, team2_data, detailed=False, knockout=False):
    team1_rating = team1_data['rating']
    team2_rating = team2_data['rating']
    
    rating_diff = (team1_rating - team2_rating) / 20  # Scale rating gap to a modest goal bias
    base_goals_team1 = max(0.5, 1.5 + rating_diff + random.uniform(-1, 1))
    base_goals_team2 = max(0.5, 1.5 - rating_diff + random.uniform(-1, 1))
    
    team1_goals = min(7, poisson_approx(base_goals_team1))  # Cap to avoid wild scores
    team2_goals = min(7, poisson_approx(base_goals_team2))
    
    match_events = []
    goal_scorers = []
    
    if detailed:
        # Build a simple timeline by jumping forward random minutes and rolling events
        current_minute = 0
        goals_scored = {team1_data['country']: 0, team2_data['country']: 0}
        
        while current_minute < 90 and (goals_scored[team1_data['country']] < team1_goals or goals_scored[team2_data['country']] < team2_goals):
            current_minute += random.randint(2, 10)
            if current_minute > 90:
                current_minute = 90
                break
            
            attacking_team = random.choice([team1_data, team2_data])  # Who attacks this phase
            defending_team = team2_data if attacking_team == team1_data else team1_data
            
            event_roll = random.random()
            
            if event_roll < 0.1 and goals_scored[attacking_team['country']] < (team1_goals if attacking_team == team1_data else team2_goals):
                # Goal event: pick an attacker/midfielder as scorer
                scorer = random.choice([p for p in attacking_team['squad'] if p['natural_position'] in ['AT', 'MD']])
                match_events.append({
                    'minute': current_minute,
                    'type': 'goal',
                    'team': attacking_team['country'],
                    'player': scorer['name']
                })
                goal_scorers.append({
                    'minute': current_minute,
                    'player': scorer['name'],
                    'team': attacking_team['country']
                })
                goals_scored[attacking_team['country']] += 1
                
            elif event_roll < 0.2:
                # Goalkeeper save event
                goalkeeper = random.choice([p for p in defending_team['squad'] if p['natural_position'] == 'GK'])
                match_events.append({
                    'minute': current_minute,
                    'type': 'save',
                    'team': defending_team['country'],
                    'player': goalkeeper['name']
                })
                
            elif event_roll < 0.3:
                # Created chance that didn't necessarily score
                attacker = random.choice([p for p in attacking_team['squad'] if p['natural_position'] in ['AT', 'MD']])
                match_events.append({
                    'minute': current_minute,
                    'type': 'chance',
                    'team': attacking_team['country'],
                    'player': attacker['name']
                })
                
            elif event_roll < 0.4:
                # Foul to add variety to the timeline
                player = random.choice(attacking_team['squad'])
                match_events.append({
                    'minute': current_minute,
                    'type': 'foul',
                    'team': attacking_team['country'],
                    'player': player['name']
                })
    
    match_events.sort(key=lambda x: x['minute'])

    # If not detailed, still generate basic goal_scorers so UI can show analysis
    if not detailed:
        for _ in range(team1_goals):
            scorer = random.choice([p for p in team1_data['squad'] if p['natural_position'] in ['AT', 'MD']])
            minute = random.randint(5, 85)
            goal_scorers.append({'minute': minute, 'player': scorer['name'], 'team': team1_data['country']})
        for _ in range(team2_goals):
            scorer = random.choice([p for p in team2_data['squad'] if p['natural_position'] in ['AT', 'MD']])
            minute = random.randint(5, 85)
            goal_scorers.append({'minute': minute, 'player': scorer['name'], 'team': team2_data['country']})

    decided_by = None
    penalty_score = None
    used_extra_time = False

    # Knockout logic: no draws allowed.
    if knockout and team1_goals == team2_goals:
        # Extra time: smaller expected goals
        used_extra_time = True
        extra1 = min(3, poisson_approx(max(0.2, base_goals_team1 * 0.3)))
        extra2 = min(3, poisson_approx(max(0.2, base_goals_team2 * 0.3)))

        # If detailed, add simple ET goal events spaced between 91-120
        if detailed:
            for _ in range(extra1):
                minute = random.randint(91, 120)
                scorer = random.choice([p for p in team1_data['squad'] if p['natural_position'] in ['AT', 'MD']])
                match_events.append({'minute': minute, 'type': 'goal', 'team': team1_data['country'], 'player': scorer['name']})
                goal_scorers.append({'minute': minute, 'player': scorer['name'], 'team': team1_data['country']})
            for _ in range(extra2):
                minute = random.randint(91, 120)
                scorer = random.choice([p for p in team2_data['squad'] if p['natural_position'] in ['AT', 'MD']])
                match_events.append({'minute': minute, 'type': 'goal', 'team': team2_data['country'], 'player': scorer['name']})
                goal_scorers.append({'minute': minute, 'player': scorer['name'], 'team': team2_data['country']})

        team1_goals += extra1
        team2_goals += extra2

        if team1_goals != team2_goals:
            decided_by = 'extra_time'
        else:
            # Penalty shootout
            decided_by = 'penalties'
            # Success probability biased by rating difference
            diff = (team1_rating - team2_rating) / 100.0
            p1 = max(0.6, min(0.9, 0.75 + diff))
            p2 = max(0.6, min(0.9, 0.75 - diff))

            t1, t2 = 0, 0
            shots = 0
            # initial 5 each
            for i in range(5):
                shots += 1
                if random.random() < p1:
                    t1 += 1
                if random.random() < p2:
                    t2 += 1
            # sudden death if tied
            while t1 == t2:
                if random.random() < p1:
                    t1 += 1
                if random.random() < p2:
                    t2 += 1
            penalty_score = f"{t1}-{t2}"
            # Set winner by penalties without altering normal-time goals
            # Winner field below will use goals comparison; override if equal
            if detailed:
                match_events.append({'minute': 120, 'type': 'penalties', 'team': 'Both', 'player': f'Shootout {penalty_score}'})

    ai_commentary = []
    match_preview = ""
    
    if detailed:
        # Try AI preview and live commentary; fall back gracefully if unavailable
        try:
            match_preview = commentary_generator.generate_match_preview(team1_data, team2_data)
            current_score = f"{goals_scored[team1_data['country']]}-{goals_scored[team2_data['country']]}"
            ai_commentary = commentary_generator.generate_live_commentary(
                match_events, team1_data['country'], team2_data['country'], current_score
            )
        except Exception as e:
            print(f"Error generating AI commentary: {e}")
            ai_commentary = ["AI commentary temporarily unavailable."]
    
    return {
        'team1': team1_data['country'],
        'team2': team2_data['country'],
        'score': f"{team1_goals}-{team2_goals}",
        'team1_goals': team1_goals,
        'team2_goals': team2_goals,
        'winner': (
            team1_data['country'] if team1_goals > team2_goals else
            team2_data['country'] if team2_goals > team1_goals else
            # If still equal in knockout, winner determined by penalties
            (team1_data['country'] if (penalty_score and int(penalty_score.split('-')[0]) > int(penalty_score.split('-')[1])) else team2_data['country']) if knockout else 'Draw'
        ),
        'events': match_events,
        'goal_scorers': goal_scorers,
        'commentary': ai_commentary,
        'match_preview': match_preview,
        'simulated_at': datetime.now().isoformat(),
        'decided_by': decided_by,
        'penalty_score': penalty_score,
        'extra_time': used_extra_time
    }

# API ROUTES
# JSON-only endpoints consumed by the React frontend.
def _ensure_goal_scorers_for_match(match_data):
    """Ensure goal_scorers array exists for completed matches.
    Mutates match_data in-place and returns True if changes were made."""
    try:
        # Only backfill when a match is completed and scorers are missing
        result = match_data.get('result') or {}
        if match_data.get('status') != 'completed':
            return False
        team1 = match_data.get('team1') or {}
        team2 = match_data.get('team2') or {}
        t1g = int(result.get('team1_goals', 0))
        t2g = int(result.get('team2_goals', 0))
        goal_scorers = result.get('goal_scorers') or []
        if (t1g + t2g) > 0 and len(goal_scorers) == 0:
            gs = []
            for _ in range(t1g):
                scorer = random.choice([p for p in team1.get('squad', []) if p.get('natural_position') in ['AT','MD']] or team1.get('squad', []) or [{'name':'Player 1'}])
                minute = random.randint(5, 120)
                gs.append({'minute': minute, 'player': scorer.get('name','Player'), 'team': team1.get('country','Team 1')})
            for _ in range(t2g):
                scorer = random.choice([p for p in team2.get('squad', []) if p.get('natural_position') in ['AT','MD']] or team2.get('squad', []) or [{'name':'Player 2'}])
                minute = random.randint(5, 120)
                gs.append({'minute': minute, 'player': scorer.get('name','Player'), 'team': team2.get('country','Team 2')})
            gs.sort(key=lambda x: x['minute'])
            result['goal_scorers'] = gs
            match_data['result'] = result
            return True
        return False
    except Exception:
        return False

def _get_team_by_country(country):
    """Fetch full team document by country name."""
    try:
        # Simple DB lookup by country name; returns full team doc or None
        if not country:
            return None
        q = db.collection('teams').where('country', '==', country).stream()
        for doc in q:
            td = doc.to_dict(); td['id'] = doc.id
            return td
        return None
    except Exception:
        return None

def _progress_tournament_if_ready():
    """Create semifinals and final when prior rounds are completed.
    Pairing rules:
      - QF winners: (QF1 vs QF2), (QF3 vs QF4)
      - SF winners: (SF1 vs SF2) => Final
    """
    try:
        # Progress to next rounds automatically when prior rounds fully complete
        # Load all matches and group by round
        all_matches = []
        for doc in db.collection('matches').stream():
            md = doc.to_dict(); md['id'] = doc.id
            all_matches.append(md)

        by_round = {'quarterfinal': [], 'semifinal': [], 'final': []}
        for m in all_matches:
            r = m.get('round')
            if r in by_round:
                by_round[r].append(m)

        # Helper: are all matches in a round completed?
        def all_completed(ms):
            return len(ms) > 0 and all(m.get('status') == 'completed' for m in ms)

        # Create semifinals if all QFs completed and no SF exists
        if all_completed(by_round['quarterfinal']) and len(by_round['semifinal']) == 0:
            qfs = sorted(by_round['quarterfinal'], key=lambda m: m.get('created_at', ''))
            winners = []
            for m in qfs:
                w_country = (m.get('result') or {}).get('winner')
                team = _get_team_by_country(w_country)
                if team:
                    winners.append(team)
            if len(winners) >= 4:
                pairs = [(winners[0], winners[1]), (winners[2], winners[3])]
                for t1, t2 in pairs:
                    db.collection('matches').add({
                        'round': 'semifinal',
                        'team1': t1,
                        'team2': t2,
                        'status': 'scheduled',
                        'created_at': datetime.now().isoformat()
                    })

        # Create final if all SFs completed and no Final exists
        if all_completed(by_round['semifinal']) and len(by_round['final']) == 0:
            sfs = sorted(by_round['semifinal'], key=lambda m: m.get('created_at', ''))
            winners = []
            for m in sfs:
                w_country = (m.get('result') or {}).get('winner')
                team = _get_team_by_country(w_country)
                if team:
                    winners.append(team)
            if len(winners) >= 2:
                db.collection('matches').add({
                    'round': 'final',
                    'team1': winners[0],
                    'team2': winners[1],
                    'status': 'scheduled',
                    'created_at': datetime.now().isoformat()
                })
    except Exception as e:
        # Fail silently to avoid breaking match simulation
        print(f"Tournament progression check failed: {e}")
@app.route('/api/match/<match_id>')
def api_match_details(match_id):
    """API endpoint for match data"""
    try:
        match_doc = db.collection('matches').document(match_id).get()
        if not match_doc.exists:
            return jsonify({'error': 'Match not found'}), 404
        
        match_data = match_doc.to_dict()
        match_data['id'] = match_id
        
        # Ensure all required fields exist
        if 'round' not in match_data:
            match_data['round'] = 'quarterfinal'
        if 'status' not in match_data:
            match_data['status'] = 'scheduled'
        if 'result' not in match_data:
            match_data['result'] = {
                'team1_goals': 0,
                'team2_goals': 0,
                'winner': 'TBD',
                'events': [],
                'goal_scorers': [],
                'commentary': []
            }
            
        # Backfill goal scorers if missing
        updated = _ensure_goal_scorers_for_match(match_data)
        if updated:
            db.collection('matches').document(match_id).update({'result.goal_scorers': match_data['result']['goal_scorers']})
        return jsonify(match_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams')
def api_teams():
    """API endpoint for all teams"""
    try:
        teams = []
        for doc in db.collection('teams').stream():
            team_data = doc.to_dict()
            team_data['id'] = doc.id
            teams.append(team_data)
        
        return jsonify(teams)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams', methods=['POST'])
def api_create_team():
    """Create/register a team via JSON API"""
    try:
        payload = request.get_json(silent=True) or {}
        country = (payload.get('country') or '').strip()
        manager = (payload.get('manager') or '').strip()
        representative = (payload.get('representative') or '').strip()
        email = (payload.get('email') or '').strip()

        if not country or not manager or not representative or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        existing_teams = db.collection('teams').where('country', '==', country).stream()
        if any(existing_teams):
            return jsonify({'error': 'This country is already registered'}), 409

        squad = generate_squad()
        team_rating = calculate_team_rating(squad)

        team_data = {
            'country': country,
            'manager': manager,
            'representative': representative,
            'email': email,
            'squad': squad,
            'rating': team_rating,
            'registered_at': datetime.now().isoformat(),
            'wins': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0
        }

        doc_ref = db.collection('teams').add(team_data)
        return jsonify({'success': True, 'team': {**team_data, 'id': doc_ref[1].id}}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matches')
def api_matches():
    """API endpoint for all matches"""
    try:
        matches = []
        for doc in db.collection('matches').stream():
            match_data = doc.to_dict()
            match_data['id'] = doc.id
            # Backfill goal scorers for completed matches without them
            if _ensure_goal_scorers_for_match(match_data):
                db.collection('matches').document(doc.id).update({'result.goal_scorers': match_data['result']['goal_scorers']})
            matches.append(match_data)
        
        return jsonify(matches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match_preview/<match_id>')
def api_match_preview(match_id):
    """API endpoint for match preview"""
    try:
        match_doc = db.collection('matches').document(match_id).get()
        if not match_doc.exists:
            return jsonify({'error': 'Match not found'}), 404
        
        match_data = match_doc.to_dict()
        preview = commentary_generator.generate_match_preview(match_data['team1'], match_data['team2'])
        
        return jsonify({'preview': preview})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team_analytics/<country>')
def api_team_analytics(country):
    """Return aggregated performance analytics for a given team country."""
    try:
        country = (country or '').strip()
        if not country:
            return jsonify({'error': 'Country is required'}), 400

        # Load team doc
        team_doc = None
        for doc in db.collection('teams').where('country', '==', country).stream():
            td = doc.to_dict(); td['id'] = doc.id
            team_doc = td
            break
        if not team_doc:
            return jsonify({'error': 'Team not found'}), 404

        # Aggregate over matches
        played = 0
        wins = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        by_opponent = {}
        top_scorers = {}
        recent_form = []  # W/L for last 5

        for doc in db.collection('matches').stream():
            m = doc.to_dict(); m['id'] = doc.id
            if m.get('status') != 'completed':
                continue
            t1 = (m.get('team1') or {}).get('country')
            t2 = (m.get('team2') or {}).get('country')
            if t1 != country and t2 != country:
                continue
            res = m.get('result') or {}
            g1 = int(res.get('team1_goals', 0))
            g2 = int(res.get('team2_goals', 0))
            winner = res.get('winner')

            played += 1
            if t1 == country:
                goals_for += g1
                goals_against += g2
                opp = t2 or 'Unknown'
            else:
                goals_for += g2
                goals_against += g1
                opp = t1 or 'Unknown'

            by_opponent.setdefault(opp, {'opponent': opp, 'played': 0, 'wins': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0})
            o = by_opponent[opp]
            o['played'] += 1
            if winner == country:
                wins += 1
                o['wins'] += 1
                recent_form.append('W')
            else:
                losses += 1
                o['losses'] += 1
                recent_form.append('L')
            o['goals_for'] += (g1 if t1 == country else g2)
            o['goals_against'] += (g2 if t1 == country else g1)

            # Top scorers aggregation
            for goal in (res.get('goal_scorers') or []):
                if goal.get('team') == country:
                    key = goal.get('player')
                    top_scorers[key] = top_scorers.get(key, 0) + 1

        gd = goals_for - goals_against
        top_scorers_list = sorted(
            [{'player': p, 'goals': g} for p, g in top_scorers.items()],
            key=lambda x: (-x['goals'], x['player'])
        )
        by_opponent_list = sorted(by_opponent.values(), key=lambda x: (-x['wins'], x['opponent']))
        recent_form = recent_form[-5:][::-1]  # last 5, newest first

        return jsonify({
            'team': {'country': team_doc.get('country'), 'rating': team_doc.get('rating'), 'manager': team_doc.get('manager')},
            'summary': {
                'played': played,
                'wins': wins,
                'losses': losses,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': gd,
                'recent_form': recent_form
            },
            'top_scorers': top_scorers_list,
            'record_by_opponent': by_opponent_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player_analysis/<match_id>/<player_name>')
def api_player_analysis(match_id, player_name):
    """API endpoint for player analysis"""
    try:
        from urllib.parse import unquote
        player_name = unquote(player_name)  # Decode URL-encoded player name
        
        match_doc = db.collection('matches').document(match_id).get()
        if not match_doc.exists:
            return jsonify({'error': 'Match not found'}), 404
        
        match_data = match_doc.to_dict()
        
        player = None
        for p in match_data['team1']['squad'] + match_data['team2']['squad']:
            if p['name'] == player_name:
                player = p
                break
        
        if not player:
            return jsonify({'error': f'Player "{player_name}" not found in match squads'}), 404
        
        # Get match events for context
        events = match_data.get('result', {}).get('events', [])
        goal_scorers = match_data.get('result', {}).get('goal_scorers', [])
        
        # Check if this player scored
        player_goals = [g for g in goal_scorers if g.get('player') == player_name]
        
        if not player_goals:
            return jsonify({'analysis': f'{player_name} did not score in this match.'}), 200
        
        # Generate analysis using the commentary generator
        try:
            analysis = commentary_generator.generate_player_performance_analysis(
                player, 
                events
            )
            if not analysis or analysis.strip() == '':
                analysis = f'{player_name} performed well in this match, scoring {len(player_goals)} goal(s).'
        except Exception as gen_error:
            print(f"Error generating player analysis: {gen_error}")
            analysis = f'{player_name} scored {len(player_goals)} goal(s) at {", ".join([str(g.get("minute", "")) + "\'" for g in player_goals])}.'
        
        return jsonify({'analysis': analysis, 'player': player})
    except Exception as e:
        print(f"Error in api_player_analysis: {e}")
        return jsonify({'error': str(e)}), 500

# HTML ROUTES are no longer used by the React app.

@app.route('/simulate_match/<match_id>')
def simulate_match_route(match_id):
    try:
        match_ref = db.collection('matches').document(match_id)  # Load match doc
        match_data = match_ref.get().to_dict()
        
        knockout = match_data.get('round') in ['quarterfinal', 'semifinal', 'final']  # KO rounds cannot draw
        result = simulate_match(match_data['team1'], match_data['team2'], detailed=False, knockout=knockout)
        
        match_ref.update({
            'result': result,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        })
        
        # Send email notification to federations
        send_match_completion_email(match_data, result, db)
        
        _progress_tournament_if_ready()  # If QFs or SFs finished, create next round
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/play_match/<match_id>')
def play_match(match_id):
    try:
        match_ref = db.collection('matches').document(match_id)
        match_data = match_ref.get().to_dict()
        
        knockout = match_data.get('round') in ['quarterfinal', 'semifinal', 'final']
        result = simulate_match(match_data['team1'], match_data['team2'], detailed=True, knockout=knockout)  # Detailed adds events/AI
        
        match_ref.update({
            'result': result,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        })
        
        # Send email notification to federations
        send_match_completion_email(match_data, result, db)
        
        _progress_tournament_if_ready()  # Also advance bracket when using detailed play
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# (Removed legacy HTML tournament management routes.)

# JSON admin endpoints used by React Dashboard (no redirects)
@app.route('/api/admin/create_tournament', methods=['POST'])
def api_create_tournament():
    try:
        teams = []  # Load all registered teams
        for doc in db.collection('teams').stream():
            td = doc.to_dict(); td['id'] = doc.id; teams.append(td)
        if len(teams) < 8:
            return jsonify({'success': False, 'error': 'Need exactly 8 teams to create tournament'}), 400
        for match in db.collection('matches').stream():  # Reset existing matches
            db.collection('matches').document(match.id).delete()
        for i in range(0, 8, 2):
            match_data = {
                'round': 'quarterfinal',
                'team1': teams[i],
                'team2': teams[i+1],
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            db.collection('matches').add(match_data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/reset_tournament', methods=['POST'])
def api_reset_tournament():
    try:
        for match in db.collection('matches').stream():  # Delete all matches
            db.collection('matches').document(match.id).delete()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Serve React build in production (optional)
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')  # Optional static serving

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    if os.path.exists(os.path.join(FRONTEND_BUILD_DIR, path)):
        return send_from_directory(FRONTEND_BUILD_DIR, path)
    index_path = os.path.join(FRONTEND_BUILD_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_BUILD_DIR, 'index.html')
    # If build does not exist, provide a simple message
    return 'React build not found. Run npm run build in the frontend directory.', 200  # Helpful hint in dev

if __name__ == '__main__':
    # Start development server
    app.run(debug=True, host='0.0.0.0', port=5000)  # Start dev server