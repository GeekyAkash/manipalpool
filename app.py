from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///manipalpool.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Phone_no = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    Airport_name = db.Column(db.String(60), nullable=False)
    A_date = db.Column(db.Integer, nullable=False)
    A_time = db.Column(db.String(15), nullable=False)
    seat_avail = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.Name} - {self.Airport_name} - {self.A_date} - {self.A_time} - {self.seat_avail}"


@app.route('/', methods=['POST', 'GET'])
def home():
    try:
        if request.method == 'POST':
            Name = request.form['Name']
            Phone_no = request.form['Phone_no']
            email = request.form['email']
            Airport_name = "Mangaluru International Airport, Mangalore, India."
            A_date = request.form['A_date']
            A_time = request.form['A_time']
            seat_avail = request.form['seat_avail']
            post = Post(Name=Name, Phone_no=Phone_no, email=email, Airport_name=Airport_name, A_date=A_date,
                        A_time=A_time,
                        seat_avail=seat_avail)

            db.session.add(post)
            db.session.commit()
    except:
        return redirect("/")

    allpost = Post.query.all()
    return render_template('home.html', allpost=allpost)


@app.route('/request/<int:sno>')
def requests(sno):
    Post.query.filter_by(sno=sno).first()
    return redirect(url_for('email', sno=sno))


@app.route('/email/<sno>', methods=['POST', 'GET'])
def email(sno):
    try:
        post = Post.query.filter_by(sno=sno).first()
        e_id = post.email
        if request.method == 'POST':
            Name = request.form.get("Name")
            Phone_no = request.form.get("Phone_no")
            T_area = request.form.get("T_area")
            message = Mail(from_email='manipalpool@gmail.com',
                           to_emails=e_id,
                           subject='You got a Request for Cab Sharing from ' + Name + ".",
                           html_content=render_template('mail.html', Name=Name, Phone_no=Phone_no, T_area=T_area))
            try:
                sg = SendGridAPIClient("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")
                sg.send(message)
            except:
                return redirect('/')

            finally:
                if post.seat_avail > 1:
                    post.seat_avail -= 1
                    db.session.add(post)
                    db.session.commit()
                    return redirect('/')
                else:
                    db.session.query(Post).filter(Post.seat_avail == 1).delete()
                    db.session.commit()
                    return redirect("/")

        return render_template("request.html", post=post)
    except:
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
