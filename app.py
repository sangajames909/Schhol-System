import os
from os import path
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_bcrypt import generate_password_hash, check_password_hash
from Databases import Users, Assignments, Receipt, Submit
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "James12345678"
myconnection = path.dirname(path.realpath(__file__)) + "\\static\\resources"
UPLOAD_FOLDER = myconnection
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx'}
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# register
@app.route('/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["w"]
        email = request.form["x"]
        password = request.form["y"]
        studentid = request.form["z"]
        course = request.form["p"]
        role = request.form["role"]
        encrypted_password = generate_password_hash(password)
        Users.create(username=name, useremail=email, password=encrypted_password, studentID=studentid,
                     studentcourse=course, role=role)
        flash("Registered Successfully")
        return redirect(url_for("register"))
    return render_template("Register.html")


# login
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        useremail = request.form["x"]
        password = request.form["y"]
        studentId = request.form["z"]
        try:
            user = Users.get(Users.useremail == useremail)
            encrypted_password = user.password
            # user = Users.get(Users.studentID == studentId)
            if check_password_hash(encrypted_password, password):
                session["logged_in"] = True
                session["password"] = user.password
                session["name"] = user.useremail
                session["id"] = user.id
                flash("You have logged in successfully")
                if user.role == 1:
                    return redirect(url_for("students_table"))#admin
                elif user.role == 2:
                    return redirect(url_for("user_dashboard"))# teacher
                else:
                    return redirect(url_for("student_dashboard"))  # student

        except Users.DoesNotExist:
            flash("Wrong password or ID")
    return render_template("Login.html")

#logout
@app.route('/logout')
def logout():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    session.pop("logged_in",None)
    return redirect(url_for("login"))

# dashboard
@app.route('/dashboard')
def students_table():
    users = Users.select()
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("Dashboard.html", users=users)


# user dashboard
@app.route('/userdashboard')
def user_dashboard():
    users = Users.select()
    numberOfAdmins = 0
    numberOfTeachers = 0
    numberOfStudents = 0
    for user in users:
        if user.role == 1:
            numberOfAdmins+=1
        elif user.role == 2:
            numberOfTeachers+=1
        elif user.role == 3:
            numberOfStudents+=1
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("UserDashboard.html", users=users,numberOfAdmins=numberOfAdmins,numberOfTeachers=numberOfTeachers,numberOfStudents=numberOfStudents)


# student dashboard
@app.route('/studentdashboard')
def student_dashboard():
    users = Users.select()
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("StudentDashboard.html", users=users)


#deleting student dashboard
@app.route('/del/<int:id>')
def deletings(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Users.delete().where(Users.id == id).execute()
    return redirect(url_for("student_dashboard"))

# delete admin dashboard
@app.route('/deleted/<int:id>')
def deleted(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Users.delete().where(Users.id == id).execute()
    return redirect(url_for("students_table"))


# deleting userDashoard
@app.route('/user_deleting/<int:id>')
def dele(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Users.delete().where(Users.id == id).execute()
    return redirect(url_for("user_dashboard"))

# fees receipt
@app.route('/fees_receipt', methods=["POST", "GET"])
def feesreceipt():
    users = Users.select()
    if request.method == "POST":
        studentname = request.form["a"]
        studentclass = request.form["b"]
        date = request.form["c"]
        feesamount = request.form["d"]
        amountpaid = request.form["e"]
        balance = request.form["f"]
        studentID = request.form["student_id"]
        Receipt.create(studentname=studentname, studentclass=studentclass, date=date, feesamount=feesamount,
                       amountpaid=amountpaid, balance=balance,studentID = studentID)
        flash("Fees Paid")
        return redirect(url_for("feesreceipt"))
    return render_template("FeesReceipt.html", users=users)


# view fees payment
@app.route('/view_fees')
def view_fees():
    if not session.get("logged_in"):
        return redirect(url_for("view_fees"))
    paid = Receipt.select()
    return render_template("ViewFeesPaid.html", paid=paid)


# generate receipt
@app.route('/generate_receipt/<int:id>')
def generate_receipt(id):
    if not session.get("logged_in"):
        return redirect(url_for("generate_receipt"))
    receipt = Receipt.get(Receipt.studentID == id)
    return render_template("GenerateReceipt.html", receipt=receipt)


# fees delete
@app.route('/deleting/<int:id>')
def deleting(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Receipt.delete().where(Receipt.id == id).execute()
    return redirect(url_for("view_fees"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# post assignment
@app.route('/post_assignment', methods=["POST", "GET"])
def postassignment():
    if request.method == "POST":
        if 'z' not in request.files:
            flash('No file part')
            return redirect(url_for("postassignment"))
        assignment = request.form["v"]
        course = request.form["w"]
        startdate = request.form["x"]
        duedate = request.form["y"]
        file = request.files['z']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        Assignments.create(assignment_name=assignment, course_name=course, start_date=startdate, due_date=duedate,
                           file=file.filename)
        flash("Assignment Posted")
        return redirect(url_for("postassignment"))
    return render_template("PostAssignment.html", worked="worked")


# view assignment posted
@app.route('/view_assignment')
def view_assignment():
    if not session.get("logged_in"):
        return redirect(url_for("view_assignment"))
    assignments = Assignments.select()
    return render_template("ViewAssignment.html", assignments=assignments)


# view assignment delete
@app.route('/deleted/<int:id>')
def delete(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Assignments.delete().where(Assignments.id == id).execute()
    return redirect(url_for("view_assignment"))


# view assignment details
@app.route('/view_assignment_details/<int:id>')
def view_assignment_details(id):
   if not session.get("logged_in"):
       return redirect(url_for("login"))
   assignment = Assignments.get(Assignments.id == id)
   return render_template("ViewAssignmentDetails.html", assignment=assignment)


# view assignment update
@app.route('/update/<int:id>')
def update(id):
    if not session.get("logged_in"):
        return redirect(url_for("postassignment"))
    Assignments.delete().where(Assignments.id == id).execute()
    return redirect(url_for("postassignment"))



#student submitting assignment
@app.route('/submit_assignment',methods=["GET","POST"])
def submit_assignment():
    if not session.get("logged_in"):
        return redirect(url_for("submit_assignment"))
    submit = Submit.select()
    if request.method == "POST":
        if 'y' not in request.files:
            flash('No file part')
            return redirect(url_for("submit_assignment"))
        student_name =request.form["v"]
        assignment = request.form["w"]
        course = request.form["x"]
        file = request.files['y']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        Submit.create(student_name=student_name, assignment_name=assignment, course_name=course,file=file.filename)
        flash("Assignment Submitted")
        return redirect(url_for("submit_assignment"))
    return render_template("StudentAssignmentSubmit.html", submitted=submit)



# view assignment posted
@app.route('/view_student_assignment/<int:id>')
def view_student_assignment(id):
    if not session.get("logged_in"):
        return redirect(url_for("view_assignment"))
    assignment = Submit.get(Submit.id ==id)
    return render_template("ViewAssignmentPostedDetails.html", assignment=assignment)

# view assignment submitted by student
@app.route('/assignment_submit')
def assignment_submit():
    if not session.get("logged_in"):
        return redirect(url_for("assignment_submit"))
    assignments = Submit.select()
    return render_template("SubmittedAssignment.html", assignments=assignments)

#delete assignment submitted
@app.route('/delete_submit/<int:id>')
def submit_delete(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    Submit.delete().where(Submit.id == id).execute()
    return redirect(url_for("view_assignment"))

if __name__ == '__main__':
    app.run()
