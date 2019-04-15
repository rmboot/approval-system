from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, current_user, login_required, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from approvalsystem.extensions import db
from approvalsystem.forms import LoginForm, RegisterForm, RegisterAdminForm, SettingForm, PasswordForm
from approvalsystem.models import Users

auth = Blueprint('auth', __name__)


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = LoginForm()
    if form.validate_on_submit():
        number = form.number.data
        password = form.password.data
        remember = form.remember.data
        user = Users.query.filter(Users.number == number).first()
        if user:
            if number == user.number and user.validate_password(password):
                login_user(user, remember)
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                flash('登录成功', 'success')
                return redirect(request.args.get('next') or url_for('user.index'))
            flash('密码错误', 'warning')
            return redirect(url_for('.login'))
        flash('用户名错误', 'warning')
        return redirect(url_for('.login'))
    return render_template('auth/login.html', form=form)


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        number = form.number.data
        name = form.name.data
        dept_id = form.dept_id.data
        phone = form.phone.data
        password = form.password.data
        user = Users(number=number, name=name, dept_id=dept_id, phone=phone,role_id=1)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        flash('注册成功,已登录', 'success')
        return redirect(url_for('user.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    form = RegisterAdminForm()
    if form.validate_on_submit():
        number = form.number.data
        name = form.name.data
        dept_id = form.dept_id.data
        role_id = form.role_id.data
        phone = form.phone.data
        password = form.password.data
        user = Users(number=number, name=name, dept_id=dept_id, role_id=role_id, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        flash('注册成功,已登录', 'success')
        return redirect(url_for('user.index'))
    return render_template('auth/register_admin.html', form=form)


@auth.route('/setting/', methods=['GET', 'POST'])
@login_required
def setting():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.number = form.number.data
        current_user.name = form.name.data
        current_user.dept_id = form.dept_id.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('.setting'))
    form.number.data = current_user.number
    form.name.data = current_user.name
    form.dept_id.data = current_user.dept_id
    form.phone.data = current_user.phone
    return render_template('auth/setting.html', form=form)


@auth.route('/password/', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        current_user.set_password(password)
        db.session.commit()
        flash('更改密码成功', 'success')
        return redirect(url_for('user.index'))
    return render_template('auth/password.html', form=form)


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    flash('已注销', 'success')
    return redirect(url_for('user.index'))
