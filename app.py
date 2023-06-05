from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
db.init_app(app)
app.app_context().push()

class venue(db.Model):
    __tablename__ = 'venue'
    venue_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    venue_name= db.Column(db.String, unique=False, nullable=False)
    place = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)


class show(db.Model):
    __tablename__ = 'show'
    show_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_name = db.Column(db.String, unique=False, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String)
    price= db.Column(db.Integer, nullable=False)


class user(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80),  nullable=False)

class showtovenue(db.Model):
    __tablename__ = 'showtovenue'
    allocation_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_id = db.Column(db.Integer, nullable=False)
    venue_id = db.Column(db.Integer, nullable=False)

class userbooking(db.Model):
    __tablename__ = 'userbooking'
    booking_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False)
    show_id = db.Column(db.Integer, nullable=False)
    venue_id = db.Column(db.Integer, nullable=False)

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        movie=show.query.all()
        return render_template('index.html',shows=movie)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/adminlogin',methods=['GET','POST'])
def admin():
    #admin username=admin1234
    #admin password=admin@1234
    if request.method=='GET':
        return render_template('admin.html')
    elif request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username=='admin1234' and password=='admin@1234':
            return redirect(url_for('admin_index'))

@app.route('/adminindex', methods=['GET', 'POST'])
def admin_index():
     if request.method == 'GET':
        movie=show.query.all()
        venues=venue.query.all()
        a=showtovenue.query.all()
        return render_template('index_admin.html',shows=movie,venues=venues,allocations=a)

@app.route('/userlogin',methods=['GET', 'POST'])
def userlogin():
    if request.method=="GET":
       return render_template("userlogin.html")
    elif request.method=="POST":
         users = user.query.all()
         username = request.form["uname"]
         password = request.form["pswd"]

         for i in users:
             if username == i.username and password == i.password:
                 #print("Logged in successfully")
                cuser = user.query.filter(user.username == username).one()
                uid = cuser.user_id
                 #print(uid)
                return redirect(url_for("user_index",uid=uid))

@app.route('/userindex/<int:uid>",methods=["GET","POST"]')
def user_index(uid):
    if request.method=="GET":
        name = user.query.filter(user.user_id == uid).one()
        movie=show.query.all()
        venues=venue.query.all()
        a=showtovenue.query.all()
        return render_template('after_user_login.html',user=name, shows=movie,venues=venues,allocations=a)

@app.route('/usersignup', methods=['GET', 'POST'])
def usersignup():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        cpassword = request.form["password-repeat"]    
        if password == cpassword:
            new_user = user(username=username, password=password)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("userlogin"))
            except:
                return "Error adding user"
    elif request.method == 'GET':
        return render_template('usersignup.html')

@app.route('/usersearch', methods=['GET', 'POST'])
def user_search():
    if request.method == 'GET':
        return render_template('user_search.html')
    elif request.method == 'POST':
        serach_place=request.form['location']
        #search_rating=request.form['rating']
        loc=venue.query.filter(venue.place==serach_place)
        #show=show.query.filter(show.rating>=search_rating)
        return render_template('user_search.html',venues=loc,place=serach_place)
    
@app.route('/usersearchshow', methods=['GET', 'POST'])
def user_search_show():
    if request.method == 'GET':
        return render_template('user_search_show.html')
    elif request.method == 'POST':
        search_rating=request.form['rating']
        show_list=show.query.filter(show.rating>=search_rating)
        return render_template('user_search_show.html',shows=show_list,rating=search_rating)
    
@app.route('/usersearchtag', methods=['GET', 'POST'])
def user_search_tag():
    if request.method == 'GET':
        return render_template('user_search_tag.html')
    elif request.method == 'POST':
        tag_name=request.form['tags']
        tag_list=show.query.filter(show.tags==tag_name)
        return render_template('user_search_tag.html',tags=tag_list,tag_name=tag_name)


