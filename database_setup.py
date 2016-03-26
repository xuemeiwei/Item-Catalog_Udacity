
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
	"""Return object data in easily serializeable format"""
	return{
		'name': self.name,
		'email': self.email,
		'id': self.id,
		'picture': self.picture,
	}


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
		'name': self.name,
                'description': self.description,
		'id': self.id,
	        'user_id': self.user_id,  
        } 


class Player(Base):
    __tablename__ = 'player'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    number = Column(Integer)
    salary = Column(String(8))
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship(Team)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'salary': self.salary
        }


engine = create_engine('sqlite:///teamwithusers.db')


Base.metadata.create_all(engine)
