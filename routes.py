from flask import (Flask, render_template,
                   request, session, redirect, url_for,
                   flash, jsonify, send_file)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from forms import (SignupForm, LoginForm,
                   UploadForm)
from urllib.parse import (unquote, unquote_plus)
from models.users import User
from models.database import Database
from models.categories import Category
from models.search import Hashtags, words
from models.images import Image as ImageC
from uuid import uuid4
from string import punctuation
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64
import re

app = Flask(__name__)

Database.initialize('Atypical')

@app.context_processor
def inject_stage_and_region():
    categories = Category.getAllCategories()
    categories = [cat for cat in categories]
    return dict(categories=categories)


app.config['SECRET_KEY'] = '{}'.format(uuid4().hex)


@app.before_request
def make_session_permanent():
    session.permanent = True


def getCUserData():
    secret_cookie = session.get('_cu')
    return User.verifySession(secret_cookie)


app.jinja_env.globals.update(getCUserData=getCUserData)

bootstrap = Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
moment = Moment(app)


def compressImage(base64str, lossless=False, size=(720, 720), quality=35):
    img_data = base64.b64decode(base64str)
    f = open('temp', 'wb+')
    f.write(img_data)
    f.seek(0)
    image = Image.open(f)
    if not lossless:
        image.thumbnail(size, Image.ANTIALIAS)
    image = image.convert('RGB')
    buffered = BytesIO()
    image.save(buffered, format="JPEG", optimize=True, quality=quality)
    encodedImg = base64.b64encode(buffered.getvalue()).decode()
    f.close()
    del img_data
    del f
    del buffered
    del image
    return encodedImg


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/profile/<string:username>")
@app.route("/profile/")
def profile(username=None):

    if session.get('_cu', None) is None and username is not None:
        if any(char in punctuation.replace('_', '') for char in username):
            flash('Invalid Username!')
            return redirect(url_for('index'))
        else:
            current_usr = {}

    elif username is None and session.get('_cu', None):
        return redirect(f'/profile/{getCUserData().get("username")}', 302)

    elif username and session.get('_cu', None):
        # if getCUserData().get('username') == username:
        current_usr = getCUserData()

    dataToDisplay = User.getUserByUsername(username)
    if dataToDisplay:
        return render_template('profile.html',
                               userData=dataToDisplay,
                               current_usr=current_usr,
                               current_time=datetime.utcnow())
    else:
        return redirect('/'), 404, {"Refresh": "2; url=/"}


@app.route("/post/<string:img_id>", methods=['GET'])
@app.route("/post/<string:vote>", methods=['POST'])
@app.route("/post/<string:updDisc>", methods=['PUT'])
@app.route("/post/<string:remove>", methods=['DELETE'])
@app.route("/post/")
def post(img_id=None, vote=None, updDisc=None, remove=None):

    if request.method == 'GET':
        if session.get('_cu', None) is None and img_id is not None:
            if any(char in punctuation.replace('_', '') for char in img_id):
                flash('Invalid img_id!')
                return redirect(url_for('index'))
            else:
                current_usr = {}

        elif img_id is None:
            return redirect(url_for('index'))

        elif img_id and session.get('_cu', None):
            current_usr = getCUserData()

        upvoted = downvoted = False

        dataToDisplay = User.getImagebyImgID(img_id)
        if session.get('_cu'):
            if current_usr.get('_id') in dataToDisplay.get('upvotes'):
                upvoted = True
            if current_usr.get('_id') in dataToDisplay.get('downvotes'):
                downvoted = True

        if dataToDisplay:
            return render_template('post.html',
                                   ImgData=dataToDisplay,
                                   current_usr=current_usr,
                                   getUserData=User.getUserByID,
                                   current_time=datetime.utcnow(),
                                   upvoted=upvoted,
                                   downvoted=downvoted)
        else:
            flash('Invalid Post ID')
            return redirect(url_for('index'))

    elif request.method == 'POST':
        img_id = request.get_data(as_text=True).split('=')[1]

        if len(img_id) != 32:
            return jsonify({'error': 'Invalid Request!'})

        if vote == 'upvote':
            result = User.vote(session.get('_cu'), img_id=img_id)
        else:
            result = User.vote(session.get('_cu'), img_id=img_id,
                               upvote=False)
        if result is True:
            return jsonify({'success': True})
        else:
            if result == -1:
                flash('User who posted this image not found!')
                flash('Upvoting/Downvoting and Commenting is Di\
sabled for this Post!')
                return jsonify({'error': '-1'})
            elif result == -2:
                flash('Please Login to Upvote/Downvote/Comment')
                return jsonify({'error': '-2'})
            elif result == -3:
                flash('Invalid Post ID')
                return jsonify({'error': '-3'})

    elif request.method == 'PUT':
        desc = request.json
        if desc:
            usr = getCUserData()
            img_id = desc.get('img_id')
            description = desc.get('desc')

            if any(char in img_id for char in punctuation):
                flash('Invalid Post ID')
                return jsonify({'error': '-1'})

            if len(img_id) != 32:
                flash('Invalid Post ID')
                return jsonify({'error': '-2'})

            if usr:
                img = User.getImagebyImgID(img_id)
                if img.get('userID') == usr.get('_id'):
                    if User.changeDescription(description, img_id):
                        return jsonify({'success': '1'})
                    else:
                        return jsonify({'error': '-1'})
                else:
                    flash('Invalid Request!')
                    return jsonify({'error': -2})
            else:
                flash('Please Login to Make Changes!')
                return jsonify({'error': -2})
        else:
            return jsonify({'error': 'no json'})
    else:
        return jsonify({'error': 'invalid request'})


