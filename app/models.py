from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from flask import current_app


class Permission:
    SUBJECTS = 1
    CHATS = 2
    POST = 4
    CREATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True) 
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Student': [Permission.SUBJECTS, Permission.CHATS],
            'Professor': [Permission.SUBJECTS, Permission.CHATS, Permission.POST, Permission.CREATE],
            'Administrator': [Permission.SUBJECTS, Permission.CHATS,
                              Permission.POST, Permission.CREATE,
                              Permission.ADMIN]
        }
        default_role = 'Student'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False) 
    last_name = db.Column(db.String(80), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    about_me = db.Column(db.Text())
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['COLLAB_ADMIN']:
                self.role = db.session.query(Role).filter_by(name='Admin').first()
            if self.role is None:
                self.role = db.session.query(Role).filter_by(default=True).first()


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()
    
    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        '''&s={size}&d={default}&r={rating}'''
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'
    
    def can(self, permission):
        return self.role.has_permission(permission)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


chat_members = db.Table('chat_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('chat_room_id', db.Integer, db.ForeignKey('chat_rooms.id')),
    prevent_existing=True
)


class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, default=None) 
    is_private = db.Column(db.Boolean, default=False)
    members = db.relationship('User', secondary='chat_members', backref='chat_rooms')


    @staticmethod 
    def get_or_create_private_chat(user1, user2):
        user_ids = sorted([user1.id, user2.id])

        rooms = ChatRoom.query.join(chat_members).filter(
            chat_members.c.user_id.in_(user_ids),
            ChatRoom.is_private.is_(True)
        ).all()

        for room in rooms:
            member_ids = sorted([u.id for u in room.members])
            if member_ids == user_ids:
                return room

        room = ChatRoom(is_private=True)
        room.members.append(user1)
        room.members.append(user2)
        db.session.add(room)
        db.session.commit()
        return room


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'))

    sender = db.relationship('User', backref='messages')
    room = db.relationship('ChatRoom', backref='messages')
