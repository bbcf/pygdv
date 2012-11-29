# -*- coding: utf-8 -*-
'''
Database model
'''
from sqlalchemy import Table, ForeignKey, Column, Sequence
from sqlalchemy.types import Unicode, Integer, DateTime, Enum, Text, Boolean, VARCHAR, TypeDecorator

from sqlalchemy.orm import relationship, synonym
from sqlalchemy import Sequence as Seq
from pygdv.lib.celery import PickleType
from pygdv.model import DeclarativeBase, metadata, DBSession
import os
from pygdv.lib import constants
from datetime import datetime
import uuid
import json


statuses = Enum('UPLOADING', 'FAILURE', name='track_status')

image_types = Enum(constants.FEATURE_TRACK, constants.IMAGE_TRACK, name='image_type')
datatypes = Enum(constants.FEATURES, constants.SIGNAL, constants.RELATIONAL, constants.NOT_DETERMINED_DATATYPE, name="datatype")
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


sequence_users_table = Table('sequence_users', metadata,
    Column('sequence_id', Integer, ForeignKey('Sequence.id',
        ondelete="CASCADE"), primary_key=True),
    Column('user_id', Integer, ForeignKey('User.id',
        ondelete="CASCADE"), primary_key=True)
)


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    Usage::
        JSONEncodedDict(255)
    """
    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)


class Right(DeclarativeBase):
    '''
    Like permissions, but not for the control of access on pages but for sharing between projects.
    '''
    __tablename__ = 'Right'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    description = Column(Text(), nullable=False)

    def __str__(self):
        return self.name


class Circle(DeclarativeBase):
    '''
    A group of users.
    '''
    __tablename__ = 'Circle'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)
    creator_id = Column(Integer, ForeignKey('User.id',  ondelete="CASCADE"), nullable=True)
    admin = Column(Boolean, nullable=False, default=False)
    creator = relationship("User")

    @property
    def display(self):
        return '%s (%s)' % (self.name, self.description)

    def __repr__(self):
        return '<Circle: name: %s, desc: %s>' % (self.name, self.description)

    @property
    def get_users(self):
        return ', '.join([user.name for user in self.users])


class RightCircleAssociation(DeclarativeBase):
    __tablename__ = 'RightCircleAssociation'

    right = relationship('Right')
    right_id = Column(Integer,
                       ForeignKey('Right.id',  ondelete="CASCADE"), nullable=False, primary_key=True)
    circle = relationship('Circle')
    circle_id = Column(Integer,
                       ForeignKey('Circle.id',  ondelete="CASCADE"), nullable=False, primary_key=True)
    project_id = Column(Integer, ForeignKey('Project.id',  ondelete="CASCADE"), nullable=False, primary_key=True)

    @property
    def circle_display(self):
        return '%s (%s)' % (self.circle.name, self.circle.description)

    def __repr__(self):
        return '<RightCircleAssociation: right: %s, circle: %s, project: %s>' % (self.right_id, self.circle_id, self.project_id)


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

    _circle_right = relationship('RightCircleAssociation', backref='project', cascade="all, delete, delete-orphan")

    jobs = relationship('Job', backref='project')

    is_public = Column(Boolean, nullable=False)

    key = Column(Unicode(255), unique=True, default=setdefaultkey, nullable=False)

    download_key = Column(Unicode(255), unique=True, default=setdefaultkey, nullable=False)

    def _get_date(self):
        return self._created.strftime(constants.date_format)

    def _set_date(self, date):
        self._created = date

    created = synonym('_created', descriptor=property(_get_date, _set_date))

    # special methods
    def __repr__(self):
        return '<Project: id=%r, name=%r, key=%r>' % (self.id, self.name, self.key)

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
        Get a list of dict {Circle: [associated rights]}
        '''
        result = {}
        for cr in self._circle_right:
            rights = result.get(cr.circle, [])
            rights.append(cr.right)
            result[cr.circle] = rights

        return result

    @property
    def success_tracks(self):
        return [t for t in self.tracks if t.status == constants.SUCCESS]

    @property
    def get_tracks(self):
        return ', '.join([track.name for track in self.success_tracks])

    @property
    def circles(self):
        res = []
        for cr in self._circle_right:
            res.append(cr.circle)
        return res

    @property
    def shared_circles(self):
        ids = []
        cs = []
        for cr in self._circle_right:
            c = cr.circle
            if c.id not in ids:
                ids.append(c.id)
                cs.append(c)
        return cs

    @property
    def get_circle_with_right_display(self):
        '''
        Get a list of groups with rights associated
        in a suitable manner for display: Circle (associated rights) )
        '''
        crs = self.circles_with_rights
        result = []
        for circle, rights in crs.items():
            result.append('%s (%s)\n' % (circle.name, ', '.join([right.name for right in rights])))
        return ', '.join(result)

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
    public = Column(Boolean, default=True)
    default_tracks = relationship('Track', secondary=default_track_table)
    users = relationship('User', secondary=sequence_users_table)

    def __repr__(self):
        return '<Sequence: id=%r, name=%r, species_id=%r>' % (self.id, self.name, self.species_id)

    def __str__(self):
        return self.name


class Species(DeclarativeBase):
    '''
    Species.
    '''
    __tablename__ = 'Species'
    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    # relation
    sequences = relationship("Sequence", backref="species")

    def __repr__(self):
        return '<Species: id=%r, name=%r>' % (self.id, self.name)

    def __str__(self):
        return self.name


class Task(DeclarativeBase):
    __tablename__ = "celery_taskmeta"

    id = Column('id', Integer, Seq('task_id_sequence'), primary_key=True, autoincrement=True)
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
    sha1 = Column(Unicode(255), unique=True, nullable=True)
    _last_access = Column(DateTime, default=datetime.now, nullable=False)
    path = Column(Unicode, nullable=True)

    task_id = Column(VARCHAR(255), nullable=True)
    task = relationship('Task', uselist=False, primaryjoin='Input.task_id == Task.task_id', foreign_keys='Task.task_id')

    parent_id = Column(Integer, ForeignKey('Input.id'), nullable=True)
    children = relationship("Input")

    # special methods
    def __repr__(self):
        return '<Input: id=%r, sha1=%r, task_id=%s>' % (self.id, self.sha1, self.task_id)

    def __unicode__(self):
        return self.sha1

    def _get_last_access(self):
        return self._last_access.strftime(constants.date_format)

    def _set_last_access(self, date):
        self._last_access = date

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
            return 'RUNNING'
        return self.task.status

    @property
    def traceback(self):
        if self.task is None:
            return ''
        return self.task.traceback


class Track(DeclarativeBase):
    '''
    Represent a track on the view.
    '''
    __tablename__ = 'Track'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    _name = Column(Unicode(255), nullable=False)
    _created = Column(DateTime, nullable=False, default=datetime.now)
    _last_access = Column(DateTime, default=datetime.now, nullable=False)
    input_id = Column(Integer, ForeignKey('Input.id', ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=True)
    input = relationship('Input', backref='tracks', primaryjoin='Input.id == Track.input_id')
    #input = relationship('Input', backref='tracks')
    sequence_id = Column(Integer, ForeignKey('Sequence.id', ondelete="CASCADE"), nullable=False)
    sequence = relationship("Sequence")

    parameters = Column(JSONEncodedDict, nullable=True)
    visualization = Column(VARCHAR(255), default='not determined')

    output_directory = Column(Unicode, nullable=True)

    task_id = Column(VARCHAR(255), nullable=True)
    task = relationship('Task', uselist=False, primaryjoin='Track.task_id == Task.task_id', foreign_keys='Task.task_id')

    def __repr__(self):
        return '<Track: id=%r, name=%r, created=%r, vizu=%r, user_id=%r, sequence_is=%r, parameters=%s>' % (self.id, self.name, self.created, self.vizu, self.user_id, self.sequence_id, self.parameters)

    def __unicode__(self):
        return self.name

    def _get_date(self):
        return self._created.strftime(constants.date_format)

    def _set_date(self, date):
        self._created = date

    def _get_last_access(self):
        return self._last_access.strftime(constants.date_format)

    def _set_last_access(self, date):
        self._last_access = date

    def _get_name(self):
        return self._name

    def _set_name(self, value):
        if self.parameters is not None:
            if 'key' in self.parameters:
                self.parameters['key'] = value
                self.parameters['label'] = value
        self._name = value

    @property
    def status(self):
        if self.task is None:
            return 'PENDING'
        return self.task.status

    @property
    def traceback(self):
        if self.task is None:
            return ''
        return self.task.traceback

    @property
    def vizu(self):
        self.visualization

    @property
    def tmp(self):
        return False

    @property
    def tiny_date(self):
        return self._created.strftime(constants.tiny_date_format)

    created = synonym('_created', descriptor=property(_get_date, _set_date))
    last_access = synonym('_last_access', descriptor=property(_get_last_access, _set_last_access))
    name = synonym('_name', descriptor=property(_get_name, _set_name))

    @property
    def accessed(self):
        '''
        Update the field 'last_access' by the current time
        '''
        self._set_last_access(datetime.now())

    @property
    def path(self):
        return self.input.path

    @property
    def rel_path(self):
        return self.input.sha1 + '.sql'


class TrackParameters(DeclarativeBase):
    '''
    Track parameters.
    Based on the type, parameters can be different.
    '''
    __tablename__ = 'TrackParameters'
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
        d = {'url': self.url, 'label': self.label, 'type': self.type,
                'gdv_id': self.track_id, 'key': self.key, 'date': self.track.tiny_date}
        if self.color:
            d['color'] = self.color
        return d

    def build_parameters(self):
        self.url = os.path.join(self.track.input.sha1, '{refseq}', constants.track_data)
        self.label = self.track.name
        self.key = self.track.name
        '''
        RELATIONAL = 'relational'
        SIGNAL = 'signal'
        FEATURES = 'features'
        '''
        if self.track.vizu == constants.RELATIONAL or self.track.vizu == constants.FEATURES:
            self.type = constants.FEATURE_TRACK
        else:
            self.type = constants.IMAGE_TRACK


class Result(DeclarativeBase):
    """
    Represent each result of a bioscript job
    """
    __tablename__='JobResult'
    id = Column(Integer, autoincrement=True, primary_key=True)
    job_id = Column(Integer, ForeignKey('Job.id',  onupdate='CASCADE', ondelete="CASCADE"),
        nullable=False)
    job = relationship('Job', uselist=False, backref='results', cascade='delete')
    name = Column(Unicode(255), nullable=False)
    rtype = Column(Unicode(255), nullable=False)
    rpath = Column(Unicode(255), nullable=False)
    rmore = Column(Unicode(255), nullable=True)
    track_id = Column(Integer, ForeignKey('Track.id',  onupdate='CASCADE', ondelete="CASCADE"),
        nullable=True)


class Job(DeclarativeBase):
    '''
    Represent external jobs submitted by GDV to BioScript.
    '''
    __tablename__ = 'Job'

    #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)

    _created = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=True)

    #task_id = Column(Integer, ForeignKey('celery_taskmeta.id', ondelete="CASCADE"), nullable=False)
    #task = relationship('Task', uselist=False, backref='job')
    #task_id = Column(VARCHAR(255))
    #task = relationship('Task', uselist=False, primaryjoin='Job.task_id == Task.task_id', foreign_keys='Task.task_id')
    status = Column(Unicode(255))
    # external task_id from bs
    ext_task_id = Column(VARCHAR(255), unique=True)
    # the result of the job
    data = Column(Text())
    # the job "type": image, file, ...
    output = Column(VARCHAR(255))

    def _get_date(self):
        return self._created.strftime(constants.date_format)

    def _set_date(self, date):
        self._created = date

    created = synonym('_created', descriptor=property(_get_date, _set_date))

    @property
    def traceback(self):
        return self.data

    @property
    def get_type(self):
        return self.parameters.type

    def __repr__(self):
        return 'Job < id: %s, name %s, desc: %s, data: %s , , output: %s>' % (
                        self.id, self.name, self.description, self.data, self.output)

    @property
    def output_display(self):
        if self.output == constants.JOB_IMAGE:
            return 'Image'
        if self.output == constants.JOB_TRACK:
            return 'Track'
        return self.output


class Location(DeclarativeBase):
    '''
    Represent the Location a Selection can have.
    '''
    __tablename__ = 'Location'
    id = Column(Integer, autoincrement=True, primary_key=True)
    chromosome = Column(Text(255), nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    description = Column(Text(), nullable=True)
    selection_id = Column(Integer, ForeignKey('Selection.id',  onupdate='CASCADE', ondelete="CASCADE"),
                           nullable=False)

    def __repr__(self):
        return '<Location %s chr: %s, start: %s, end: %s, description: %s>' % (self.id, self.chromosome, self.start, self.end, self.description)


class Selection(DeclarativeBase):
    '''
    Represent all selections that are submitted to GDV.
    '''
    __tablename__ = 'Selection'
    id = Column(Integer, autoincrement=True, primary_key=True)
    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=False)
    description = Column(Text(), nullable=True)
    color = Column(Unicode(255), nullable=True)
    locations = relationship('Location', uselist=True, backref='selection', cascade='delete')
