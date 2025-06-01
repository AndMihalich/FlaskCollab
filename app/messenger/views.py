from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .. import db
from ..models import ChatRoom, Message, User, Role, chat_members

from . import messenger as mess
from .forms import MessageForm, StartChatForm

@mess.route('/', methods=['GET', 'POST'])
@login_required
def chats():
    form = StartChatForm()
    rooms = ChatRoom.query\
        .join(chat_members)\
        .filter(chat_members.c.user_id == current_user.id)\
        .all()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('User not found.', 'danger')
        elif user.id == current_user.id:
            flash('You cannot chat with yourself.', 'warning')
        else:
            room = ChatRoom.get_or_create_private_chat(current_user, user)
            return redirect(url_for('mess.chat_room', room_id=room.id))

    return render_template('mess/chat_list.html', rooms=rooms, form=form)

@mess.route('/chat/<int:room_id>', methods=['GET', 'POST'])
@login_required
def chat_room(room_id):
    room = ChatRoom.query.get(room_id)
    messages = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp.asc()).all()
    form = MessageForm()

    
    companion = None
    if room and room.is_private:
        members = [u for u in room.members if u.id != current_user.id]
        if members:
            companion = members[0]

    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            room_id=room.id
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('mess.chat_room', room_id=room.id))

    return render_template('mess/chat_room.html', room=room, messages=messages, form=form, companion=companion)

