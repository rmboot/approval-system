import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approval_system.extensions import db, school_permission
from approval_system.forms import CommentForm, NoticeForm, MyNoticeForm, UserSearchForm, PasswordResetForm
from approval_system.models import Apply, Comment, User, Notice
from approval_system.utils import file_path

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
    return render_template('school/pending_approval_id.html', apply=apply, files_list=files_list, comments=comments,
                           comment_form=comment_form)


@school.route('/approved/', methods=['GET'])
@login_required
@school_permission.require(http_exception=403)
def approved():
    school_apply = Apply.query.filter(Apply.s_id == current_user.id, Apply.status_id > 5).all()
    return render_template('school/approved.html', apply=school_apply)


@school.route('/publish_notice/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def publish_notice():
    form = NoticeForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        notice = Notice(title=title, body=body, author_id=current_user.id)
        db.session.add(notice)
        db.session.commit()
        flash('发布通告成功', 'success')
        return redirect(url_for('.notice_manager'))
    return render_template('school/publish_notice.html', form=form)


@school.route('/notice_manager/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def notice_manager():
    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 6))
        paginate = Notice.query.filter(Notice.author_id == current_user.id) \
            .order_by(Notice.id.desc()).paginate(page, per_page, error_out=False)
        notice_all = paginate.items
        return render_template('school/notice_manager.html', paginate=paginate, notice_all=notice_all)
    else:
        notice_id = request.form.get('notice_id')
        notice = Notice.query.filter(Notice.id == notice_id).first()
        db.session.delete(notice)
        db.session.commit()
        flash('删除公告成功', 'success')
        return redirect(url_for('.notice_manager'))


@school.route('/notice_manager/<int:id>/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def notice_manager_id(id):
    notice = Notice.query.get_or_404(id)
    form = MyNoticeForm()
    if form.submit.data and form.validate_on_submit():
        notice.title = form.title.data
        notice.body = form.body.data
        db.session.commit()
        return redirect(url_for('.notice_manager'))
    form.title.data = notice.title
    form.body.data = notice.body
    return render_template('school/notice_manager_id.html', form=form)


@school.route('/user_manager/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def user_manager():
    form = UserSearchForm()
    reset_form = PasswordResetForm()
    if form.submit.data and form.validate_on_submit():
        user = User.query.filter(User.number == form.number.data).first()
        if not user:
            flash('不存在该用户', 'warning')
        elif user.role_id == 4:
            flash('无法重置校审批处用户', 'warning')
        else:
            return render_template('school/user_manager.html', form=form, reset_form=reset_form, user=user)
    if reset_form.submit1.data and reset_form.validate_on_submit():
        user_id = request.form.get('user_id')
        new_password = reset_form.new_password.data
        user = User.query.filter(User.id == user_id).first()
        user.set_password(new_password)
        db.session.commit()
        flash('重置' + user.name + '密码成功', 'success')
        return redirect(url_for('.user_manager'))
    return render_template('school/user_manager.html', form=form)
