from flask import Blueprint
from pythonic.models import Lesson, Course
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    session,
    abort,
)
from pythonic.lessons.forms import (
    NewLessonForm,
    LessonUpdateForm,
)
from pythonic.courses.forms import NewCourseForm

from pythonic import db
from flask_modals import render_template_modal
from flask_login import (
    login_required,
    current_user,
)
from pythonic.helpers import save_picture
from pythonic.lessons.helpers import get_previous_next_lesson, delete_picture

lessons = Blueprint("lessons", __name__)


@lessons.route("/dashboard/new_lesson", methods=["GET", "POST"])
@login_required
def new_lesson():
    new_lesson_form = NewLessonForm()
    new_course_form = NewCourseForm()
    form = ""
    flag = session.pop("flag", False)
    if "content" in request.form:
        form = "new_lesson_form"
    elif "description" in request.form:
        form = "new_course_form"

    if form == "new_lesson_form" and new_lesson_form.validate_on_submit():
        if new_lesson_form.thumbnail.data:
            picture_file = save_picture(
                new_lesson_form.thumbnail.data, "static/lesson_thumbnails"
            )
        lesson_slug = str(new_lesson_form.slug.data).replace(" ", "-")
        course = new_lesson_form.course.data
        lesson = Lesson(
            title=new_lesson_form.title.data,
            content=new_lesson_form.content.data,
            slug=lesson_slug,
            author=current_user,
            course_name=course,
            thumbnail=picture_file,
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Your lesson has been created!", "success")
        return redirect(url_for("lessons.new_lesson"))

    elif form == "new_course_form" and new_course_form.validate_on_submit():
        if new_course_form.icon.data:
            picture_file = save_picture(
                new_course_form.icon.data, "static/course_icons", output_size=(150, 150)
            )
        course_title = str(new_course_form.title.data).replace(" ", "-")
        course = Course(
            title=new_course_form.title.data,
            description=new_course_form.description.data,
            icon=picture_file,
        )
        db.session.add(course)
        db.session.commit()
        session["flag"] = True
        flash("New Course has been created!", "success")
        return redirect(url_for("users.dashboard"))

    modal = None if flag else "newCourse"
    return render_template_modal(
        "new_lesson.html",
        title="New Lesson",
        new_lesson_form=new_lesson_form,
        new_course_form=new_course_form,
        active_tab="new_lesson",
        modal=modal,
    )


@lessons.route("/<string:course>/<string:lesson_slug>")
def lesson(lesson_slug, course):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first()
    if lesson:
        previous_lesson, next_lesson = get_previous_next_lesson(lesson)
    lesson_id = lesson.id if lesson else None
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template(
        "lesson_view.html",
        title=lesson.title,
        lesson=lesson,
        previous_lesson=previous_lesson,
        next_lesson=next_lesson,
    )


@lessons.route("/dashboard/user_lessons", methods=["GET", "POST"])
@login_required
def user_lessons():
    return render_template(
        "user_lessons.html", title="Your Lessons", active_tab="user_lessons"
    )


@lessons.route("/<string:course>/<string:lesson_slug>/update", methods=["GET", "POST"])
def update_lesson(lesson_slug, course):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first()
    if lesson:
        previous_lesson, next_lesson = get_previous_next_lesson(lesson)
    lesson_id = lesson.id if lesson else None
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.author != current_user:
        abort(403)
    form = LessonUpdateForm()
    if form.validate_on_submit():
        lesson.course_name = form.course.data
        lesson.title = form.title.data
        lesson.slug = str(form.slug.data).replace(" ", "-")
        lesson.content = form.content.data
        if form.thumbnail.data:
            delete_picture(lesson.thumbnail, "static/lesson_thumbnails")
            new_picture = save_picture(form.thumbnail.data, "static/lesson_thumbnails")
            lesson.thumbnail = new_picture
        db.session.commit()
        flash("Your lesson has been updated!", "success")
        return redirect(
            url_for("lessons.lesson", lesson_slug=lesson.slug, course=lesson.course_name.title)
        )
    elif request.method == "GET":
        form.course.data = lesson.course_name.title
        form.title.data = lesson.title
        form.slug.data = lesson.slug
        form.content.data = lesson.content
    return render_template(
        "update_lesson.html",
        title="Update | " + lesson.title,
        lesson=lesson,
        previous_lesson=previous_lesson,
        next_lesson=next_lesson,
        form=form,
    )


@lessons.route("/lesson/<lesson_id>/delete", methods=["POST"])
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.author != current_user:
        abort(403)
    db.session.delete(lesson)
    db.session.commit()
    flash("Your lesson has been deleted!", "success")
    return redirect(url_for("lessons.user_lessons"))
