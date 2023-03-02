"""
My system has only regular users.
To save your time,you can try to use the following one:
    user name:ldl
    password:123
But you can also register a new account.

There are four pages:
1.login page：
    Enter account and password to enter the main page.
2.register page:
    Register a new account if it doesn't exist in the database.
3.main page:
    i.Account name is shown in the nav.
    ii.The calendar of the current month marks today.
       choose one day of this month and then submit. 
       The events of the corresponding day will shown, 
       otherwise you will receive congratulationsdatetime A combination of a date and a time. Attributes: ()
    iii.Something to be solved today is shown in a table, 
        or you will receive congradulations. 
4.event edit page
    i.You can delete multiple events 
      and the id of them will be upgraded automactically.
    ii. click on the button and finish the form to create a new event.
    iii.click on the button and finish the form to update the event of the id you provide.
"""
from database import get_db, close_db
from flask import Flask,render_template,redirect,url_for,session
from flask_session import Session
from forms import IndexForm,RegisterForm,EventForm,CalendarForm
from werkzeug.security import generate_password_hash,check_password_hash 
from datetime import datetime,timedelta

import calendar

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

app=Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)

@app.route("/",methods=["GET","POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    form=IndexForm()
    if form.validate_on_submit():
        db = get_db()
        account=form.account.data
        password=form.password.data
        client= db.execute("""SELECT * FROM accounts
                              WHERE account=?;""", (account,)).fetchone()
        if client is None:
            form.account.errors.append("Inexistent account！")
        elif not check_password_hash(client["password"],password):
            form.password.errors.append("Incorrect password！")
        else:
            if "account" in session.keys():
                session.pop("account")
                session["account"]=account
                return redirect(url_for("main_page"))
            else:
                session["account"] = account
                return redirect(url_for("main_page"))
    return render_template("index.html",form=form)

@app.route("/register", methods=["GET", "POST"])
def register_account():
    form = RegisterForm()
    message=""
    if form.validate_on_submit():
        account = form.account.data
        password = form.password.data
        db = get_db()
        if db.execute("""SELECT * FROM accounts
                                where account=?;""", (account,)).fetchone() is not None:
            form.account.errors.append("Existing account！Please change another one!")
        else:
            db.execute("""INSERT INTO accounts(account, password) 
                      VALUES(?, ?);""", (account, generate_password_hash(password)))
            db.commit()
            message="Success!"
            return redirect(url_for('index'))
    return render_template("register.html",form=form,message=message)

"""
1.The implement of calendar
    From the standard library,choose calendar,datetime.now()  
    to implement a month calendar.
   I. The caption of the calendar table shows today and this month.
   II. Use double iteration to list each day of this month in the table.
       For each day in <td>, if it is today, the <td> will be marked.
       Other <td> corresponding to other days will be include 
       sub buttons.
   III.If the data of radio buttons isn't empty(form.days_of_month),the
        mapped events( event_of_chosen_day) will be shown in the page.
The use of timedelta and replace function is inspired by the following link:
https://stackoverflow.com/questions/37396329/finding-first-day-of-the-month-in-python

2.Find the events of today
    values of radio buttons are days of this month.
    The dict variable 
        "mapping" maps events to corresponding days.
    if array variable "events_today" is not empty, 
    the events will be shown in a table.
"""
@app.route("/mainpage", methods=["GET", "POST"])
def main_page():
    db = get_db()
    form=CalendarForm()

    now_time = datetime.now()
    calendar_ = calendar.monthcalendar(now_time.year, now_time.month)

    event_of_chosen_day={}
    mapping_ = {}

    temp_day = datetime.today().replace(day=1)

    for week_ in calendar_:
        for day_ in week_:
            events_today = db.execute("""SELECT * FROM events
                                        WHERE end_date between ? and ?
                                        and account=?;""", (temp_day.strftime("%Y-%m-%d"), (temp_day+timedelta(days=1)).strftime("%Y-%m-%d"), session['account'],)).fetchall()
            temp_day += timedelta(days=1)
            mapping_[day_]=events_today

    form.days_of_month.choices = [(day_, day_) for day_ in mapping_]
    date_today = now_time.strftime("%Y-%m-%d")
    due_date_today = (now_time+timedelta(days=1)).strftime("%Y-%m-%d")
    events_today = db.execute("""SELECT * FROM events
                              WHERE end_date between ? and ?;""", (date_today,due_date_today,)).fetchall()
    _today = now_time.day

    if form.validate_on_submit:
        chosen_day=form.days_of_month.data
        if chosen_day is not None:
            event_of_chosen_day = mapping_[int(chosen_day)]

    return render_template("main_page.html", form=form, calendar_=calendar_, now_time=now_time, events_today=events_today, event_of_chosen_day=event_of_chosen_day, _today=_today)

"""
My original intention is to implement multiple 
delete/add/update events.
But it is more convenient to add/update one event in one time 
than clicking on submit button in many times.

The forms of three operations are combined in one form(EventForm).
I got the inspiration from the following link:
https://dev.to/sampart/combining-multiple-forms-in-flask-wtforms-but-validating-independently-cbm

The use of MultiCheckboxField references the following one:
https://wtforms.readthedocs.io/en/stable/specific_problems/

mapping_ is used to combine multicheckbox and contents of existing events
for better presentation.

1.delete multiple events
  Multiple events can be deleted in one time by using multicheckbox.
  choices consists of many tuples.(label,value)
  The list of Ids can be got by calling form.id_event.data.
  Each event of corresponding id can be deleted through iteration. 
2.update an exist event
  enter the event id and contents to be changed
3.add a new event
"""
@app.route("/event_edit", methods=["GET", "POST"])
def event_edit():
    form=EventForm()
    db = get_db()
    mapping={}
    events = db.execute("""SELECT * FROM events where account=?;""",(session['account'],)).fetchall()
    types = db.execute("""SELECT * FROM types;""").fetchall()
    form.add_event_form.type_.choices = [(type_[1]) for type_ in types]
    form.update_event_form.type_.choices = [(type_[1]) for type_ in types]
    form.id_event.choices = [(event_[0], event_[0]) for event_ in events]
    for event_ in events:
        mapping[event_[0]]=event_
    if form.add_event_form.validate(form):
        type_ = form.add_event_form.type_.data
        end_date = form.add_event_form.end_date.data
        subject = form.add_event_form.subject.data
        content = form.add_event_form.content.data
        db.execute("""INSERT INTO 
                        events(account,type,start_date,end_date,subject,content) 
                        VALUES(?,?,?,?,?,?);""", (session['account'], type_, datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), end_date, subject, content))
        db.commit()
        return redirect(url_for('event_edit'))

    if form.update_event_form.id_select.data is not None:
        if form.update_event_form.validate(form):
            temp_id = form.update_event_form.id_select.data
            type_ = form.update_event_form.type_.data
            end_date = form.update_event_form.end_date.data
            subject = form.update_event_form.subject.data
            content = form.update_event_form.content.data
            db.execute("""Update events
                        SET type=?,start_date=?,end_date=?,subject=?,content=?
                        WHERE id=?;""", (type_, datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), end_date, subject, content, temp_id,))
            db.commit()
            return redirect(url_for('event_edit'))

    if form.delete_event_form.validate(form):
        if form.id_event.data is None:
            form.id_event.errors.append("Empty choice!")
        else:
            delete_events = form.id_event.data
            for delete_event in delete_events:
                db.execute("DELETE FROM events WHERE id=?", (delete_event,))
                db.commit()
            temp_id = 1
            for event_ in events:
                db.execute("""Update events SET id=? 
                            WHERE id=(?);""", (temp_id, event_[0],))
                db.commit()
                temp_id += 1
            return redirect(url_for('event_edit'))

    return render_template("event_edit.html", form=form, mapping=mapping)

