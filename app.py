from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


app = Flask(__name__)
client = Client("ACda9f81c9558109c70ec80f8eb90257a8", "7dcfa5a3d18407d594ee012f1b3ee09a")

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://qcfxmlvpoorbnq:ef8b2881dd5561fd062ccec730acee834b74c9df159140359553d9c0bcc924c0@ec2-34-225-103-117.compute-1.amazonaws.com:5432/d56ntuj1g1552k"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__='manipalpool'
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
        e_name = post.Name
        e_id = post.email
        e_phone = post.Phone_no
        if request.method == 'POST':
            Name = request.form.get("Name")
            Phone_no = request.form.get("Phone_no")
            T_area = request.form.get("T_area")
            client.messages.create(
                body="Sender Name:" + Name + ",Sender Phone no:" + str(Phone_no) + ",Reciever Name:" + str(
                    e_name) + ",Reciever Phone no:" + str(e_phone) + ",Reciever Email ID:" + str(e_id) +".",from_="whatsapp:+14155238886", to="whatsapp:+917048984193")
            message = Mail(from_email='akash.singh88023@gmail.com',
                           to_emails=e_id,
                           subject='You got a Request for Cab Sharing from '+Name+".",
                           html_content=render_template('mail.html',Name=Name, Phone_no=Phone_no, T_area=T_area))
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
