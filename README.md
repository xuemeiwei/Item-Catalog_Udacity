## Teams Management App
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
  - Google account is used to login.
  - Only the owner of each team can manage his team.
2. JSON APIs are used to get information:

##

	@app.route('/index/<string:team_ID>/JSON/')
	def teamJSON(team_ID):
		teams = session.query(Team).filter_by(id=team_ID).one()
		players = session.query(Player).filter_by(team_id = team_ID).all()
		return jsonify(Team=teams.serialize, Players = [g.serialize for g in players])
		
	@app.route('/index/<string:team_ID>/<string:player_ID>/JSON/')
	def playerJSON(team_ID,player_ID):
		player = session.query(Team).filter_by(id=player_ID).one()
		return jsonify(Player = player.serialize)



## Display
1. Main page looks like:
![1](https://lh6.googleusercontent.com/-mTzq33J-v9Q/Vv1z6DJ35bI/AAAAAAAAABg/HzNKUmWt8HsroS1STNuBudSoSW27Kdbbg/w1894-h1014-no/main%2Bpage.jpg)

2. The JSON of each team looks like:
![2](https://lh6.googleusercontent.com/-Rt6yQ4J1Coc/Vv3c82OqgsI/AAAAAAAAADI/KF_qqhjEEiUTQcSm3HbHS8FGO7Y8hZjUA/w1896-h1124-no/team.jpg)

3. The JSON of each player looks like:
![3](https://lh4.googleusercontent.com/-fTUmkHyaqjQ/Vv1z-4fxMEI/AAAAAAAAABg/hX0CrCRM55cxhi2GGaKf1BmMO9NseEVZg/w1894-h460-no/player.jpg)