@app.route("/images", methods=['POST'])
@app.route("/images/search", methods=['POST'])
def displayImages():
    if request.method != 'POST':
        return redirect('/', 302)
    else:
        data = request.json
        print(data)
        if not data.get('skip') is None:
            skip = data.get('skip', 0)
            cat = data.get('category')
            username = data.get('username')
            search_query = data.get('search')
            # print(search_query)
            usr = {}
            isProfile = False
            if 'int' in str(type(skip)) and skip < 10000:
                if cat and cat.replace(' ', '').isalpha() and len(cat) < 100:
                    imgs = ImageC.GetImgsByCategory(skip_=skip,
                                                    limit_=10,
                                                    category=cat)

                elif username and len(username) < 100:
                    usr = User.getUserByUsername(username)
                    if usr:
                        imgs = ImageC.GetAllImages(query={
                            'userID': usr.get('_id')},
                            skip_=skip, limit_=10, sortField='_id')

                        isProfile = True
                        
                elif search_query:
                    query = words(search_query)
                    squery=[]
                    for q in range(len(query)):
                        squery.append(
                            {'tags': {'$all': query[:q+1]}}
                        )
                    imgs = list(ImageC.GetAllImages(
                        query = {
                            "$or": squery
                        },
                        skip_=skip,
                        limit_=10
                    ))
                    print(f'images for search : {squery}')
                else:
                    imgs = ImageC.GetAllImages(skip_=skip, limit_=10)

                final_imgs = []

                for img in imgs:
                    description = img.get('description')
                    hasProfilePicture = True

                    if not usr:
                        usr = User.getUserByID(img.get('userID'))

                    if not isProfile:
                        description = None

                    if usr:
                        if not usr.get('profilePicture'):
                            hasProfilePicture = False
                            if usr.get('gender') == 'M':
                                usr.update({
                                    'profilePicture': url_for('static',
                                                              filename='\
images/profile/profile_male.jpg')
                                })
                            else:
                                usr.update({
                                    'profilePicture': url_for('static',
                                                              filename='\
images/profile/profile_female.jpg')
                                })
                                
                        # print(img.get('img_id'))
                        final_imgs.append({
                            'img_id': img.get('img_id'),
                            'category': img.get('categories'),
                            'name': usr.get('name').title(),
                            'profilePicture': str(usr.get('profilePicture')),
                            'description': description,
                            'isProfile': isProfile,
                            'created_at': Database.created_at(img.get('_id')),
                            'hasProfilePicture': hasProfilePicture})
                        usr = None
                    del img
                del imgs
                # print(final_imgs[0]['profilePicture'])
                return jsonify({'images': final_imgs, 'endCursor': skip + 10})
            else:
                return jsonify({'error': 'something wrong with skip value'})
        else:
            return jsonify({'error': 'invalid request'})


@app.route('/images/<string:img_id>.jpg')
@app.route('/images/display/<string:img_id>.jpg')
def get_image(img_id):
    if any(char in img_id for char in punctuation):
        flash('Invalid Post ID')
        return redirect('/', 302)

    if len(img_id) != 32:
        flash('Invalid Post ID')
        return redirect('/', 302)

    img = User.getImagebyImgID(img_id)
    if img:
        image_binary = base64.b64decode(img.get('image'))
        if "/images/display/" not in request.path:
            usr = User.getUserByID(img.get('userID'))
            if usr:
                usr.update({'totalDownloads': usr.get('totalDownloads') + 1})
                User.updateUserInfo(user=usr, _id=usr.get('_id'))
                ImageC.updateImgData(img_id=img_id, Download=True)
            else:
                print('Error: Couldn\'t find User..')
        # image_binary = read_image(pid)
        # response = make_response(image_binary)
        # response.headers.set('Content-Type', 'image/jpeg')
        if img.get('name'):
            return send_file(
                BytesIO(image_binary),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename=f"{img.get('name').title()}\'s Picture - \
Atypical.jpeg")
        return jsonify({'error': 'Image Corrupt!'})
    else:
        return jsonify({'error': 'Image Not Found!'})


