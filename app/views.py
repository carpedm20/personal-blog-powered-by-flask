# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from app import app, db
from models import Post
from models import Tag
from models import Comment
from datetime import datetime
from config import POSTS_PER_PAGE

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

import re

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])

def show_posts(page = 1):
    posts = Post.query.paginate(page, POSTS_PER_PAGE, False).items
    has_next = Post.query.paginate(page, POSTS_PER_PAGE, False).has_next
    """
    entries = []

    for post in posts:
	entry = post.body

	r=re.compile(r'\[code lang="(?P<lang>.+)"\](?P<code>.+)\[/code\]')
	m=r.match(entry)

	if m is not None:
	    lang = m.group('lang')
	    code = m.gropu('code')

  	    lexer = get_lexer_by_name(lang, stripall=True)
	    code = highlight(code, lexer, HtmlFormatter())

	    front = entry[:entry.find('[code')]
	    back = entry[entry.find('[/code]') + 7:]
	    entry = front + code + back

	entries.append(entry)
    """
    return render_template('show_posts.html', posts=posts, index=page, has_next = str(has_next))

#@app.route('/tag')
@app.route('/tag', methods=['POST'])
def show_tagged_posts():
    posts = db.session.query(Post).filter(Post.tags.any(name=request.form['name'])).all()
    #posts = db.session.query(Post).filter(Post.tags.any(name=name)).all()
    return render_template('show_posts.html', posts=posts, index=1)

@app.route('/post', methods = ['GET','POST'])
@app.route('/post/<int:id>', methods = ['GET', 'POST'])
def show_post(id = 1):
    post = db.session.query(Post).filter_by(id = id).first()
    
    return render_template('show_post.html', post = post)

@app.route('/archives', methods = ['GET','POST'])
def show_archives():
    posts = Post.query.all()

    archives=[]
    for post in posts:
	archive = {}
	archive['title'] = post.title
	archive['id'] = post.id
	archive['timestamp'] = post.timestamp
	archive['tags'] = post.tags
	archive['year'] = post.timestamp

	archives.append(archive)

    print archives

    return render_template('show_archives.html', archives = archives, id="123")

@app.route('/about', methods = ['GET','POST'])
def show_about():
    return render_template('about.html')

@app.route('/gallery', methods = ['GET','POST'])
def show_gallery():
    return render_template('gallery.php')

@app.route('/add', methods=['POST'])
def add_post():
    page = int(request.form['index'])
    posts = Post.query.paginate(page, POSTS_PER_PAGE, False).items
    has_next = Post.query.paginate(page, POSTS_PER_PAGE, False).has_next

    if request.form['title'] == "" or request.form['body'] == "":
        flash('You have to fill all the inputs!','error')
        return render_template('show_posts.html', posts=posts, index=page, has_next = str(has_next), title=request.form['title'], body=request.form['body'], tags = request.form['tags'])

    if not session.get('logged_in'):
        abort(401)

    entry = request.form['body']

    r=re.compile(r'.*\[code (?P<lang>.{1,10})\](?P<code>.+)\[/code\].*', re.DOTALL)
    m=r.match(entry)

    if m is not None:
        lang = m.group('lang')
        code = m.group('code')

        lexer = get_lexer_by_name(lang, stripall=True)
        code = highlight(code, lexer, HtmlFormatter())

        front = entry[:entry.find('[code')]
        back = entry[entry.find('[/code]') + 7:]
        new_entry = front + code + back

	post = Post(title = request.form['title'], body = entry, coded_body = new_entry, timestamp = datetime.utcnow())
    else:
	post = Post(title = request.form['title'], body = entry, coded_body = '', timestamp = datetime.utcnow())

    if request.form['tags'].strip() != '':
        tags = request.form['tags'].split(',')
	for tag in list(set(tags)):
            if tag.strip() == '':
	        continue
            post.tags.append(Tag(tag.strip()))

    db.session.add(post)
    db.session.commit()
    flash('New post was successfully posted','normal')

    posts = Post.query.paginate(page, POSTS_PER_PAGE, False).items

    return render_template('show_posts.html', posts=posts, index=page, has_next = str(has_next))

@app.route('/edit', methods=['POST'])
def edit_post():
    page = int(request.form['index'])
    posts = Post.query.paginate(page, POSTS_PER_PAGE, False).items
    has_next = Post.query.paginate(page, POSTS_PER_PAGE, False).has_next

    if request.form['title'] == "" or request.form['body'] == "":
        flash('You have to fill all the inputs!','error')
        return render_template('show_posts.html', posts=posts, index=page, has_next = str(has_next))

    if not session.get('logged_in'):
        abort(401)

    post = Post.query.filter_by(id = request.form['id']).first()

    entry = request.form['body']

    r=re.compile(r'.*\[code (?P<lang>.{0,10})\](?P<code>.+)\[/code\].*', re.DOTALL)
    m=r.match(entry)

    if m is not None:
        lang = m.group('lang')
        code = m.group('code')

        lexer = get_lexer_by_name(lang, stripall=True)
        code = highlight(code, lexer, HtmlFormatter())

        front = entry[:entry.find('[code')]
        back = entry[entry.find('[/code]') + 7:]
        new_entry = front + code + back

	print new_entry

	post.coded_body = new_entry
    else:
	print "Nooooooooooooooooooooooooooo"
	post.coded_body = ''

    post.title = request.form['title']
    post.body = request.form['body']

    while len(post.tags) is not 0:
        for tag in post.tags:
            post.tags.remove(tag)
    if request.form['tags'].strip() != '':
        tags = request.form['tags'].split(',')
        for tag in list(set(tags)):
            if tag.strip() == '':
	        continue
            post.tags.append(Tag(tag.strip()))
    db.session.commit()
    flash('Post was successfully edited','normal')

    return render_template('show_posts.html', posts=posts, index=page, has_next = str(has_next))

@app.route('/delete', methods=['POST'])
def delete_post():
    if not session.get('logged_in'):
        abort(401)

    post = Post.query.filter_by(id = request.form['id']).first()
    db.session.delete(post)
    db.session.commit()
    flash('Post was successfully deleted','normal')

    return redirect(url_for('show_posts'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in','normal')

            return redirect(url_for('show_posts'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out','normal')

    return redirect(url_for('show_posts'))
