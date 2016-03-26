
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Player, Base, Team, User

engine = create_engine('sqlite:///teamwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
session.query(Player).delete()
session.commit()
session.query(Team).delete()
session.commit()
session.query(User).delete()
session.commit()

# Create dummy user
user1 = User(name="Judy Wei", email="xuemeiwei1226@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

user2 = User(name="Grace Wei", email="weixuemeianhui@gmail.com")
session.add(user2)
session.commit()
 
# Players for Golden State Warriors
team1 =Team(user_id=user1.id, name="Golden State Warriors",description="The Golden State Warriors are an American professional basketball team based in Oakland, California")

session.add(team1)
session.commit()

player1 = Player(user_id=user1.id, name="Stephen Curry", description="Point guard",
               salary=1137, team=team1, number=30)

session.add(player1)
session.commit()

player2 = Player(user_id=user1.id, name="Klay Thompson", description="Shooting guard",
              salary=1550, team=team1, number=11)

session.add(player2)
session.commit()

player3 = Player(user_id=user1.id, name="Draymond Green", description="Power forward",
              salary=1426, team=team1, number=23)

session.add(player3)
session.commit()

player4 = Player(user_id=user1.id, name="Harrison Barnes", description="Small forward",
              salary=387, team=team1, number=40)

session.add(player4)
session.commit()

player5 = Player(user_id=user1.id, name="Andre Iguodala", description="Small forward",
              salary=1171, team=team1, number=9)

session.add(player5)
session.commit()

player6 = Player(user_id=user1.id, name="Andrew Bogut", description="Center",
              salary=1380, team=team1, number=12)

session.add(player6)
session.commit()

# Players for Cleveland Cavaliers
team1 =Team(user_id=user1.id, name="Cleveland Cavaliers", id = 2)

session.add(team1)
session.commit()

player1 = Player(user_id=user1.id, name="Lebron James", description="Small forward", salary=2297, team=team1, number=23)
session.add(player1)
session.commit()

player2 = Player(user_id=user1.id, name="Kyrie Irving", description="Point guard",salary=1640, team=team1,number=2)

session.add(player2)
session.commit()

player3 = Player(user_id=user1.id, name="Kevin Love", description="Center",salary=1968, team=team1, number=0)

player4 = Player(user_id=user1.id, name="Matthew Dellavedova", description="Point guard", salary=114, team=team1, number=8)

session.add(player4)
session.commit()

player5 = Player(user_id=user1.id, name="J. R. Smith", description="Small forward",salary=500, team=team1, number=5)

session.add(player5)
session.commit()

player6 = Player(user_id=user1.id, name="Iman Shumpert", description="Small forward", salary=898, team=team1, number=4)

session.add(player6)
session.commit()

# Players for Houston Rockets
team1 =Team(user_id=user2.id, name="Houston Rockets", id = 3)

session.add(team1)

session.commit()

player1 = Player(user_id=user2.id, name="James Harden", description="Shooting guard", salary=1575, team=team1, number=13)

session.add(player1)

session.commit()

player2 = Player(user_id=user2.id, name="Dwight Howard", description="Center", salary=2235, team=team1, number=12)

session.add(player2)

session.commit()

player3 = Player(user_id=user2.id, name="Ty Larson", description="Point guard", salary=1240, team=team1, number=3)

session.add(player3)
session.commit()

player4 = Player(user_id=user2.id, name="Josh Smith", description="Forward", salary=149, team=team1, number=5)

session.add(player4)

session.commit()

player5 = Player(user_id=user2.id, name="Patrick Beverley", description="Pointing guard", salary=648, team=team1, number=2)

session.add(player5)

session.commit()

player6 = Player(user_id=user2.id, name="Trevor Ariza", description="Small forward", salary=819, team=team1, number=1)

session.add(player6)
session.commit()
