from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from approvalsystem.extensions import db


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', foreign_keys=[role_id])
    dept_id = db.Column(db.Integer, db.ForeignKey('dept.id'))
    dept = db.relationship('Dept', foreign_keys=[dept_id])
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    info = db.Column(db.String(100))


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)


class Dept(db.Model):
    __tablename__ = 'dept'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)


class Apply(db.Model):
    __tablename__ = 'apply'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    info = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship('Status', foreign_keys=[status_id])
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', foreign_keys=[u_id])
    t_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher = db.relationship('Users', foreign_keys=[t_id])
    c_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    college = db.relationship('Users', foreign_keys=[c_id])
    s_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    school = db.relationship('Users', foreign_keys=[s_id])
    inner_path = db.Column(db.String(128))
    last_time = db.Column(db.String(128))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('Users', foreign_keys=[author_id])
    apply_id = db.Column(db.Integer, db.ForeignKey('apply.id'))
    apply = db.relationship('Apply', foreign_keys=[apply_id])
