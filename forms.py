from wtforms import TextAreaField, SubmitField, StringField, PasswordField,SelectField,IntegerField,RadioField
from wtforms.validators import InputRequired,EqualTo
from wtforms.fields.html5 import DateTimeLocalField
from wtforms import SelectMultipleField,widgets
import wtforms

from flask_wtf import FlaskForm

class IndexForm(FlaskForm):
   account = StringField("Account:", validators=[InputRequired()])
   password = PasswordField("Password", validators=[InputRequired()])
   submit=SubmitField("Submit") 

class RegisterForm(FlaskForm):
   account = StringField("Account:", validators=[InputRequired()])
   password = PasswordField("Password", validators=[InputRequired()])
   repeat_password = PasswordField("Repeat Password", validators=[InputRequired(),EqualTo("password")])
   submit = SubmitField("Submit")

class AddEventForm(FlaskForm):
   type_ = SelectField("Type:", validators=[InputRequired()])
   end_date = DateTimeLocalField(
       "End Date:", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
   subject = StringField("Enter Subject:", validators=[InputRequired()])
   content = TextAreaField("Enter content:", validators=[InputRequired()])
   add_submit = SubmitField()

class UpdateEventForm(FlaskForm):
   id_select=IntegerField("Update Id:")
   type_ = SelectField("Type:", validators=[InputRequired()])
   end_date = DateTimeLocalField(
       "End Date:", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
   subject = StringField("Enter Subject:", validators=[InputRequired()])
   content = TextAreaField("Enter content:", validators=[InputRequired()])
   update_submit = SubmitField("Update")

class DeleteEventForm(FlaskForm):
   delete_submit = SubmitField("Delete")

class MultiCheckboxField(SelectMultipleField):
   widget = widgets.ListWidget(prefix_label=False)
   option_widget = widgets.CheckboxInput()

class EventForm(FlaskForm):
   add_event_form = wtforms.FormField(AddEventForm)
   update_event_form = wtforms.FormField(UpdateEventForm)
   delete_event_form = wtforms.FormField(DeleteEventForm)
   id_event = MultiCheckboxField()
   type_ = SelectField("Type:", validators=[InputRequired()], default="Other")
   add_event_button = SubmitField("Add a new event")
   update_event_button=SubmitField("update a current event")

class CalendarForm(FlaskForm):
   days_of_month = RadioField()
   submit=SubmitField("submit")

class LogoutForm(FlaskForm):
   submit=SubmitField("Log out")


