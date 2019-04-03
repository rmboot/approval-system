import os
import time

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required

from approvalsystem.extensions import db, archives, student_permission
from approvalsystem.forms import ApplyForm, MyApplyForm, FileApplyForm, CommentForm
from approvalsystem.models import Apply, Comment
from approvalsystem.utils import flash_errors, path, upload_file, file_path

user = Blueprint('user', __name__)


@user.route('/')
def index():
    # from approvalsystem.models import Users
    # user1 = Users(number='201508090009', name='Student1', dept_id=2, role_id=1)
    # user1.set_password('admin')
    # user2 = Users(number='201508090079', name='Student2', dept_id=2, role_id=1)
    # user2.set_password('admin')
    # user3 = Users(number='20150001', name='Teacher1', dept_id=2, role_id=2)
    # user3.set_password('admin')
    # user4 = Users(number='20150002', name='Teacher2', dept_id=2, role_id=2)
    # user4.set_password('admin')
    # user5 = Users(number='20150099', name='College1', dept_id=2, role_id=3)
    # user5.set_password('admin')
    # user6 = Users(number='00000001', name='School1', dept_id=1, role_id=4)
    # user6.set_password('admin')
    # db.session.add(user1)
    # db.session.add(user2)
    # db.session.add(user3)
    # db.session.add(user4)
    # db.session.add(user5)
    # db.session.add(user6)
    # db.session.commit()
    # print('测试数据插入OK')
    return render_template('user/index.html')


@user.route('/all_apply/', methods=['GET'])
def all_apply():
    apply = Apply.query.all()
    return render_template('user/all_apply.html', apply=apply)


@user.route('/my_apply/', methods=['GET', 'POST'])
@login_required
@student_permission.require(http_exception=403)
def my_apply():
    my_apply = Apply.query.filter(Apply.u_id == current_user.id).all()
    return render_template('user/my_apply.html', my_apply=my_apply)


@user.route('/my_apply/<int:id>/', methods=['GET', 'POST'])
@login_required
@student_permission.require(http_exception=403)
def my_apply_id(id):
    apply = Apply.query.get_or_404(id)
    comments = Comment.query.filter_by(apply_id=id).all()
    form = MyApplyForm()
    file_form = FileApplyForm()
    comment_form = CommentForm()
    if form.submit1.data and form.validate_on_submit():
        apply.name = form.name.data
        apply.t_id = form.t_id.data
        db.session.commit()
        flash('更改项目信息成功', 'success')
        return redirect(url_for('user.my_apply_id', id=id))
    if file_form.submit2.data and file_form.validate_on_submit():
        last_time = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        upload_file(last_time, id=id)
        apply.last_time = last_time
        db.session.commit()
        flash('上传项目文件成功', 'success')
        return redirect(url_for('user.my_apply_id', id=id))
    if comment_form.submit3.data and comment_form.validate_on_submit():
        body = comment_form.body.data
        new_comment = Comment(body=body, author_id=current_user.id, apply_id=id)
        db.session.add(new_comment)
        db.session.commit()
        # flash('评论成功', 'success')
        return redirect(url_for('user.my_apply_id', id=id))
    flash_errors(file_form)
    form.name.data = apply.name
    form.t_id.data = apply.t_id
    files_list = os.listdir(file_path(apply.inner_path))
    return render_template('user/my_apply_id.html', form=form, file_form=file_form, comment_form=comment_form,
                           apply=apply, comments=comments, files_list=files_list)


@user.route('/apply/', methods=['GET', 'POST'])
@login_required
@student_permission.require(http_exception=403)
def apply():
    form = ApplyForm()
    if form.validate_on_submit():
        name = form.name.data
        t_id = form.t_id.data
        last_time = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        apply = Apply(name=name, status_id=1, u_id=current_user.id, t_id=t_id, last_time=last_time)
        db.session.add(apply)
        db.session.commit()
        apply.inner_path = current_user.number+'/'+str(apply.id)
        db.session.commit()
        upload_file(last_time, id=apply.id)
        flash('提交项目申请成功', 'success')
        return redirect(url_for('.my_apply'))
    flash_errors(form)
    return render_template('user/apply.html', form=form)


@login_required
@student_permission.require(http_exception=403)
@user.route('/my_apply/open/', methods=['GET', 'POST'])
def open_file():
    id = request.args.get('id')
    filename = request.args.get('filename')
    file_url = archives.url(path(number=current_user.number, id=id, filename=filename))
    return redirect(file_url)


@login_required
@student_permission.require(http_exception=403)
@user.route('/my_apply/delete/', methods=['GET', 'POST'])
def delete_file():
    id = request.args.get('id')
    filename = request.args.get('filename')
    file = archives.path(filename, folder=path(number=current_user.number, id=id))
    os.remove(file)
    return redirect(request.referrer)
    # return redirect(url_for('.my_apply_id', id=id))


@user.route('/delete/comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    # flash('评论已删除', 'info')
    return redirect(request.referrer)
    # return redirect(url_for('.my_apply_id', id=comment.apply_id))
