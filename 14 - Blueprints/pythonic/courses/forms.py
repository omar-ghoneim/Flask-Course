from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from pythonic.models import Course
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
)


class NewCourseForm(FlaskForm):
    title = StringField("Course Name", validators=[DataRequired(), Length(max=50)])
    description = TextAreaField(
        "Course Description", validators=[DataRequired(), Length(max=150)]
    )
    icon = FileField("Icon", validators=[DataRequired(), FileAllowed(["jpg", "png"])])
    submit = SubmitField("Create")

    def validate_title(self, title):
        course = Course.query.filter_by(title=title.data).first()
        if course:
            raise ValidationError(
                "Course name already exists! Please choose a different one"
            )
