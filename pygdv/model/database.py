# -*- coding: utf-8 -*-
'''
Database model
'''



from sqlalchemy import Table, ForeignKey, Column, Sequence
from sqlalchemy.types import Unicode, Integer, DateTime, Enum, Text, Boolean, VARCHAR, BLOB, Binary

from sqlalchemy.orm import relationship, synonym
from sqlalchemy import Sequence as Seq
from pygdv.lib.celery import PickleType
from pygdv.model import DeclarativeBase, metadata, DBSession
import transaction
import os
from pygdv.lib import constants
from datetime import datetime

import uuid
from sqlalchemy.engine.base import Transaction

__all__ = ['Right', 'Circle', 'Project',
           'RightCircleAssociation','Sequence',
           'Species','TrackParameters',
           'Track', 'Task', 'Input',
           'Sequence',
           'Species',
           'Job','JobParameters']


statuses = Enum('SUCCESS', 'PENDING', 'ERROR', 'RUNNING', name='job_status')
image_types = Enum(constants.FEATURE_TRACK, constants.IMAGE_TRACK, name='image_type')
datatypes = Enum(constants.FEATURES, constants.SIGNAL, constants.RELATIONAL, constants.NOT_DETERMINED_DATATYPE ,name="datatype")
job_types = Enum('NEW_SELECTION', 'NEW_TRACK', 'GFEATMINER', 'NEW_PROJECT', name='job_type')
job_outputs = Enum('RELOAD', 'IMAGE', name='job_output')








project_track_table = Table('project_track', metadata,
    Column('project_id', Integer, ForeignKey('Project.id',
         ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('Track.id',
         ondelete="CASCADE"), primary_key=True)
)



default_track_table = Table('default_tracks', metadata,
        Column('track_id', Integer, ForeignKey('Track.id',
         ondelete="CASCADE"), primary_key=True),
        Column('sequence_id', Integer, ForeignKey('Sequence.id',
         ondelete="CASCADE"), primary_key=True)
)

class Right(DeclarativeBase):
    '''
    Like permissions, but not for the control of access on pages but for sharing between projects.
    '''
    __tablename__='Right'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    description = Column(Text(), nullable=False)

    def __str__(self):
        return self.name
    
class Circle(DeclarativeBase):
    '''
    A group of users.
    '''
    __tablename__='Circle'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)
    creator_id = Column(Integer, ForeignKey('User.id',  ondelete="CASCADE"), nullable=True)
    admin = Column(Boolean, nullable= False, default = False)
    
    
    @property
    def display(self):
        return '%s (%s)' % (self.name, self.description)

    def __repr__(self):
        return '<Circle : name : %s, desc : %s>' % (self.name, self.description)
    
class RightCircleAssociation(DeclarativeBase):
    __tablename__='RightCircleAssociation'
    
    right = relationship('Right')
    right_id = Column(Integer,
                       ForeignKey('Right.id',  ondelete="CASCADE"), nullable=False, primary_key=True)
    circle =  relationship('Circle',  cascade="all, delete")
    circle_id = Column(Integer,
                       ForeignKey('Circle.id',  ondelete="CASCADE"), nullable=False, primary_key=True)
    project_id = Column(Integer, ForeignKey('Project.id',  ondelete="CASCADE"), nullable=False, primary_key=True)

    @property
    def circle_display(self):
        return '%s (%s)' %(self.circle.name, self.circle.description)
    
    def __repr__(self):
        return '<RightCircleAssociation : right : %s, circle : %s, project : %s>' % (self.right_id, self.circle_id, self.project_id)
    
    
