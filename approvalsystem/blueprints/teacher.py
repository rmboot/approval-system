import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approvalsystem.extensions import db, teacher_permission, archives
from approvalsystem.forms import ApprovalForm, CommentForm
from approvalsystem.models import Users, Apply, Comment
from approvalsystem.utils import path, file_path

teacher = Blueprint('teacher', __name__)


@teacher.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@teacher_permission.require(http_exception=403)
def pending_approval():
    form = ApprovalForm()
    if request.method == 'GET':
        teacher_apply = Apply.query.filter(Apply.t_id == current_user.id, Apply.status_id == 1).all()
        college = Users.query.filter(Users.dept_id == current_user.dept_id, Users.role_id == 3).all()
        return render_template('teacher/pending_approval.html', teacher_apply=teacher_apply, college=college, form=form)
    else:
        id = request.form.get('id')
        c_id = request.form.get('c_id')
        if c_id:
            apply = Apply.query.filter(Apply.id == id).first()
            apply.status_id += 1
            apply.c_id = c_id
            db.session.commit()
            flash('审批通过', 'success')
            return redirect(url_for('.pending_approval'))
        else:
            flash('未选择审批负责人', 'warning')
            return redirect(url_for('.pending_approval'))


@teacher.route('/pending_approval/<int:id>/', methods=['GET', 'POST'])
@login_required
@teacher_permission.require(http_exception=403)
def pending_approval_id(id):
    apply = Apply.query.get_or_404(id)
    comments = Comment.query.filter_by(apply_id=id).all()
    files_list = os.listdir(file_path(apply.inner_path))
    comment_form = CommentForm()
    if comment_form.submit3.data and comment_form.validate_on_submit():
        body = comment_form.body.data
        new_comment = Comment(body=body, author_id=current_user.id, apply_id=id)
        db.session.add(new_comment)
        db.session.commit()
        # flash('评论成功', 'success')
        return redirect(url_for('teacher.pending_approval_id', id=id))
    return render_template('teacher/pending_approval_id.html', apply=apply, files_list=files_list,comments=comments,comment_form=comment_form)


@login_required
@teacher_permission.require(http_exception=403)
@teacher.route('/pending_approval/open/', methods=['GET', 'POST'])
def open_file():
    number = request.args.get('number')
    id = request.args.get('id')
    filename = request.args.get('filename')
    file_url = archives.url(path(number=number,id=id, filename=filename))
    return redirect(file_url)














"""
@teacher.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@teacher_permission.require(http_exception=403)
def pending_approval():
    form = ApprovalForm()
    teacher_apply = Apply.query.filter(Apply.t_id == current_user.id, Apply.status_id == 1).all()
    if form.validate_on_submit():
        id = teacher_apply.id
        c_id = form.c_id.data
        apply = Apply.query.filter(Apply.id == id).first()
        apply.status_id += 1
        apply.c_id = c_id
        db.session.commit()
        return redirect(url_for('.pending_approval'))

    return render_template('teacher/pending_approval.html', form=form, teacher_apply=teacher_apply)
"""