@app.route("/settings/")
def settings():
    if session.get('_cu'):
        dataToDisplay = getCUserData()
        return render_template('settings.html',
                               userData=dataToDisplay,
                               current_time=datetime.utcnow())
    else:
        flash('Please Login to Access Settings Page!')
        return redirect('/login', 302)


@app.route("/categories")
@app.route('/category/<string:category>')
def Categories(category=None):
    categories = User.getCategories()
    if category is None:
        # print(categories)
        for cat in categories:
            image = cat.get('image')
            cat.update({'image': compressImage(image)})
            print(categories[0].get('category'))
        return render_template('category.html',
                            categories=categories,
                            enumerate=enumerate)

    if any(char in punctuation for char in category):
        flash('Invalid Category!')
        print(category)
        return redirect('/categories', 302)

    cats = User.getCategories(category)
    if cats:
        imgs = [i for i in cats]
    else:
        flash('Category not found!')
        return redirect('/')

    if imgs:
        return render_template('imgByCat.html',
                               category=category)
    else:
        flash('Category not Found!')
        return redirect('/categories', 302)
    

@app.route('/search')
def imageSearch():
    query = " ".join(words(request.args.get('q')))
    return render_template('search.html', query=query)

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if session.get('_cu', None) == None:
            form = LoginForm()
            # If Post Method is used..
            if form.validate() == False:
                # if form validation fails..
                return render_template('login.html', form=form)
            else:
                # Regular Expression for checking email syntax
                isEmail = re.compile(r"[^@]+@[^@]+\.[^@]+")

                if isEmail.fullmatch(form.username.data):
                    # flash('Email detected!')
                    result = User.checkUser(
                        username=form.username.data.lower(),
                        password=form.password.data,
                        email=True)
                else:
                    result = User.checkUser(
                        username=form.username.data.lower(),
                        password=form.password.data)

                if result:
                    new_session = User.createSession(result)
                    session['_cu'] = new_session

                    return redirect('/profile/')

                elif result is False:
                    flash('Invalid Password! Try Again..')

                else:
                    flash('User Does not Exist!')
                    flash('Please Check your Email Address or Username \
and Try Again..')

                return redirect(url_for('login'))

        else:
            return redirect(url_for('index'))

    elif request.method == 'GET':
        return render_template('login.html', form=form)


@app.route('/upload/profilePicture', methods=['POST'])
def updateProfilePicture():
    current_session = session.get('_cu')
    if current_session:
        img = request.get_data(as_text=True)
        # as_text=True
        if img:
            img = str(unquote(img))[str(unquote(img)).find('=') + 1:]
            image = str(unquote(img)).split(',')[-1]
            img
            try:
                img_data = base64.b64decode(image)
                f = open('temp', 'wb+')
                f.write(img_data)
                f.seek(0)
                image = Image.open(f)
                image.verify()
            except (IOError, SyntaxError):
                flash('Picture is Corrupt!')
                flash('Please Upload Another Picture or Try Again!')
                return jsonify({'error': 'Image is Corrupt!'})
            else:
                f.seek(0)
                image = Image.open(f)
                image = image.convert('RGB')
                image = image.resize((900, 900), Image.ANTIALIAS)
                buffered = BytesIO()
                image.save(buffered, format="JPEG", optimize=True, quality=75)
                encodedImg = base64.b64encode(buffered.getvalue()).decode()
                result = User.changeProfilePicture(
                    _cu=current_session,
                    profilePicture=encodedImg)
                f.truncate()
                f.close()
                flash('Profile Picture has been Updated!')

                del img_data
                del f
                del buffered
                del image
                del encodedImg

                if result:
                    return jsonify({'success': 'Profile Picture Updated!'})
                else:
                    return jsonify({'error': 'User Not Found!'})
            return jsonify({'result': 'success'})
        else:
            return jsonify({'error': 'Invalid Args!', 'args': request.args})
    else:
        return jsonify({'error': 'Invalid Session!'})