class CircleRights(object):
    '''
    Represent a circle with the rights associated
    '''
    def __init__(self, project_id, circle, rights):
        self.project_id = project_id
        self.circle = circle
        self.rights = rights
 
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
    sequence_id = Column(Integer, ForeignKey('Sequence.id',  ondelete="CASCADE"), nullable=False)
    sequence = relationship("Sequence")
    #relations
    user_id = Column(Integer, ForeignKey('User.id',  ondelete="CASCADE"), nullable=False)
 
    tracks = relationship('Track', secondary=project_track_table, backref='projects')
    
    _circle_right = relationship('RightCircleAssociation', backref='project')
    
    jobs = relationship('Job', backref='project')
    
    is_public = Column(Boolean, nullable=False)
    key = Column(Unicode(255), unique=True,default=setdefaultkey, nullable=False)
    
    def _get_date(self):
        return self._created.strftime(constants.date_format);
        
    def _set_date(self,date):
        self._created=date

    created = synonym('_created', descriptor=property(_get_date, _set_date))
    
    # special methods
    def __repr__(self):
        return '<Project: id=%r, name=%r, created=%r>' % (self.id,self.name,self.created)
    def __unicode__(self):
        return self.name
    @property
    def assembly(self):
        return self.sequence.name
    @property
    def species(self):
        return self.sequence.species
    @property
    def circles_with_rights(self):
        '''
        Get a list of dict {Circle : [associated rights]}
        '''
        result = {}
        for cr in self._circle_right:
            if result.has_key(cr.circle) :
                rights = result.get(cr.circle)
            else :
                rights = []
            rights.append(cr.right)
            result[cr.circle]=rights
        return result
    
    
    @property 
    def get_tracks(self):
        return ', '.join([track.name for track in self.tracks])
    @property
    def circles(self):
        res = []
        for cr in self._circle_right:
            res.append(cr.circle)
        return res
    @property
    def get_circle_with_right_display(self):
        '''
        Get a list of groups with rights associated
        in a suitable manner for display : Circle (associated rights) )
        '''
        crs = self.circles_with_rights
        result = []
        for circle, rights in crs.items():
            result.append('%s (%s)\n' %(circle.name, ', '.join([right.name for right in rights])))
        return result
    
    @property
    def circles_rights(self):
        data = self.circles_with_rights
        return [CircleRights(self.id, circle, rights) for circle, rights in data.iteritems()]
    
    
    
    
class Sequence(DeclarativeBase):
    '''
    Sequences created.
    '''
    __tablename__ = 'Sequence'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    species_id = Column(Integer, ForeignKey('Species.id', ondelete="CASCADE"), nullable=False)
    
    default_tracks = relationship('Track', secondary=default_track_table)
    
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
    


