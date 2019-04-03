from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from approvalsystem.extensions import db, college_permission
from approvalsystem.forms import ApprovalForm
from approvalsystem.models import Users, Apply

college = Blueprint('college',__name__)


@college.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@college_permission.require(http_exception=403)
def pending_approval():
    form = ApprovalForm()
    if request.method == 'GET':
        college_apply = Apply.query.filter(Apply.c_id == current_user.id, Apply.status_id == 2).all()
        school = Users.query.filter(Users.role_id == 4).all()
        return render_template('college/pending_approval.html', college_apply=college_apply, school=school, form=form)
    else:
        id = request.form.get('id')
        s_id = request.form.get('s_id')
        if s_id:
            apply = Apply.query.filter(Apply.id == id).first()
            apply.status_id += 1
            apply.s_id = s_id
            db.session.commit()
            return redirect(url_for('.pending_approval'))
        else:
            flash('未选择审批负责人')
            return redirect(url_for('.pending_approval'))
