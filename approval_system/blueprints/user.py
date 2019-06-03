import os
import time

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from flask_ckeditor import upload_success, upload_fail

from approval_system.extensions import db, archives, student_permission
from approval_system.forms import ApplyForm, MyApplyForm, FileApplyForm, CommentForm, ReApplyForm
from approval_system.models import Apply, Comment, Notice
from approval_system.utils import flash_errors, upload_file, file_path

user = Blueprint('user', __name__)


@user.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 8))
    paginate = Notice.query.order_by(Notice.id.desc()).paginate(page, per_page, error_out=False)
    notice = paginate.items
    # from approval_system.models import User
    # user1 = User(number='201508090009', name='Student1', dept_id=2, role_id=1, phone='10010001000')
    # user1.set_password('admin')
    # user2 = User(number='201508090079', name='Student2', dept_id=2, role_id=1, phone='10010001000')
    # user2.set_password('admin')
    # user3 = User(number='20150001', name='Teacher1', dept_id=2, role_id=2, phone='10010001000')
    # user3.set_password('admin')
    # user4 = User(number='20150002', name='Teacher2', dept_id=2, role_id=2, phone='10010001000')
    # user4.set_password('admin')
    # user5 = User(number='20150099', name='College1', dept_id=2, role_id=3, phone='10010001000')
    # user5.set_password('admin')
    # user6 = User(number='00000001', name='School1', dept_id=1, role_id=4, phone='10010001000')
    # user6.set_password('admin')
    # db.session.add(user1)
    # db.session.add(user2)
    # db.session.add(user3)
    # db.session.add(user4)
    # db.session.add(user5)
    # db.session.add(user6)
    # db.session.commit()
    # print('测试数据插入OK')
    return render_template('user/index.html', paginate=paginate, notice=notice)


@user.route('/notice/<int:id>/', methods=['GET', 'POST'])
def notice_id(id):
    notice = Notice.query.get_or_404(id)
    return render_template('user/notice_id.html', notice=notice)


@user.route('/all_apply/', methods=['GET'])
def all_apply():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 8))
    paginate = Apply.query.order_by(Apply.id.desc()).paginate(page, per_page, error_out=False)
    apply = paginate.items
    return render_template('user/all_apply.html', paginate=paginate, apply=apply)


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
    if apply.status_id % 2 == 0:
        reapply_form = ReApplyForm()
    else:
        reapply_form = None
    if form.submit1.data and form.validate_on_submit():
        apply.name = form.name.data
        apply.info = form.info.data
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
        return redirect(url_for('user.my_apply_id', id=id))
    if reapply_form and reapply_form.submit0.data and reapply_form.validate_on_submit():
        apply.status_id = 1
        apply.t_id = reapply_form.t_id.data
        apply.s_id, apply.c_id = None, None
        apply.last_time = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        for i in comments:
            db.session.delete(i)
        db.session.commit()
        flash('项目已重新申请', 'success')
        return redirect(url_for('user.my_apply'))
    flash_errors(file_form)
    form.name.data = apply.name
    form.info.data = apply.info
    files_list = os.listdir(file_path(apply.inner_path))
    return render_template('user/my_apply_id.html', form=form, file_form=file_form, comment_form=comment_form,
                           reapply_form=reapply_form, apply=apply, comments=comments, files_list=files_list)


@user.route('/apply/', methods=['GET', 'POST'])
@login_required
@student_permission.require(http_exception=403)
def apply():
    form = ApplyForm()
    if form.validate_on_submit():
        name = form.name.data
        info = form.info.data
        t_id = form.t_id.data
        last_time = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        apply = Apply(name=name, info=info, status_id=1, u_id=current_user.id, t_id=t_id, last_time=last_time)
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
@user.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    inner_path = current_user.number
    f.save(file_path(inner_path)+'/'+f.filename)
    url = archives.url(inner_path+'/'+f.filename)
    return upload_success(url, f.filename)


@login_required
@user.route('/my_apply/open/', methods=['GET'])
def open_file():
    inner_path = request.args.get('inner_path')
    filename = request.args.get('filename')
    file_url = archives.url(inner_path+'/'+filename)
    return redirect(file_url)


@login_required
@student_permission.require(http_exception=403)
@user.route('/my_apply/delete/', methods=['GET'])
def delete_file():
    inner_path = request.args.get('inner_path')
    filename = request.args.get('filename')
    file = archives.path(filename, folder=inner_path)
    os.remove(file)
    return redirect(request.referrer)


@user.route('/delete/comment/<int:comment_id>', methods=['GET'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)
