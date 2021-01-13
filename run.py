#-*- coding:utf-8 -*- 
from flask import Flask, render_template, request, escape, send_file, url_for, session, redirect, app
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
#from vsearch import search4letters
from datetime import timedelta
import time
import os

#powershell 권한 -
#Set-ExecutionPilicy Unrestricted -Scope CurrentUser



def log_save2(req: 'flask_request', res: str) -> None:
    with open('uploadlogfile.log', 'a') as log2:
        ip = request.remote_addr
        print(req, ip, res, '</br>', file=log2)

def log_request(req : 'flask_request', res: str) -> None:
    with open('asearch.log', 'a') as log3:
        ip = request.remote_addr
        print(req, ip, res, '</br>', file= log3)

def check_a(filename, path):
    find = 0
    for x in path:
        if (x==filename) :
            find = 1
    return (find)

def check_b():
    platform = request.user_agent.platform
    print (platform)
    if platform == 'android' or platform == 'iphone':
        return 0
    else :
        return 1

app = Flask(__name__, static_url_path = '/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
db = SQLAlchemy(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique = False)

    def __init__(self, nickname, username, password, email):
        self.nickname = nickname
        self.username = username
        self.password = password
        #self.set_password(password)
        self.email = email
     
    def set_password(self, password):
        self.password = generate_password_hash('password')
        print(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User( '{self.username}', '{self.email}')>"

#text return
@app.route('/', methods=['GET', 'POST'])
def defalut():
    if check_b() == 1:
        if not session.get('logged_in'):
            session['logged_in'] = False
            return render_template('main.html')
        else:
            result = '%s' % escape(session['name'])
            name = session['username']
            if os.path.isdir("./static/profile/" + session['username']):
                isthere = True
            else :
                isthere = False
            return render_template('main.html', showname = result, isthere = isthere, name = name)
    if check_b() == 0:
        if not session.get('logged_in'):
            session['logged_in'] = False
            return render_template('mobile.html')
        else:
            result = '%s' % escape(session['name'])
            name = session['username']
            if os.path.isdir("./static/profile/" + session['username']):
                isthere = True
            else :
                isthere = False
            return render_template('mobile.html', showname = result, isthere = isthere, name = name)
@app.route("/mobile")
def test():
    if not session.get('logged_in'):
        session['logged_in'] = False
        return render_template('mobile.html')
    else:
        result = '%s' % escape(session['name'])
        name = session['username']
        if os.path.isdir("./static/profile/" + session['username']):
            isthere = True
        else :
            isthere = False
        return render_template('mobile.html', showname = result, isthere = isthere, name = name)

@app.route("/mypage")
def mypage():
    if session['logged_in'] is None  or session['logged_in'] == False:
        session['loggen_in'] = False
        backpage = "mypage"
        return render_template('login.html', backpage=backpage)
    else:
        result = '%s' % escape(session['name'])
        if os.path.isdir("./LoginUpload/" + session['username']) == False:
            os.mkdir('./LoginUpload/' + session['username'])
        myfiles = os.listdir("./LoginUpload/" + session['username'])
        myfiles = len(myfiles)
        name = session['username']
        if os.path.isdir("./static/profile/" + session['username']):
            isthere = True
        else :
            isthere = False
        return render_template('html1.html', showname = result, myfiles = myfiles, name = name, isthere = isthere)

@app.route("/profileupload")
def profile():
    if session['logged_in'] == False:
        return render_template('login.html')
    else:
        return render_template('pfupload.html')
@app.route("/profileuploading", methods = ['GET','POST'] )
def pfupload():
    if request.method == 'POST':
        f = request.files['file']
        if (os.path.isdir('./static/profile/' + session['username']) == False):
            os.mkdir('./static/profile/' + session['username'])
        if f.filename.rsplit('.', 1)[1] == 'png':
            f.save('./static/profile/' + session['username'] + '/profile.png')
        else:
            return 'png 확장자가 아닙니다.'
        return 'upload가 성공적으로 완료되었습니다.'
@app.route("/search", methods = ['GET', 'POST'])
def search():
    yourinput = request.args.get('input')
    log_request(request, yourinput)
    return render_template('search.html', result = yourinput)

#youtube return
@app.route("/movie")
def hello2():
	return render_template('video.html')

@app.route("/content")
def content():
    return render_template('content.html')
#view log2
@app.route('/adminlog')
def view_th_log2() -> str:
    with open('uploadlogfile.log') as log2:
        contents = log2.read()
    return escape(contents)
@app.route('/searchlogs')
def view_th_log3() -> str:
    with open('asearch.log') as log3:
        contents = log3.read()
    return escape(contents)

#UPLOAD
@app.route('/upload')
def render_file():
    try:
        if session['logged_in'] is None:
            session['logged_in'] = False
        if session['logged_in'] == True:
            result = '%s' % escape(session['name'])
            return render_template('upload.html', showname = result)
        else :
            backpage = "render_file"
            return render_template('login.html', backpage = backpage)
    except:
        return '다시로그인'
@app.route('/fileUpload', methods = ['GET','POST'])
def upload_file():
    try:
        if request.method == 'POST':
            f = request.files['file']
            where = request.form['where']
            if where == 'my':
                if (os.path.isdir('./LoginUpload/' + session['username']) == False):
                    os.mkdir('./LoginUpload/' + session['username'])
                path = os.listdir('./LoginUpload/' + session['username'])
                if check_a(f.filename, path):
                    f.save('./LoginUpload/' + session['username'] + '/' + time.strftime('%y%m%d') + '-' + secure_filename(f.filename))
                else :
                    f.save('./LoginUpload/' + session['username'] + '/' + time.strftime('%y%m%d') + '-' + secure_filename(f.filename))
            elif where == 'nomy':
                f.save('./uploads/' + time.strftime('%y%m%d') + '-' + secure_filename(f.filename))
            log_save2(request, f.filename)
            result = '%s' % escape(session['name'])
            return render_template('upsuccess.html', showname = result)
    except:
        return ('파일 크기 제한은 500MB입니다.')


#list&download
@app.route("/downfile")
def downmain():
    files = os.listdir("./uploads")
    if session['logged_in'] == True:
        if (os.path.isdir('./LoginUpload/' + session['username']) == False):
            os.mkdir('./LoginUpload/' + session['username'])
        myfiles = os.listdir("./LoginUpload/" + session['username'])
        result = '%s' % escape(session['name'])
        return render_template('downfile.html', files = files, showname = result, myfiles = myfiles)
    else:
        files = os.listdir("./uploads")
        return render_template('downfile.html', files = files)

@app.route("/fileDown", methods = ['POST'])
def download():
    if request.method == 'POST':
        if session['logged_in'] == True:
            if os.path.isdir('./LoginUpload/' + session['username'] == False):
                os.mkdir('./LoginUpload/' + session['username'])
            files = os.listdir("./LoginUpload/" + session['username'])
            find = 0
            for x in files:
                if(x==request.form['file']):
                    find = 1
            if(find == 1):
                path = "./LoginUpload/" + session['username'] + "/"
                return send_file(path + request.form['file'], 
                attachment_filename = request.form['file'], 
                as_attachment=True)
            else:
                return request.form['file']
        else:
            files = os.listdir("./uploads")
            find = 0
            for x in files:
                if(x==request.form['file']):
                    find = 1
            if(find == 1):
                path = "./uploads/"
                return send_file(path + request.form['file'], 
                attachment_filename = request.form['file'], 
                as_attachment=True)
            else:
                return request.form['file']

@app.route("/deletefile", methods = ['POST'])
def deletefile():
    if request.method == 'POST':
        if session['logged_in'] == True:
            name = request.form['radio']
            path = "./LoginUpload/" + session['username'] + "/"
            os.remove(path + name)
            files = os.listdir("./uploads")
            myfiles = os.listdir("./LoginUpload/" + session['username'])
            result = '%s' % escape(session['name'])
            return render_template('deleted.html', files = files, showname = result, myfiles = myfiles)
        return redirect(url_for('login'))
    else :
        return render_template('main.html')

@app.route("/gallery")
def showimg():
    files = os.listdir("./static/poster")
    path = "./static/poster/"
    for i in range(len(files)):
        files[i] = path + files[i]
    filename = os.listdir("./static/poster")
    if session['username'] == 'admin':
        upload= 1
    else:
        upload =0
    return render_template('gallery.html', files = files, show = filename, upload = upload)

#UPLOAD
@app.route('/galleryupload')
def grender_file():
    try:
        if session['logged_in'] is None:
            session['logged_in'] = False
        if session['logged_in'] == True:
            result = '%s' % escape(session['name'])
            return render_template('gupload.html', showname = result)
        else :
            backpage = "grender_file"
            return render_template('login.html', backpage = backpage)
    except:
        return '다시로그인'
@app.route("/gupload", methods = ['GET','POST'] )
def gupload():
    try:
        if request.method == 'POST':
            f = request.files['file']
            if f.filename.rsplit('.', 1)[1] == 'png' or f.filename.rsplit('.', 1)[1] == 'jpg' or f.filename.rsplit('.', 1)[1] == 'jpeg':
                f.save('./static/poster/'+ secure_filename(f.filename))
            else:
                return 'png, jpg, jpeg 확장자가 아닙니다.'
            return 'upload가 성공적으로 완료되었습니다.'
    except:
        return ('파일 크기 제한은 500MB입니다.')

#list&download
@app.route("/gdownfile")
def gdownmain():
    files = os.listdir('./static/poster/')
    if session['logged_in'] == True:
        myfiles = os.listdir('./static/poster/')
        result = '%s' % escape(session['name'])
        return render_template('downfile.html', files = files, showname = result, myfiles = myfiles)
    else:
        files = os.listdir('./static/poster/')
        return render_template('gdownfile.html', files = files)

@app.route("/gdeletefile", methods = ['POST'])
def gdeletefile():
    if request.method == 'POST':
        if session['logged_in'] == True:
            name = request.form['radio']
            path = './static/poster/'
            os.remove(path + name)
            files = os.listdir('./static/poster/')
            myfiles = os.listdir('./static/poster/')
            result = '%s' % escape(session['name'])
            return render_template('gdeleted.html', files = files, showname = result, myfiles = myfiles)
        return redirect(url_for('login'))
    else :
        return render_template('main.html')

#patch
@app.route("/patch")
def patch():
    return render_template('patch.html')

#404 
@app.errorhandler(404)
def page_not_found(error):
	return render_template('nopage.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        #hash = generate_password_hash(passw)
        try:
            name = request.form['username']
            session['username'] = request.form['username']
            passw = request.form['password']
            data = User.query.filter_by(username=name, password = passw).first()
            if data is None:
                return '존재하지 않는 계정입니다.'
            #elif not check_password_hash(data.password, passw):
                #return '비밀번호를 틀림'
            else : 
                session['logged_in'] = True
                session['name'] = data.nickname
                return redirect(url_for(request.form['backpage']))
        #try:
            '''data = User.query.filter_by(username=name).first()
            if data is not None:
                if check_password_hash(data.password, passw):
                    session['logged_in'] = True
                    return redirect(url_for('defalut'))
                else:
                    u = User(username ='efrona', password = 'abcde', email = 'abcd@ad')
                    db.session.add(u)
                    db.session.commit()
                    u = User.query.filter_by(username='efrona').one()
                    print(u.password)
                    # pbkdf2:sha1:1000$w9jx4Egp$b420d784ac6ad0575e4a9a908bb4679826e56f5f
                    print(u.check_password('abcde'))
                    print(check_password_hash(u.password, 'abcde'))
                    # True
                    print('a')
                    hasha = generate_password_hash('abcd')
                    print('b')
                    print(check_password_hash(hasha, 'abcd'))
                    return 'abcde'
                #return User.nickname()
            else:
                return '존재하지 않음'''
        except:
            return redirect(url_for('defalut'))
            #return User.nickname()

@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first() is not None:
            return '아이디중복'
        if User.query.filter_by(nickname=request.form['nickname']).first() is not None:
            return '닉네임중복'
        new_user = User(nickname = request.form['nickname'], username=request.form['username'], password=request.form['password'], 
            email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')

@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = None
    session['name'] = None
    session['username'] = None
    return redirect(url_for('defalut'))
    
if __name__ == '__main__':
	db.create_all()
	app.secret_key = "123123123"
	app.run(host='0.0.0.0', port=80, debug=True)
