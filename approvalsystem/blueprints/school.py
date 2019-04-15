import os


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approvalsystem.extensions import db, school_permission
from approvalsystem.forms import CommentForm
from approvalsystem.models import Apply, Comment
from approvalsystem.utils import file_path

school = Blueprint('school', __name__)


@school.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def pending_approval():
    if request.method == 'GET':
        school_apply = Apply.query.filter(Apply.s_id == current_user.id, Apply.status_id == 5).all()
        return render_template('school/pending_approval.html', apply=school_apply)
    else:
        pass_id = request.form.get('pass_id')
        if pass_id:
            apply = Apply.query.filter(Apply.id == pass_id).first()
            apply.status_id += 2
            db.session.commit()
            flash('审批通过', 'success')
            return redirect(url_for('.pending_approval'))
        else:
            reject_id = request.form.get('reject_id')
            apply = Apply.query.filter(Apply.id == reject_id).first()
            apply.status_id += 1
            db.session.commit()
            flash('已拒绝', 'warning')
            return redirect(url_for('.pending_approval'))


@school.route('/pending_approval/<int:id>/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
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
        return redirect(url_for('school.pending_approval_id', id=id))
    return render_template('school/pending_approval_id.html', apply=apply, files_list=files_list,comments=comments,comment_form=comment_form)


@school.route('/approved/', methods=['GET'])
@login_required
@school_permission.require(http_exception=403)
def approved():
    school_apply = Apply.query.filter(Apply.s_id == current_user.id, Apply.status_id > 5).all()
    return render_template('school/approved.html', apply=school_apply)
