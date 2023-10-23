#stores all the url and blueticks means it has url or roots inside it
from flask import Blueprint, render_template
from flask_login import login_required, current_user
views =Blueprint('views',__name__)

@views.route('/', methods=['GET', 'POST'])

def home():
    return render_template("home.html", user=current_user)
 