from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    BooleanField,
    SubmitField,
    FloatField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Optional,
    NumberRange,
)
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class CoffeeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField(
        "Category",
        choices=[
            ("espresso", "Espresso"),
            ("cold", "Cold Brew"),
            ("specialty", "Specialty"),
            ("tea", "Tea"),
            ("filter", "Filter Coffee"),
            ("seasonal", "Seasonal Specials"),
        ],
        validators=[DataRequired()],
    )
    is_favorite = BooleanField("Featured Item")
    flavors = StringField("Flavors (comma separated)", validators=[Optional()])

    # Coffee enthusiast details
    bean_origin = StringField("Bean Origin", validators=[Optional(), Length(max=100)])
    bean_type = SelectField(
        "Bean Type",
        choices=[
            ("", "Select Bean Type"),
            ("arabica", "Arabica"),
            ("robusta", "Robusta"),
            ("blend", "Blend"),
            ("single_origin", "Single Origin"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )

    roast_level = SelectField(
        "Roast Level",
        choices=[
            ("", "Select Roast Level"),
            ("light", "Light"),
            ("medium_light", "Medium-Light"),
            ("medium", "Medium"),
            ("medium_dark", "Medium-Dark"),
            ("dark", "Dark"),
        ],
        validators=[Optional()],
    )

    processing_method = SelectField(
        "Processing Method",
        choices=[
            ("", "Select Processing Method"),
            ("washed", "Washed/Wet"),
            ("natural", "Natural/Dry"),
            ("honey", "Honey/Pulped Natural"),
            ("wet_hulled", "Wet-Hulled"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )

    flavor_notes = TextAreaField("Detailed Flavor Notes", validators=[Optional()])

    acidity = SelectField(
        "Acidity",
        choices=[
            ("", "Select Acidity Level"),
            ("low", "Low"),
            ("medium_low", "Medium-Low"),
            ("medium", "Medium"),
            ("medium_high", "Medium-High"),
            ("high", "High"),
        ],
        validators=[Optional()],
    )

    body = SelectField(
        "Body",
        choices=[
            ("", "Select Body"),
            ("light", "Light"),
            ("medium_light", "Medium-Light"),
            ("medium", "Medium"),
            ("medium_full", "Medium-Full"),
            ("full", "Full"),
        ],
        validators=[Optional()],
    )

    sweetness = SelectField(
        "Sweetness",
        choices=[
            ("", "Select Sweetness Level"),
            ("low", "Low"),
            ("medium_low", "Medium-Low"),
            ("medium", "Medium"),
            ("medium_high", "Medium-High"),
            ("high", "High"),
        ],
        validators=[Optional()],
    )

    recommended_brew = StringField(
        "Recommended Brewing Methods (comma separated)", validators=[Optional()]
    )

    image = FileField(
        "Image", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )

    submit = SubmitField("Save")


class OrderNoteForm(FlaskForm):
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Place Order")


class UserEditForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=64)])
    is_barista = BooleanField("Barista Access")
    is_admin = BooleanField("Admin Access")
    submit = SubmitField("Save Changes")

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError("Please use a different email address.")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Change Password")
