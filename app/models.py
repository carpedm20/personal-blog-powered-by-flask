from app import db
from app import app
import flask.ext.whooshalchemy as whooshalchemy

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

comments = db.Table('comments',
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class Post(db.Model):
    __tablename__ = 'post'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(1000))
    coded_body = db.Column(db.String(2000))
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('posts', lazy='dynamic'))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % (self.name)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(10))
    body = db.Column(db.String(500))

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return '<Comment %r>' % (self.body)

whooshalchemy.whoosh_index(app, Post)

from config import WHOOSH_ENABLED

if WHOOSH_ENABLED:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, Post)
