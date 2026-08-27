from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

CUSTOM_ID_RE = r"^[A-Za-z0-9]+$"


class URLMapForm(FlaskForm):
    original_link = StringField(
        "Длинная ссылка",
        validators=[
            DataRequired(message="Обязательное поле"),
            URL(message="Некорректная ссылка"),
            Length(max=2048),
        ],
    )

    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(max=16, message="Длина не должна превышать 16 символов"),
            Regexp(CUSTOM_ID_RE, message="Допустимы только латинские буквы и цифры"),
        ],
    )

    submit = SubmitField("Создать")


class FileUploadForm(FlaskForm):
    files = FileField(
        "Файлы",
        validators=[FileRequired(message="Выбери хотя бы один файл")],
        render_kw={"multiple": True},
    )
    submit = SubmitField("Загрузить")