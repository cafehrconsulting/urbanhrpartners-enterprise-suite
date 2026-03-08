from flask import Blueprint, render_template

xiomy_bp = Blueprint("xiomy", __name__)

@xiomy_bp.route("/xiomy")
def xiomy():
    return render_template("xiomy.html")