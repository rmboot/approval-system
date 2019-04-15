import os

from flask import Flask, render_template
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from flask_uploads import configure_uploads
from flask_wtf.csrf import CSRFError

from approvalsystem.blueprints.auth import auth
from approvalsystem.blueprints.college import college
from approvalsystem.blueprints.school import school
from approvalsystem.blueprints.teacher import teacher
from approvalsystem.blueprints.user import user
from approvalsystem.extensions import bootstrap, ckeditor, db, login_manager, principals, archives, csrf, moment
from approvalsystem.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('approvalsystem')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_template_context(app)
    return app


def register_extensions(app):
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    principals.init_app(app)
    configure_uploads(app, archives)
    moment.init_app(app)
    csrf.init_app(app)


def register_template_context(app):
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # 设置当前用户身份为login登录对象
        identity.user = current_user
        # 添加UserNeed到identity user对象
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))
        # 每个Role添加到identity user对象，roles是User的多对多关联
        # 我们这里是  一个用户对应一个角色
        if hasattr(current_user, 'role'):
            identity.provides.add(RoleNeed(current_user.role.name))


def register_blueprints(app):
    app.register_blueprint(user)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(teacher, url_prefix='/teacher')
    app.register_blueprint(college, url_prefix='/college')
    app.register_blueprint(school, url_prefix='/school')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def page_not_found(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400
