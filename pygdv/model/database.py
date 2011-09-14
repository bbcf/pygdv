# -*- coding: utf-8 -*-
'''
Database model
'''


from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import relationship, synonym

from pygdv.model import DeclarativeBase, metadata, DBSession

from datetime import datetime

import uuid

__all__ = ['Project','PublicProject',
           'Track','TrackParameters',
           'TrackType','Style',
           'UserStyle','Input',
           'Sequence','AdminTrack',
           'Species','Status',
           'Job','JobParameter']



statuses = Enum('SUCCESS','PENDING','ERROR','RUNNING',name='job_status')
image_types = Enum('FeatureTrack','ImageTrack',name='image_type')
datatypes = Enum('QUALITATIVE','QUANTITATIVE','QUALITATIVE_EXTENDED',name="datatype")
job_types = Enum('NEW_SELECTION','NEW_TRACK','GFEATMINER','NEW_PROJECT',name='job_type')
job_outputs = Enum('RELOAD','IMAGE',name='job_output')




date_format = "%A %d. %B %Y %H.%M.%S"






project_track_table = Table('project_track', metadata,
    Column('project_id', Integer, ForeignKey('Project.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('Track.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

user_circle_table = Table('user_circle', metadata,
    Column('user_id', Integer, ForeignKey('User.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('circle_id', Integer, ForeignKey('Circle.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

user_track_table = Table('user_track', metadata,
    Column('user_id', Integer, ForeignKey('User.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('Track.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)





class Right(DeclarativeBase):
    '''
    Like permissions, but not for the control of access on pages but for sharing between projects.
    '''
    __tablename__='right'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)

class Circle(DeclarativeBase):
    '''
    A group of users.
    '''
    __tablename__='circle'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)
    creator = relationship('User')
    
    users = relationship('User', secondary=user_circle_table, backref='circles')
    


class Project(DeclarativeBase):
    '''
    Project table. It is a view that an user can browse.
    '''
    
    def setdefaultkey(self):
        uid = str(uuid.uuid4())
        while DBSession.query(Project).filter(Project.key == uid).first():
            uid = str(uuid.uuid4())
        return uid
    
    
    __tablename__ = 'Project'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    _created = Column(DateTime, default=datetime.now, nullable=False)
    sequence_id = Column(Integer, ForeignKey('Sequence.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    #relations
    user_id = Column(Integer, ForeignKey('User.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
 
    tracks = relationship('Track', secondary=project_track_table, backref='projects')
    
    sequences = relationship('Sequence', backref='projects')
    
    _circle_right = relationship('RightGroupAssociation', backref='project')
    
    jobs = relationship('Job', backref='project')
    
    is_public = Column(Boolean, nullable=False)
    key = Column(Unicode(255), unique=True,default=setdefaultkey, nullable=False)
    
    def _get_date(self):
        return self._created.strftime(date_format);
        
    def _set_date(self,date):
        self._created=date

    created = synonym('_created', descriptor=property(_get_date, _set_date))
        
    # special methods
    def __repr__(self):
        return '<Project: id=%r, name=%r, created=%r>' % (self.id,self.name,self.created)
    def __unicode__(self):
        return self.name
    @property
    def species(self):
        return self.sequence.species
    
    @property
    def circles_with_rights(self):
        '''
        Get a list of tuples (Circle, associated rights)
        '''
        result = []
        for cr in self._circle_right:
            result.append((cr.circle, cr.right))
        return result
    


class RightCircleAssociation(DeclarativeBase):
    __tablename__='right_group_assoc'
    
    right = relationship('Right')
    circle =  relationship('Circle')
    project_id = Column(Integer, ForeignKey('Project.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    
 
    
class Sequence(DeclarativeBase):
    '''
    Sequences created.
    '''
    __tablename__ = 'Sequence'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    species_id = Column(Integer, ForeignKey('Species.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    default_tracks = relationship('Track')
    
    def __repr__(self):
        return '<Sequence: id=%r, name=%r, species_id=%r>' % (self.id,self.name,self.species_id)
    def __str__(self):
        return self.name  
    
class Species(DeclarativeBase):
    '''
    Species.
    '''
    __tablename__='Species'
    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    # relation
    sequences = relationship("Sequence", backref="species")
    def __repr__(self):
        return '<Species: id=%r, name=%r>' % (self.id,self.name)
    def __str__(self):
        return self.name
    
    
    
    
    
class Input(DeclarativeBase):
    '''
    An unique input.
    '''
    __tablename__ = 'Input'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    sha1 = Column(Unicode(255), unique=True, nullable=False)
    _last_access = Column(DateTime, default=datetime.now, nullable=False)
    tracks = relationship('Track', backref='input')
    
    # special methods
    def __repr__(self):
        return '<Input: id=%r, sha1=%r>' % (self.input,self.sha1)
    def __unicode__(self):
        return self.sha1
    
    def _get_last_access(self):
        return self._last_access.strftime(date_format);
        
    def _set_last_access(self,date):
        self._last_access=date

    last_access = synonym('_last_access', descriptor=property(_get_last_access, _set_last_access))
    
    @property
    def accessed(self):
        '''
        Update the field 'last_access' by the current time
        '''
        self._set_last_access(datetime.now())

    

    
    
    
    
class TrackParameters(DeclarativeBase):
    '''
    Track parameters.
    Based on the type, parameters can be different.
    '''
    __tablename__='Track_parameters'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(Unicode(255), nullable=False)
    label = Column(Unicode(255), nullable=False)
    type = Column(image_types, nullable=False)
    key = Column(Unicode(255), nullable=False)
    color = Column(Unicode(255), nullable=False)
    track_id = Column(Integer, nullable=False, ForeignKey('Track.id', onupdate="CASCADE", ondelete="CASCADE"))
    track = relationship('Track', uselist=False, backref='parameters')


class Track(DeclarativeBase):
    '''
    Represent a track on the view.
    '''
    __tablename__ = 'Track'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    _created = Column(DateTime, nullable=False, default=datetime.now)
    _last_access = Column(DateTime, default=datetime.now, nullable=False)
    visu = Column(datatypes, nullable=False)
    
    input_id = Column(Integer, ForeignKey('Input.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    parameter_id = Column(Integer, ForeignKey('TrackParameters.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    sequence_id = Column(Integer, ForeignKey('Sequence.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    # special methods
    def __repr__(self):
        return '<Track: id=%r, name=%r, created=%r, visu=%r>' % (self.id,self.name,self.created,self.visu)
    def __unicode__(self):
        return self.name
    
    def _get_date(self):
        return self._created.strftime(date_format);
        
    def _set_date(self,date):
        self._created=date
        
    def _get_last_access(self):
        return self._last_access.strftime(date_format);
        
    def _set_last_access(self,date):
        self._last_access=date

    created = synonym('_created', descriptor=property(_get_date, _set_date))
    last_access = synonym('_last_access', descriptor=property(_get_last_access, _set_last_access))
    
    def accessed(self):
        '''
        Update the field 'last_access' by the current time
        '''
        self._set_last_access(datetime.now())
        
        

class JobParameter(DeclarativeBase):
    '''
    Jobs parameters.
    '''
    __tablename__='Job_parameter'
    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(job_types, nullable=False)
    output = Column(job_outputs, nullable=False)
    data = Column(Text(), nullable=True)
    job_id = Column(Integer, ForeignKey('Job.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
class Job(DeclarativeBase):
    '''
    Represent all jobs that are submitted to GDV.
    '''
    __tablename__='Job'
    
    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)
    
    _created = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(statuses, nullable=False)
    
    user_id = Column(Integer, ForeignKey('User.id',onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    project_id = Column(Integer, ForeignKey('Project.id',onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    
    parameters = relationship('JobParameter', uselist=False, backref='job')
    
    def _get_date(self):
        return self._created.strftime(date_format);
        
    def _set_date(self,date):
        self._created=date
    
    created = synonym('_created', descriptor=property(_get_date, _set_date))

    @property
    def get_type(self):
        return self.parameters.type
    
    
    


     
    