from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_moment import Moment
from flask_principal import Principal, Permission, RoleNeed
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, ARCHIVES
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
ckeditor = CKEditor()
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()
csrf = CSRFProtect()
principals = Principal()


@login_manager.user_loader
def load_user(user_id):
    from approvalsystem.models import Users
    user = Users.query.get(int(user_id))
    return user


archives = UploadSet('archives', ARCHIVES)

login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'warning'

student_permission = Permission(RoleNeed('student'))
teacher_permission = Permission(RoleNeed('teacher'))
college_permission = Permission(RoleNeed('college'))
school_permission = Permission(RoleNeed('school'))