class Task(DeclarativeBase):
    __tablename__ = "celery_taskmeta"
    
    id = Column('id', Integer, Seq('task_id_sequence'), primary_key=True, autoincrement=True )
    task_id = Column(VARCHAR(255), unique=True)
    status = Column(VARCHAR(50), default='PENDING')
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.now,
                       onupdate=datetime.now, nullable=True)
    traceback = Column(Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id

    


class Input(DeclarativeBase):
    '''
    An unique input.
    '''
    __tablename__ = 'Input'
    
    
    
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    sha1 = Column(Unicode(255), unique=True, nullable=False)
    _last_access = Column(DateTime, default=datetime.now, nullable=False)
    tracks = relationship('Track', backref='input',  cascade="all, delete, delete-orphan")
  
    task_id = Column(VARCHAR(255), nullable=False)
    task = relationship('Task', uselist=False, primaryjoin='Input.task_id == Task.task_id', foreign_keys='Task.task_id')
    #task_id = Column(Integer, ForeignKey('celery_taskmeta.task_id', ondelete="CASCADE"), nullable=False)
    #task = relationship('Task')
    datatype = Column(datatypes, nullable=False, default=constants.NOT_DETERMINED_DATATYPE)
    
    @property
    def path(self):
        return os.path.join(constants.track_directory(), '%s.%s' % (self.sha1, 'sql'))
    
    
    # special methods
    def __repr__(self):
        return '<Input: id=%r, sha1=%r>' % (self.id,self.sha1)
    def __unicode__(self):
        return self.sha1
    
    def _get_last_access(self):
        return self._last_access.strftime(constants.date_format);
        
    def _set_last_access(self,date):
        self._last_access=date

    last_access = synonym('_last_access', descriptor=property(_get_last_access, _set_last_access))
    
    @property
    def accessed(self):
        '''
        Update the field 'last_access' by the current time
        '''
        self._set_last_access(datetime.now())

    @property
    def status(self):
        if self.task is None:
            return 'PENDING'
        return self.task.status
    
    @property
    def traceback(self):
        if self.task is None: return ''
        return self.task.traceback
    



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
    
    input_id = Column(Integer, ForeignKey('Input.id', ondelete="CASCADE"), nullable=False)
   
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    
    
    sequence_id = Column(Integer, ForeignKey('Sequence.id', ondelete="CASCADE"), nullable=False)
    sequence = relationship("Sequence")
    
    parameters = relationship('TrackParameters', uselist=False, backref='track', cascade='delete')
    
    # special methods
    def __repr__(self):
        return '<Track: id=%r, name=%r, created=%r, vizu=%r, user_id=%r>' % (self.id, self.name, self.created, self.vizu, self.user_id)
    def __unicode__(self):
        return self.name
    
    def _get_date(self):
        return self._created.strftime(constants.date_format);
        
    def _set_date(self,date):
        self._created=date
        
    def _get_last_access(self):
        return self._last_access.strftime(constants.date_format);
        
    def _set_last_access(self, date):
        self._last_access=date

    @property
    def status(self):
        return self.input.status
    
    
    @property
    def task(self):
        return self.input.task
    
    @property
    def traceback(self):
        return self.input.traceback

    
    @property
    def vizu(self):
        return self.input.datatype
    
    created = synonym('_created', descriptor=property(_get_date, _set_date))
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
    __tablename__='TrackParameters'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(Unicode(255), nullable=True)
    label = Column(Unicode(255), nullable=True)
    type = Column(image_types, nullable=True)
    key = Column(Unicode(255), nullable=True)
    color = Column(Unicode(255), nullable=True)
    track_id = Column(Integer, ForeignKey('Track.id',  onupdate='CASCADE', ondelete="CASCADE"), 
                           nullable=False)
    
    
    @property
    def jb_dict(self):
        '''
        Get the representation dict for jbrowse
        '''
        return {'url' : self.url, 'label' : self.label, 'type' : self.type, 
                'gdv_id' : self.id, 'key' : self.key}
    
    def build_parameters(self):
        self.url = os.path.join(self.track.input.sha1, '{refseq}' ,constants.track_data)
        self.label = self.track.name
        self.key = self.track.name
        '''
        RELATIONAL = 'relational'
SIGNAL = 'signal'
FEATURES = 'features'
        '''
        if self.track.vizu == constants.RELATIONAL or self.track.vizu == constants.FEATURES :
            self.type = constants.FEATURE_TRACK
        else :
            self.type = constants.IMAGE_TRACK

class JobParameters(DeclarativeBase):
    '''
    Jobs parameters.
    '''
    __tablename__='JobParameters'
    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(job_types, nullable=False)
    output = Column(job_outputs, nullable=False)
    data = Column(Text(), nullable=True)
    job_id = Column(Integer, ForeignKey('Job.id',  ondelete="CASCADE"), nullable=False)
    
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
    
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    
    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=True)
    
    #task_id = Column(Integer, ForeignKey('celery_taskmeta.id', ondelete="CASCADE"), nullable=False)
    #task = relationship('Task', uselist=False, backref='job')
    task_id = Column(VARCHAR(255), nullable=False)
    task = relationship('Task', uselist=False, primaryjoin='Job.task_id == Task.task_id', foreign_keys='Task.task_id')
    parameters = relationship('JobParameters', uselist=False, backref='job')
    
    def _get_date(self):
        return self._created.strftime(constants.date_format);
        
    def _set_date(self,date):
        self._created=date
    
    created = synonym('_created', descriptor=property(_get_date, _set_date))

    @property
    def get_type(self):
        return self.parameters.type




