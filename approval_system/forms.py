from flask_login import current_user
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, EqualTo, ValidationError

from approval_system.extensions import archives
from approval_system.models import User, Dept, Role


class LoginForm(FlaskForm):
    number = StringField('学号/工号', validators=[DataRequired(), Length(8, 12)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 100)])
    remember = BooleanField()
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    number = StringField('学号', validators=[DataRequired(), Length(12, 12), Regexp('^[0-9]*$', message='学号只能包含0-9')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 60)])
    dept_id = SelectField('学院', coerce=int, validators=[DataRequired()])
    phone = StringField('手机号', validators=[DataRequired(), Length(11, 11)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 100), EqualTo('password1')])
    password1 = PasswordField('确认密码', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('注册')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.dept_id.choices = [(dept.id, dept.name) for dept in Dept.query.filter(Dept.id > 1).all()]

    def validate_number(self, field):
        if User.query.filter_by(number=field.data).first():
            raise ValidationError('该学号已经被注册')


class RegisterAdminForm(FlaskForm):
    number = StringField('工号', validators=[DataRequired(), Length(8, 8), Regexp('^[0-9]*$', message='工号只能包含0-9')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 60)])
    dept_id = SelectField('学院/部门', coerce=int, validators=[DataRequired()])
    role_id = SelectField('角色', coerce=int, validators=[DataRequired()])
    phone = StringField('手机号', validators=[DataRequired(), Length(11, 11)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 100), EqualTo('password1')])
    password1 = PasswordField('确认密码', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('注册')

    def __init__(self, *args, **kwargs):
        super(RegisterAdminForm, self).__init__(*args, **kwargs)
        self.dept_id.choices = [(dept.id, dept.name) for dept in Dept.query.order_by(Dept.id.desc()).all()]
        self.role_id.choices = [(role.id, role.info) for role in Role.query.filter(Role.id > 1).all()]

    def validate_number(self, field):
        if User.query.filter_by(number=field.data).first():
            raise ValidationError('该工号已经被注册')


class SettingForm(FlaskForm):
    number = StringField('学号/工号', validators=[DataRequired(), Length(8, 12), Regexp('^[0-9]*$', message='学号/工号只能包含0-9')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 60)])
    dept_id = SelectField('学院', coerce=int, validators=[DataRequired()])
    phone = StringField('手机号', validators=[DataRequired(), Length(11, 11)])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)
        if current_user.dept_id == 1:
            self.dept_id.choices = [(current_user.dept_id, current_user.dept.name)]
        else:
            self.dept_id.choices = [(dept.id, dept.name) for dept in Dept.query.filter(Dept.id > 1).all()]

    def validate_number(self, field):
        if current_user.number == field.data:
            return
        if User.query.filter_by(number=field.data).first():
            raise ValidationError('该学号/工号已经被注册')


class PasswordForm(FlaskForm):
    old_password = PasswordField('原密码', validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('新密码', validators=[DataRequired(), Length(1, 100), EqualTo('password1')])
    password1 = PasswordField('确认密码', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('提交')

    def validate_old_password(self, field):
        if not current_user.validate_password(field.data):
            raise ValidationError('原密码错误')


class ApplyFormBase(FlaskForm):
    name = StringField('项目名', validators=[DataRequired(), Length(1, 60)])
    info = CKEditorField('项目描述', validators=[DataRequired()])
    file = FileField('项目文件', render_kw={'multiple': 'multiple'}, validators=[
        FileRequired(), FileAllowed(archives, '必须为压缩文件')
    ])
    t_id = SelectField('导师', coerce=int, validators=[DataRequired()])
    submit = SubmitField('立即申请')


class ApplyForm(ApplyFormBase):
    def __init__(self, *args, **kwargs):
        super(ApplyForm, self).__init__(*args, **kwargs)
        self.t_id.choices = [(t.id, t.name) for t in
                             User.query.filter(User.dept_id == current_user.dept_id, User.role_id == 2).all()]


class ReApplyForm(ApplyForm):
    name, info, file, submit = None, None, None, None
    submit0 = SubmitField('重新申请')


class MyApplyForm(ApplyFormBase):
    file, t_id, submit = None, None, None
    submit1 = SubmitField('立即更改')


class FileApplyForm(ApplyFormBase):
    name, info, t_id, submit = None, None, None, None
    submit2 = SubmitField('立即上传')


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit3 = SubmitField('提交评论')


class NoticeForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 100)])
    body = CKEditorField('公告内容', validators=[DataRequired()])
    submit = SubmitField('发布公告')


class MyNoticeForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 100)])
    body = CKEditorField('公告内容', validators=[DataRequired()])
    submit = SubmitField('立即更改')


class UserSearchForm(FlaskForm):
    number = StringField('学号/工号', validators=[DataRequired(), Length(8, 12), Regexp('^[0-9]*$', message='学号/工号只能包含0-9')])
    submit = SubmitField('搜索')


class PasswordResetForm(FlaskForm):
    new_password = StringField('密码', default='12345678', validators=[DataRequired(), Length(1, 100)])
    submit1 = SubmitField('重置')
