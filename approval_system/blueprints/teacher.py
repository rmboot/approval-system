import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approval_system.extensions import db, teacher_permission
from approval_system.forms import CommentForm
from approval_system.models import User, Apply, Comment
from approval_system.utils import file_path

teacher = Blueprint('teacher', __name__)


@teacher.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@teacher_permission.require(http_exception=403)
def pending_approval():
    if request.method == 'GET':
        teacher_apply = Apply.query.filter(Apply.t_id == current_user.id, Apply.status_id == 1).all()
        college = User.query.filter(User.dept_id == current_user.dept_id, User.role_id == 3).all()
        return render_template('teacher/pending_approval.html', apply=teacher_apply, next=college)
    else:
        pass_id = request.form.get('pass_id')
        if pass_id:
            c_id = request.form.get('next_id')
            if c_id:
                apply = Apply.query.filter(Apply.id == pass_id).first()
                apply.status_id += 2
                apply.c_id = c_id
                db.session.commit()
                flash('审批通过', 'success')
                return redirect(url_for('.pending_approval'))
            else:
                flash('未选择审批负责人', 'warning')
                return redirect(url_for('.pending_approval'))
        else:
            reject_id = request.form.get('reject_id')
            apply = Apply.query.filter(Apply.id == reject_id).first()
            apply.status_id += 1
            db.session.commit()
            flash('已拒绝', 'warning')
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
        return redirect(url_for('teacher.pending_approval_id', id=id))
    return render_template('teacher/pending_approval_id.html', apply=apply, files_list=files_list,comments=comments,comment_form=comment_form)


@teacher.route('/approved/', methods=['GET'])
@login_required
@teacher_permission.require(http_exception=403)
def approved():
    teacher_apply = Apply.query.filter(Apply.t_id == current_user.id, Apply.status_id > 1).all()
    return render_template('teacher/approved.html', apply=teacher_apply)