@app.route('/userbook', methods=['GET', 'POST'])
def user_book():
    if request.method == 'GET':
        shows=show.query.all()
        venues=venue.query.all()
        return render_template('user_book.html',shows=shows,venues=venues)

    elif request.method == 'POST':
        show_name=request.form['show_name']
        venue_name=request.form['venue_name']
        username=request.form['username']
        no_of_tickets=int(request.form['tickets'])
        u=user.query.filter(user.username==username).one()
        u_id=u.user_id
        venue_obj=venue.query.filter(venue.venue_name==venue_name).one()
        if no_of_tickets>venue_obj.capacity:
            return "No of tickets exceeds venue capacity"
        else:
            venue_obj.capacity=venue_obj.capacity-no_of_tickets
            new_booking = userbooking(username=username, show_id=show_name, venue_id=venue_name)
            try:
                db.session.add(new_booking)
                db.session.commit()
                return redirect(url_for('user_index',uid=u_id))
            except:
                return "Error booking"

@app.route('/adminaddvenue', methods=['GET', 'POST'])
def admin_add_venue():
    if request.method == 'POST':
     venue_id = request.form['venue_id']
     venue_name = request.form['name']
     place = request.form['address']
     capacity = request.form['capacity']
     new_venue = venue(venue_id=venue_id, venue_name=venue_name, place=place, capacity=capacity)
     try:
         db.session.add(new_venue)
         db.session.commit()
         return redirect(url_for('admin_index'))
     except:
         return "Error adding venue"

    elif request.method == 'GET':
        return render_template('add_venue.html')

@app.route('/admineditvenue',methods=['GET', 'POST'])
def admin_edit_venue():
    if request.method == 'GET':
        return render_template('edit_venue.html')
    elif request.method == 'POST':
        venue_id = request.form['venueid']
        venue_name = request.form['venuename']
        l = venue.query.filter(venue.venue_id == venue_id).one()
        l.venue_name = venue_name  # update the venue name
        try:
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            db.session.rollback()
            return redirect(url_for('admin_edit_venue'))



@app.route('/adminremovevenue',methods=['GET', 'POST'])
def admin_remove_venue():
    if request.method == 'GET':
        return render_template('remove_venue.html')
    elif request.method == 'POST':
        venue_id = request.form['venueid']
        l = venue.query.filter(venue.venue_id == venue_id).one()
        try:
            db.session.delete(l)
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            db.session.rollback()
            return redirect(url_for('admin_remove_venue'))

@app.route('/adminaddshow',methods=['GET', 'POST'])
def admin_add_show():
    if request.method == 'POST':
        show_id = request.form['show_id']
        show_name = request.form['show_name']
        rating = request.form['rating']
        tags = request.form['tag']
        price = request.form['price']
        new_show = show(show_id=show_id, show_name=show_name, rating=rating, tags=tags, price=price)
        try:
            db.session.add(new_show)
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            return "Error adding show"
    elif request.method == 'GET':
        return render_template('add_show.html')

@app.route('/admineditshow', methods=['GET', 'POST'])
def admin_edit_show():
    if request.method == 'GET':
        return render_template('edit_show.html')
    elif request.method == 'POST':
        show_id = request.form['showid']
        show_name = request.form['showname']
        l = show.query.filter(show.show_id == show_id).one()
        l.show_name = show_name
        try:
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            db.session.rollback()
            return redirect(url_for('admin_edit_show'))

@app.route('/adminremoveshow', methods=['GET', 'POST'])
def admin_remove_show():
    if request.method == 'GET':
        return render_template('remove_show.html')
    elif request.method == 'POST':
        show_id = request.form['showid']
        l = show.query.filter(show.show_id == show_id).one()
        try:
            db.session.delete(l)
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            db.session.rollback()
            return redirect(url_for('admin_remove_show'))

@app.route('/adminallocateshow', methods=['GET', 'POST'])
def admin_allocate_show():
    if request.method == 'POST':
        show_id = request.form['show_id']
        venue_id = request.form['venue_id']
        new_showtovenue = showtovenue(show_id=show_id, venue_id=venue_id)
        try:
            db.session.add(new_showtovenue)
            db.session.commit()
            return redirect(url_for('admin_index'))
        except:
            return "Error allocating show to venue"
    elif request.method == 'GET':
        return render_template('allocate_venue.html')



if __name__ == '__main__':
    app.run(debug=True)
