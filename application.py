
from flask import Flask,jsonify,flash,render_template,request,redirect,url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Team, Player, User
from functions_helper import *
import random, string

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


engine = create_engine('sqlite:///teamwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all teams
@app.route('/')
@app.route('/index/')
def showTeams():
    teams = session.query(Team).all()
    latest_players = session.query(Player).order_by(Player.created_at.desc()).limit(5)
    return  render_template('main.html', teams = teams, latest_players = latest_players, login_session = login_session)

# Show players
@app.route('/index/<string:team_ID>/')
def showPlayers(team_ID):
    team = session.query(Team).filter_by(id=team_ID).one()
    user_id = team.user_id
    user = session.query(User).filter_by(id=user_id).one()
    players = session.query(Player).filter_by(team_id=team_ID).all()
    return render_template('players.html', players=players, team=team, user=user, login_session=login_session)

# Login screen
@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state, login_session = login_session)

# Connect to google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = request.args.get('gplus_id')
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
	oauth_flow.redirect_uri = 'postmessage'
	credentials = oauth_flow.step2_exchange(code)
        
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    credentials = credentials.to_json()            
    credentials = json.loads(credentials)         
    access_token = credentials['token_response']['access_token']     
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials['id_token']['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    response = make_response(json.dumps('Successfully connected user.', 200))

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials['token_response']['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    # dimensions of the picture at login:
    output += ' " style = "width: 300px; height: \
        300px;border-radius: \
        50px;-webkit-border-radius: \
        150px;-moz-border-radius: 50px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# Disconnect from current google account
@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')
    # Only disconnect a connected user.
    if not checkLogin(login_session):
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials['token_response']['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('showTeams'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        flash('Failed to revoke token for given user.')
        return redirect(url_for('showTeams'))

# Create a new team
@app.route('/new/',methods = ['GET','POST'])
def newTeam():
    if not checkLogin(login_session):
	flash('You must login to create a team')
	return redirect(url_for('showTeams'))

    if request.method == 'POST':
	newTeam = Team(name=request.form['name'],description=request.form['description'],user_id=login_session.get('user_id'))
	session.add(newTeam)
	flash('New Team %s Successfully Created' % newTeam.name)
	session.commit()
	return redirect(url_for('showTeams'))
    else:
	return render_template('newTeam.html',login_session=login_session)

# Add a new player to team
@app.route('/index/<string:team_ID>/add', methods=['GET', 'POST'])
def addNewPlayer(team_ID):
    if not checkLogin(login_session):
	flash('You must login to add a new player')
	return redirect(url_for('showTeams'))
    if request.method=='POST':
	newPlayer=Player(name=request.form['name'],
			description = request.form['description'], 
			user_id = login_session.get('user_id'), 
			salary = request.form['salary'], 
			team_id = team_ID)
	session.add(newPlayer)
	session.commit()
	flash('New Player %s has been successfully Created' % newPlayer.name)
	return redirect(url_for('showTeams', team_ID=team_ID))
    else:
	return render_template('newPlayer.html',team_ID=team_ID,login_session=login_session)

# Delete a player from team
@app.route('/index/<string:team_ID>/<string:player_ID>/delete')
def deletePlayer(team_ID,player_ID):
    if not checkLogin(login_session):
	flash('You must login to manage a team.')
	return redirect(url_for('showTeams',team_ID = team_ID))
    login_user_id=getUserID(login_session['email'])
    playerToDelete=session.query(Player).filter_by(id=player_ID).one()
    if playerToDelete.user_id != login_user_id:
	flash("You can only manage your own team.")
	return redirect(url_for('showTeams',team_ID=team_ID))
    session.delete(playerToDelete)
    session.commit()
    flash("You have deleted a player successfully.")
    return redirect(url_for('showTeams',team_ID=team_ID))

# Edit a player
@app.route('/index/<string:team_ID>/<string:player_ID>/edit', methods=['GET', 'POST'])
def editPlayer(team_ID,player_ID):
    if not checkLogin(login_session):
	flash('You must login to manage a team.')
	return redirect(url_for('showTeams',team_ID = team_ID))
    login_user_id = getUserID(login_session['email'])
    playerToEdit= session.query(Player).filter_by(id=player_ID).one()
    if playerToEdit.user_id != login_user_id:
	flash("You can only manage your own team.")
	return redirect(url_for('showTeams',team_ID=team_ID))
    if request.method == 'POST':
	playerToEdit.name = request.form['name']
	playerToEdit.description = request.form['description']
	playerToEdit.salary = request.form['salary']
	flash('%s has been successfully edited' % playerToEdit.name)
	return redirect(url_for('showTeams',team_ID = team_ID))
    else:
	return render_template('editPlayer.html',player=playerToEdit,login_session = login_session)

# Edit a team
@app.route('/index/<string:team_ID>/edit/',methods = ['GET','POST'])
def editTeam(team_ID):
    if not checkLogin(login_session):
        flash('You must login to manage a team.')
        return redirect(url_for('showTeams',team_ID = team_ID))
    login_user_id = getUserID(login_session['email'])
    teamToEdit= session.query(Team).filter_by(id=team_ID).one()
    if teamToEdit.user_id != login_user_id:
        flash("You can only manage your own team.")
        return redirect(url_for('showTeams',team_ID=team_ID))
    if request.method == 'POST':
	teamToEdit.name = request.form['name']
	teamToEdit.description = request.form['description']
	return redirect(url_for('showTeams',team_ID=team_ID))
    else:
	return render_template('editTeam.html',team = teamToEdit,login_session=login_session)


# Delete a team
@app.route('/index/<string:team_ID>/delete/',methods = ['GET','POST'])
def deleteTeam(team_ID):
    if not checkLogin(login_session):
        flash('You must login to manage a team.')
        return redirect(url_for('showTeams',team_ID = team_ID))
    login_user_id = getUserID(login_session['email'])
    teamToDelete= session.query(Team).filter_by(id=team_ID).one()
    if teamToDelete.user_id != login_user_id:
        flash("You can only manage your own team.")
        return redirect(url_for('showTeams',team_ID=team_ID))
    session.delete(teamToDelete)
    session.commit()
    flash("You have deleted your team successfully.")
    return redirect(url_for('showTeams',team_ID=team_ID))   

# Redirect to the screen of Help
@app.route('/help')
def help():
    return render_template("help.html")

#json APIs
@app.route('/index/<string:team_ID>/JSON/')
def teamJSON(team_ID):
    teams = session.query(Team).filter_by(id=team_ID).one()
    players = session.query(Player).filter_by(team_id = team_ID).all()
    return jsonify(Team=teams.serialize, Players = [g.serialize for g in players])

@app.route('/index/<string:team_ID>/<string:player_ID>/JSON/')
def playerJSON(team_ID,player_ID):
    player = session.query(Team).filter_by(id=player_ID).one()
    return jsonify(Player = player.serialize)


if __name__ == '__main__':
    app.secret_key='super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
