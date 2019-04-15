import os


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approvalsystem.extensions import db, college_permission
from approvalsystem.forms import CommentForm
from approvalsystem.models import Users, Apply, Comment
from approvalsystem.utils import file_path

college = Blueprint('college',__name__)


@college.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@college_permission.require(http_exception=403)
def pending_approval():
    if request.method == 'GET':
        college_apply = Apply.query.filter(Apply.c_id == current_user.id, Apply.status_id == 3).all()
        school = Users.query.filter(Users.role_id == 4).all()
        return render_template('college/pending_approval.html', apply=college_apply, next=school)
    else:
        pass_id = request.form.get('pass_id')
        if pass_id:
            s_id = request.form.get('next_id')
            if s_id:
                apply = Apply.query.filter(Apply.id == pass_id).first()
                apply.status_id += 2
                apply.s_id = s_id
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


@college.route('/pending_approval/<int:id>/', methods=['GET', 'POST'])
@login_required
@college_permission.require(http_exception=403)
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
        return redirect(url_for('college.pending_approval_id', id=id))
    return render_template('college/pending_approval_id.html', apply=apply, files_list=files_list, comments=comments,comment_form=comment_form)


@college.route('/approved/', methods=['GET'])
@login_required
@college_permission.require(http_exception=403)
def approved():
    college_apply = Apply.query.filter(Apply.c_id == current_user.id, Apply.status_id > 3).all()
    return render_template('college/approved.html', apply=college_apply)
