from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from approvalsystem.extensions import db, school_permission
from approvalsystem.forms import ApprovalForm
from approvalsystem.models import Apply

school = Blueprint('school', __name__)


@school.route('/pending_approval/', methods=['GET', 'POST'])
@login_required
@school_permission.require(http_exception=403)
def pending_approval():
    form = ApprovalForm()
    if request.method == 'GET':
        school_apply = Apply.query.filter(Apply.s_id == current_user.id, Apply.status_id == 3).all()
        return render_template('school/pending_approval.html', school_apply=school_apply, form=form)
    else:
        id = request.form.get('id')
        apply = Apply.query.filter(Apply.id == id).first()
        apply.status_id += 1
        db.session.commit()
        return redirect(url_for('.pending_approval'))
