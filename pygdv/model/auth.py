# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the pygdv application,
though.

"""
import uuid

from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relationship, synonym

from pygdv.model import DeclarativeBase, metadata, DBSession
from pygdv.lib.util import obfuscate_email
date_format = "%A %d. %B %Y %H.%M.%S"

__all__ = ['User', 'Group', 'Permission']


#
# Association tables
#
 
# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table('GroupPermissions', metadata,
    Column('group_id', Integer, ForeignKey('Group.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('Permission.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table('UserGroup', metadata,
    Column('user_id', Integer, ForeignKey('User.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('Group.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

user_circle_table = Table('user_circle', metadata,
    Column('user_id', Integer, ForeignKey('User.id',
         ondelete="CASCADE"), primary_key=True),
    Column('circle_id', Integer, ForeignKey('Circle.id',
         ondelete="CASCADE"), primary_key=True)
)


#
# *The auth* model itself
#
 
class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.
    Only the ``group_name`` column is required by :mod:`repoze.what`.
    """
    __tablename__ = 'Group'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    _created = Column(DateTime, default=datetime.now, nullable=False)
    # relations
    users = relationship('User', secondary=user_group_table, backref='groups')
    
    
    # special methods
    def __repr__(self):
        return '<Group: name=%r>' % self.name
    def __unicode__(self):
        return self.name
    @property
    def get_users(self) :
        return self.users
    @property  
    def get_permissions(self):
        return self.permissions
    
    def _get_date(self):
        return self._created.strftime(date_format);
        
    def _set_date(self,date):
        self._created=date

    created = synonym('_created', descriptor=property(_get_date, _set_date))
    
    def has_permission(self,tag):
        '''
        Return true if the group has the permission specified
        '''
        for perm in self.permissions:
            if perm.name == tag : return True
            return False
# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class User(DeclarativeBase):
    """
    User definition.
    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """
    __tablename__ = 'User'
   
    def setdefaultkey(self):
        uid = str(uuid.uuid4())
        while DBSession.query(User).filter(User.key == uid).first():
            uid = str(uuid.uuid4())
        return uid
            
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    firstname = Column(Unicode(255), nullable=False)
    _email = Column(Unicode(255), unique=True, nullable=False, info={'rum': {'field':'Email'}})
    _created = Column(DateTime, default=datetime.now, nullable=False)
    key = Column(Unicode(255), unique=True,default=setdefaultkey, nullable=False)
    
    tracks = relationship('Track', backref='user')
    projects = relationship('Project', backref='user')
    jobs = relationship('Job', backref='user')
    circles = relationship('Circle', secondary=user_circle_table, backref='users')
    
    
    def _get_date(self):
        return self._created.strftime(date_format);
        
    def _set_date(self,date):
        self._created=date

    created = synonym('_created', descriptor=property(_get_date, _set_date))
 
    @property
    def projects_(self):
        pass
    # email and user_name properties
    def _get_email(self):
        return self._email
 
    def _set_email(self, email):
        self._email = email.lower()
 
    email = synonym('_email', descriptor=property(_get_email, _set_email))
 
    # class methods
    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter(cls.email == email).first()
 
    # non-column properties
    def validate_login(self, password):
        print 'validate_login' 
        print password        
    
    @property
    def obsfuscated_email(self):
        return obfuscate_email(self.email)
    
    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    
    def permissions_for_group(self, group_id):
        '''
        Return permissions granted for the group.
        '''
        for g in self.groups:
            if g.id == group_id :
                return g.permissions
        return []
    def __repr__(self):
        return '<User: id=%r, name=%r, email=%r, key=%r>' % (self.id, self.name, self.email,self.key)
 
    def __unicode__(self):
        return self.__str__()
  
    def __str__(self):
        return self.short()
 
    def short(self):
        return '%s %s' % (self.name, self.firstname)
    def long(self):
        return '%s %s (%s)' % (self.name, self.firstname, self.obsfuscated_email)
 
class Permission(DeclarativeBase):
    '''
    This class handle the ``permissions`` existing in the application
 
    '''
    __tablename__ = 'Permission'
    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(63), unique=True, nullable=False)
    description = Column(Unicode(255), nullable=False)

    # relations
    groups = relationship(Group, secondary=group_permission_table, backref='permissions')
    
    # special methods
    def __repr__(self):
        return '<Permission: name=%r>' % self.name
    def __unicode__(self):
        return '%s (%s)' %(self.name, self.description)





