from flask import Blueprint
import secrets
import os
from pythonic.models import Lesson, Course
from flask_ckeditor import upload_success, upload_fail
from flask import (
    render_template,
    url_for,
    request,
    send_from_directory,
)
from flask import current_app


main = Blueprint("main", __name__)


@main.route("/files/<path:filename>")
def uploaded_files(filename):
    path = os.path.join(current_app.root_path, "static/media")
    return send_from_directory(path, filename)


@main.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("upload")
    extension = f.filename.split(".")[-1].lower()
    if extension not in ["jpg", "gif", "png", "jpeg"]:
        return upload_fail(message="File extension not allowed!")
    random_hex = secrets.token_hex(8)
    image_name = random_hex + extension
    f.save(os.path.join(current_app.root_path, "static/media", image_name))
    url = url_for("main.uploaded_files", filename=image_name)
    return upload_success(url, filename=image_name)


@main.route("/")
@main.route("/home")
def home():
    lessons = Lesson.query.order_by(Lesson.date_posted.desc()).paginate(
        page=1, per_page=6
    )
    courses = Course.query.paginate(page=1, per_page=6)
    return render_template("home.html", lessons=lessons, courses=courses)


@main.route("/about")
def about():
    return render_template("about.html", title="About")
