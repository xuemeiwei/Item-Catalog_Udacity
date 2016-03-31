## NBA Teams Management App
----
This is the third project for "Full Stack Web Developer Nanodegree" on Udacity, which provides a list of players within a variety of teams as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Instructions
1. Clone the project to local machine.
2. Use "python database_setup.py" to build the database named "teamwithusers.db".
3. Use "python lotsofplayers.py" to import some fake data to the database.
4. Use "python application.py" to run the website on local machine.
5. Open the browser and navigate to "http://localhost:8000/".
6. You can manage the database by clicking respective buttons on the website.

## Functions
1. OAuth 2.0 is used to access Google APIs:
  - Google account is used to login
  - Only the owner of each team can manage his team.
2. JSON APIs are used to get information:
	@app.route('/index/<string:team_ID>/JSON/')
	def teamJSON(team_ID):
    		teams = session.query(Team).filter_by(id=team_ID).one()
    		players = session.query(Player).filter_by(team_id = team_ID).all()
    	return jsonify(Team=teams.serialize, Players = [g.serialize for g in players])

	@app.route('/index/<string:team_ID>/<string:player_ID>/JSON/')
	def playerJSON(team_ID,player_ID):
    		player = session.query(Team).filter_by(id=player_ID).one()
    		return jsonify(Player = player.serialize)