@app.route('/api', methods=['POST', 'PUT', 'DELETE'])
def api():
    current_session = session.get('_cu')

    if current_session:
        data = request.json
        if data:
            print(data)
            result = None
            if data.get('fieldType', '') == 'username':
                usr = getCUserData()
                if usr:
                    uname = data.get('data')
                    if len(uname) > 100:
                        flash('Username too Long!')
                        return jsonify({'error': 'failed'})

                    if not uname.replace('_', '').isalnum():
                        flash('Username Must Not Contain Special Characters')
                        return jsonify({'error': 'failed'})

                    uname = uname.replace(' ', '_')
                    result = User.changeUsername(
                        usr.get('_id'), uname)
                    # print(result)
                    flash('Username Changed Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            elif data.get('fieldType', '') == 'about':
                usr = getCUserData()
                if usr:
                    about = data.get('data')
                    about = about.replace('\n', '<br>')
                    result = User.changeAbout(usr.get('_id'),
                                              about)
                    # print(result)
                    flash('About You updated Successfully Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            elif data.get('fieldType', '') == 'password':
                usr = getCUserData()
                if usr:
                    result = User.changePassword(
                        usr.get('_id'), data.get('data'))
                    print(result)
                    flash('Password Changed Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            else:
                return(jsonify({'success': False}))

            if result:
                return(jsonify({'success': True}))
            else:
                return(jsonify({'success': False}))

        else:
            print('data not found')
            return redirect('/')
    else:
        print('invalid request')
        return('<h1>Invalid Request Sent to The Server</h1>', 404)


@app.route('/remove/profilePicture', methods=['POST'])
def removeProfilePicture():
    current_session = session.get('_cu')
    if current_session:
        json_data = request.get_data(as_text=True)
        response = json_data.split('=')
        if 'true' in response and 'removeProPic' in response:
            User.changeProfilePicture(
                _cu=current_session,
                profilePicture=None)
            flash('Profile Picture has been Removed!')
            return jsonify({'profilePicture': 'removed'})
        else:
            return jsonify({'error': 'invalid request'})

    else:
        return jsonify({'error': 'Invalid Session!'})


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if User.sessionCreatedAt(session.get('_cu', None)):
        form = UploadForm()
        if request.method == 'POST':
            if form.validate() == False:
                flash('Validation Failed!')
                return redirect(url_for('upload'))
            else:
                image = form.photo.data
                try:
                    img = Image.open(image)
                    img.verify()

                except (IOError, SyntaxError):
                    flash('Image is not Valid!')

                else:
                    img = Image.open(image)
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG",
                             optimize=True, quality=75)
                    fileObj = buffered.getvalue()
                    encodedImg = base64.b64encode(fileObj).decode()

                    tags, api_data = Hashtags(fileObj)
                    min_score = api_data['keywords'][1]['score'] # second highest score
                    cats = [i.get('keyword').lower() for i in api_data['keywords'] if i.get('score') >= min_score]
                    tags = [i.lower() for i in tags]
                    
                    img_id = str(uuid4().hex)[::-1]
                    User.uploadImage(session.get('_cu'),
                                     categories=cats,
                                     image=encodedImg,
                                     description=form.description.data,
                                     hashtags=tags,
                                     img_id=img_id)
                    del fileObj
                    flash('Image Uploaded Successfully!')
                    return redirect(f'/post/{img_id}', 302)

        elif request.method == 'GET':
            return render_template('upload.html', form=form)

    else:
        if session.get('_cu'):
            flash('Invalid Session Cookies..')
            flash('Please Login Again..')
            session.pop('_cu', None)
        else:
            flash('You are not Logged In!')
            flash('Please Login to Upload a Picture!')
        return redirect(url_for('login'))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            result = User.checkUser(
                username=form.email.data,
                password=form.password.data,
                signUp=True,
                email=True)

            if result:
                flash('User Already Exists!')
                flash('Please Login or Use different email address..')
                return redirect(url_for('signup'))

            else:
                newUser = User(name=form.name.data.lower(),
                               email=form.email.data.lower(),
                               username="{}{}".format(
                                   form.name.data.split()[0].lower(),
                    uuid4().hex),
                    password=form.password.data,
                    age=form.age.data,
                    gender=form.gender.data)
                newUser.saveUser()
                flash('Account Created Successfully! Now go to the login page\
 to Login into your account.')
                return redirect(url_for('index'))

    elif request.method == 'GET':
        session['username'] = None
        return render_template('signup.html', form=form)


@app.route("/logout")
def logout():
    cu = session.pop('_cu', None)
    if cu:
        User.removeSession(cu)
        flash('You are Logged out!')
    else:
        flash('You were not Logged In!')

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0')
