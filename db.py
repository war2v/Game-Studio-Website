from flask import Flask, redirect, url_for, render_template, request, session
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__)
app.secret_key = "key"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=20)

db = SQLAlchemy(app)

class post(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    poster = db.Column(db.String(100))
    title = db.Column(db.String(100))
    post_content = db.Column(db.String(400))

    def __init__(self, title, post_content, poster) -> None:
        super().__init__()
        self.post_content = post_content
        self.title = title
        self.poster = poster

class donations(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)

    def __init__(self, name, amount):
        super().__init__()
        self.name = name
        self.amount = amount


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    bio = db.Column(db.String(500))
    pro_pic = db.Column(db.String( ))


    def __init__(self, username, email, password):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password
        self.bio = ""


@app.route("/")
def index():
    if "profile" in session:
        return render_template("home.html", loginTab='Profile', logout="logout")
    else:
        return render_template("home.html", loginTab='Login')

@app.route("/home/", methods=["POST", "GET"])
def home():
    if "profile" in session:
        return render_template("home.html", loginTab='Profile', logout="logout")
    else:
        return render_template("home.html", loginTab='Login')
    
@app.route("/descent/", methods=["POST", "GET"])
def descent():
    if "profile" in session:
        return render_template("games/descent.html", loginTab='Profile', logout="logout")
    else:
        return render_template("games/descent.html", loginTab='Login')
    
@app.route("/aftermath/", methods=["POST", "GET"])
def aftermath():
    if "profile" in session:
        return render_template("games/aftermath.html", loginTab='Profile', logout="logout")
    else:
        return render_template("games/aftermath.html", loginTab='Login')
    
@app.route("/ruinhunter/", methods=["POST", "GET"])
def ruinhunter():
    if "profile" in session:
        return render_template("games/ruinhunter.html", loginTab='Profile', logout="logout")
    else:
        return render_template("games/ruinhunter.html", loginTab='Login')
    

    
@app.route("/community/", methods=["POST", "GET"])
def community():
    posts = post.query.all()
    if "profile" in session:
        return render_template("tabs/board.html", loginTab='Profile', logout="logout", post_list=posts, name=session['profile'])
    else:
        return render_template("tabs/board.html", loginTab='Login', post_list=posts, name="name")
    
    

@app.route("/news/")
def news():
    if "profile" in session:
        return render_template("tabs/news.html", loginTab='Profile', logout="logout")
    else:
        return render_template("tabs/news.html", loginTab='Login')


@app.route("/support/", methods=["POST", "GET"])
def support():
    if request.method == "POST":
        name = request.form['name']
        amount = float(request.form['amount'])
        deposit = donations(name, amount)
        db.session.add(deposit)
        db.session.commit()
        flash(f"{amount} deposited, Thank you {name}!")
        if "profile" in session:
            return render_template("tabs/support.html", loginTab='Profile', logout="logout")
        else:
            return render_template("tabs/support.html", loginTab='Login')
    else:
        None
    if "profile" in session:
        return render_template("tabs/support.html", loginTab='Profile', logout="logout")
    else:
        return render_template("tabs/support.html", loginTab='Login')


@app.route("/profile/", methods=["POST", "GET"])
def profile() :
    email = None
    profile = session['profile']
    if "profile" in session:
        profile = session["profile"]
        user = users.query.filter_by(username=profile).first()
        bio = user.bio

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            flash("email saved")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("profile.html", profilename=profile, email=email, loginTab='Profile', logout="logout", bio=bio)
    else:
        return redirect(url_for("login", loginTab='Login'))
    
@app.route("/view/", methods=["POST", "GET"])
def view():
    if "profile" in session:
        if session['profile'] == 'root':
            if request.method == "POST":
                admin = ""
            
                match request.form['delete']:
                    case 'deleteUser':
                        found_user = users.query.filter_by(username=request.form['username']).delete()
                        db.session.commit()
                    case 'deletePost':
                        found_post = post.query.filter_by(_id=request.form['id']).delete()
                        db.session.commit()
                    case 'deleteDon':
                        found_Don = donations.query.filter_by(_id=request.form['id']).delete()
                        db.session.commit()
                    case 'enter':
                        name = request.form['name']
                        title = request.form['title']
                        content = request.form['body']
                        new_post = post(title, content, name)
                        db.session.add(new_post)
                        db.session.commit()
            if session['profile'] == 'root':
                admin = 'Admin Page'
            return render_template("view.html", loginTab='Profile', logout='logout', values=users.query.all(), post_info=post.query.all(), donation_info=donations.query.all(), admin=admin)  
        else:
            return redirect(url_for('home'))
        
    else:
        return redirect(url_for("login")) 


@app.route("/editprofile/", methods=["POST", "GET"])
def edit_profile():
    if request.method == "GET":
        return render_template("editprofile.html", _id=session["id"], profilename=session['profile'], email=session['email'], loginTab='Profile', logout="logout")
    else:
        found_user = users.query.filter_by(_id=session["id"]).first()
        found_user.username = session['profile'] = request.form['profilename']
        found_user.email = session['email'] = request.form['email']
        found_user.bio = request.form['bio']
        db.session.commit()
        return render_template("editprofile.html", _id=session["id"], profilename=session['profile'], email=session['email'], loginTab='Profile', logout="logout", bio=found_user.bio)
    
 
@app.route("/createProfile/", methods=["POST", "GET"])
def create_account():
    if "profile" in session:
        return(redirect(url_for("profile", loginTab='Profile', logout="logout")))
    else:
        if request.method == "POST":
            username = request.form['username']
            found_user = users.query.filter_by(username=username).first()
            if found_user:
                flash("Username is in use")
                return(render_template("createProfile.html", loginTab='Login'), )
            else:
                email = request.form['email']
                password = request.form['password']
                usr = users(username, email, password)
                db.session.add(usr)
                db.session.commit()
                return redirect(url_for("login", loginTab='Login'))
        else:
            return(render_template("createProfile.html", loginTab='Login'))
   


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        if request.form['Button'] == "Enter":
            username = request.form['username']

            found_user = users.query.filter_by(username=username).first()
            if found_user:
                session['id'] = found_user._id
                profile = session["profile"] = found_user.username
                email = session["email"] = found_user.email
                return redirect(url_for("home", loginTab='Profile', profile=profile, email=email, logout="logout",
                        homedata='<a href="{{ url_for(\'login\')}}"><button type="button" class="btn btn-primary">Sign-In</button></a> <a href="{{ url_for(\'create_account\')}}"><button type="button" class="btn btn-primary">Create-Account</button></a>'))
            else:
                flash("user not found")
                return render_template("login.html", loginTab='Login')
        elif request.form['Button'] == "Create An Account":
            return redirect(url_for("create_account", loginTab='Login'))
    else:
        if "profile" in session:
            return redirect(url_for("profile", loginTab='Profile', profile=session['profile'], logout="logout"))
        return render_template("login.html", loginTab='Login')
    
@app.route("/logout/")
def logout():
    if "profile" in session:
        session.pop("profile", None)
        session.pop("email", None)
        flash(f"Logout successful", "info")
    return redirect(url_for("home", loginTab='Login'))






if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
