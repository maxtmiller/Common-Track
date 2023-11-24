import os.path
import requests
import sqlite3

from cs50 import SQL
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, before_first_request, check_for_sql, clear_session, is_digit, authentication, check_for_calendar, create_calendar, check_for_events, events_in_calendar, create_event, delete_event


# From CS50 Module - (Configure application)
app = Flask(__name__)


# From CS50 Module - (Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# From CS50 Module - (Configure CS50 Library to use SQLite database)
db = SQL("sqlite:///storage.db")


# From CS50 Module
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.before_request
@before_first_request
def before_request():
    """Clear Session"""

    # Checks if college list is populated
    check_for_sql(app)

    # Calls function to redirect to login page only on app start
    clear_session(app)

    return


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Variable for storing error message
        error = None

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username!"
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password!"
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid username and/or password!"
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        print("success")
        return redirect("/my")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Variable for storing error message
        error = None

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username!"
            return render_template("register.html", error=error)

        # Ensure username is unique
        elif len(rows) != 0:
            error = "Username not available!"
            return render_template("register.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Missing password!"
            return render_template("register.html", error=error)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            error = "Passwords don't match!"
            return render_template("register.html", error=error)

        elif len(request.form.get("password")) < 6 or len(request.form.get("password")) > 15:
            error = "Password must be between 6 and 15 characters long!"
            return render_template("register.html", error=error)

        username = request.form.get("username")
        password = request.form.get("password")

        # Hashes password when before inserting into users table
        hash = generate_password_hash(password, method='pbkdf2', salt_length=16)

        db.execute("INSERT INTO USERS (username, hash) VALUES(?, ?)", username, hash)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        flash("Registered!")
        return redirect("/#")

    else:

        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add Colleges to My College List"""

    user_id = session["user_id"]
    scrollable = False

    rawcollegelist = db.execute("SELECT Common_App_Member FROM CollegeList;")

    collegelist = [college for college in rawcollegelist]

    if request.method == "POST":

        CollegeName = request.form.get("collegeSelect")

        print("CollegeName", CollegeName)

        ListCount = db.execute("SELECT COUNT(Common_App_Member) FROM MyCollegeList;")
        ListCount = ListCount[0]['COUNT(Common_App_Member)']

        ExistingCollegeCount = db.execute("SELECT COUNT(Common_App_Member) FROM MyCollegeList WHERE Common_App_Member = ?;", CollegeName)
        ExistingCollegeCount = ExistingCollegeCount[0]['COUNT(Common_App_Member)']

        RawCollegeInfo = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member = ?;", CollegeName)
        RCI = RawCollegeInfo[0]

        CollegeCount = db.execute("SELECT COUNT(Common_App_Member) FROM CollegeList WHERE Common_App_Member = ?;", CollegeName)
        CollegeCount = CollegeCount[0]['COUNT(Common_App_Member)']

        if ExistingCollegeCount == 0 and ListCount < 20:
            flash("College Added!")
            db.execute("INSERT INTO MyCollegeList (Common_App_Member, School_Type, ED, EDII, EA, EAII, REA, RD_Rolling, US, INTL, Personal_Essay_Req_d, C_G, Portfolio, Writing, Test_Policy, SAT_ACT_Tests_Used, INTL_1, TE, OE, MR, CR, Saves_Forms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", RCI['Common_App_Member'], RCI['School_Type'], RCI['ED'], RCI['EDII'], RCI['EA'], RCI['EAII'], RCI['REA'], RCI['RD_Rolling'], RCI['US'], RCI['INTL'], RCI['Personal_Essay_Req_d'], RCI['C_G'], RCI['Portfolio'], RCI['Writing'], RCI['Test_Policy'], RCI['SAT_ACT_Tests_Used'], RCI['INTL_1'], RCI['TE'], RCI['OE'], RCI['MR'], RCI['CR'], RCI['Saves_Forms'])
        elif ListCount >= 20:
            flash("College list at capacity!")
        elif ExistingCollegeCount != 0:
            flash("College already in list!")

        RawCollegeInfo = db.execute("SELECT * FROM MyCollegeList;")

        CollegeCount = db.execute("SELECT COUNT(Common_App_Member) FROM MyCollegeList;")
        CollegeCount = CollegeCount[0]['COUNT(Common_App_Member)']

        CollegeInfo = [college for college in RawCollegeInfo]

        for college in CollegeInfo:
            if college["Test_Policy"] == "A":
                college["Test_Policy"] = "Always Required"
            elif college["Test_Policy"] == "F":
                college["Test_Policy"] = "Flexible"
            elif college["Test_Policy"] == "I":
                college["Test_Policy"] = "Ignored"
            elif college["Test_Policy"] == "N":
                college["Test_Policy"] = "Never Required"
            elif college["Test_Policy"] == "S":
                college["Test_Policy"] = "Sometimes Required"

        return redirect("/my")

    else:

        return render_template("add.html", user_id=user_id, collegelist=collegelist, scrollable=scrollable)


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Remove Colleges from My College List"""

    user_id = session["user_id"]
    scrollable = False

    rawcollegelist = db.execute("SELECT Common_App_Member FROM MyCollegeList ORDER BY Common_App_Member ASC;")

    collegelist = [college for college in rawcollegelist]

    if request.method == "POST":

        CollegeName = request.form.get("collegeSelect")

        db.execute("DELETE FROM MyCollegeList WHERE Common_App_Member = ?;", CollegeName)

        flash("College Removed!")

        RawCollegeInfo = db.execute("SELECT * FROM MyCollegeList ORDER BY Common_App_Member ASC;")

        CollegeInfo = [college for college in RawCollegeInfo]

        for college in CollegeInfo:
            if college["Test_Policy"] == "A":
                college["Test_Policy"] = "Always Required"
            elif college["Test_Policy"] == "F":
                college["Test_Policy"] = "Flexible"
            elif college["Test_Policy"] == "I":
                college["Test_Policy"] = "Ignored"
            elif college["Test_Policy"] == "N":
                college["Test_Policy"] = "Never Required"
            elif college["Test_Policy"] == "S":
                college["Test_Policy"] = "Sometimes Required"

        return redirect("/my")

    else:

        return render_template("remove.html", user_id=user_id, collegelist=collegelist, scrollable=scrollable)


@app.route("/edit_list", methods=["GET", "POST"])
@login_required
def edit_list():
    """Edit college deadlines from calendar"""

    user_id = session["user_id"]
    scrollable = False

    return render_template("edit_list.html", user_id=user_id, scrollable=scrollable)


@app.route('/search', methods=['POST'])
def search():
    """Searching"""

    user_id = session["user_id"]

    search_term = request.json['searchTerm']
    currentEndpoint = request.json['currentEndpoint']

    if currentEndpoint == "add":
        results = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ? ORDER BY Common_App_Member ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))

    elif currentEndpoint == "remove":
        results = db.execute("SELECT * FROM MyCollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ? ORDER BY Common_App_Member ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))

    elif currentEndpoint == "calendar":
        resList = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ? ORDER BY Common_App_Member ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))
        results = []

        service = authentication()
        calendarId = check_for_calendar(service)

        if calendarId == False:
            calendarId = create_calendar(service)

        deadlines = None

        for i in range(0, len(resList)):
            print("Looping", i, resList[i]['Common_App_Member'])

    elif currentEndpoint == "add_event":
        results = db.execute("SELECT * FROM MyCollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ? ORDER BY Common_App_Member ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))

    elif currentEndpoint == "search_ranking":
        results = db.execute("SELECT * FROM CollegeRanking WHERE institution LIKE ? OR institution LIKE ? OR institution LIKE ? ORDER BY institution ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))

    elif currentEndpoint == "search_list":
        results = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ? ORDER BY Common_App_Member ASC;", (search_term + '%'), ('%' + search_term + '%'), (search_term + '%',))

    else:
        results = None

    return results


@app.route("/search_list", methods=["GET", "POST"])
@login_required
def search_list():
    """View different Coleges"""

    user_id = session["user_id"]
    scrollable = False

    rawcollegelist = db.execute("SELECT Common_App_Member FROM CollegeList")

    collegelist = [college for college in rawcollegelist]

    if request.method == "POST":

        CollegeName = request.form.get("collegeSelect")

        RawCollegeInfo = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))

        CollegeCount = db.execute("SELECT COUNT(Common_App_Member) FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))
        CollegeCount = CollegeCount[0]['COUNT(Common_App_Member)']

        CollegeInfo = [college for college in RawCollegeInfo]

        for college in CollegeInfo:
            if college["Test_Policy"] == "A":
                college["Test_Policy"] = "Always Required"
            elif college["Test_Policy"] == "F":
                college["Test_Policy"] = "Flexible"
            elif college["Test_Policy"] == "I":
                college["Test_Policy"] = "Ignored"
            elif college["Test_Policy"] == "N":
                college["Test_Policy"] = "Never Required"
            elif college["Test_Policy"] == "S":
                college["Test_Policy"] = "Sometimes Required"

        for college in CollegeInfo:
            RawCollegeRanking = db.execute("SELECT rank_display_2024, size, status, ar_score, er_score, isr_score, irn_score, sus_score, overall_score FROM CollegeRanking WHERE institution LIKE ? OR institution LIKE ? OR institution LIKE ?;", (college["Common_App_Member"] + '%'), ('%' + college["Common_App_Member"] + '%'), (college["Common_App_Member"] + '%',))

            if not RawCollegeRanking:
                RawCollegeRanking = {'rank_display_2024': '-', 'size': '-', 'status': '-', 'size': '-', 'ar_score': '-', 'er_score': '-', 'isr_score': '-', 'irn_score': '-', 'sus_score': '-', 'overall_score': '-'}
            else:
                RawCollegeRanking = RawCollegeRanking[0]

            college.update(RawCollegeRanking)

        for college in CollegeInfo:
            if college["status"] == "A":
                college["status"] = "Public"
            elif college["status"] == "B":
                college["status"] = "Private"
            elif college["status"] == "NULL":
                college["status"] = "-"

        return render_template("searched_list.html", CollegeInfo=CollegeInfo, scrollable=scrollable)

    else:

        return render_template("search_list.html", collegelist=collegelist, scrollable=scrollable)



@app.route("/my", methods=["GET"])
@login_required
def my():
    """View different Coleges"""

    user_id = session["user_id"]
    scrollable = True
    short = False

    RawCollegeInfo = db.execute("SELECT * FROM MyCollegeList ORDER BY Common_App_Member ASC;")

    CollegeCount = db.execute("SELECT COUNT(Common_App_Member) FROM MyCollegeList;")
    CollegeCount = CollegeCount[0]['COUNT(Common_App_Member)']

    CollegeInfo = [college for college in RawCollegeInfo]

    for college in CollegeInfo:
        if college["Test_Policy"] == "A":
            college["Test_Policy"] = "Always Required"
        elif college["Test_Policy"] == "F":
            college["Test_Policy"] = "Flexible"
        elif college["Test_Policy"] == "I":
            college["Test_Policy"] = "Ignored"
        elif college["Test_Policy"] == "N":
            college["Test_Policy"] = "Never Required"
        elif college["Test_Policy"] == "S":
            college["Test_Policy"] = "Sometimes Required"

    for college in CollegeInfo:
        RawCollegeRanking = db.execute("SELECT rank_display_2024, size, status FROM CollegeRanking WHERE institution = ?", college["Common_App_Member"])

        if not RawCollegeRanking:
            print("empty")
            RawCollegeRanking = {'rank_display_2024': '-', 'size': '-', 'status': '-'}
        else:
            RawCollegeRanking = RawCollegeRanking[0]

        college.update(RawCollegeRanking)

    for college in CollegeInfo:
        if college["status"] == "A":
            college["status"] = "Public"
        elif college["status"] == "B":
            college["status"] = "Private"
        elif college["status"] == "NULL":
            college["status"] = "-"
    
    if CollegeCount <= 13:
        short = True

    return render_template("my.html", CollegeInfo=CollegeInfo, CollegeCount=CollegeCount, short=short, scrollable=scrollable)


@app.route("/add_event", methods=["GET", "POST"])
@login_required
def add_event():
    """Add college deadline to calendar"""

    user_id = session["user_id"]
    scrollable = False
    noDate = False

    rawcollegelist = db.execute("SELECT Common_App_Member, School_Type, RD_Rolling, US, Personal_Essay_Req_d FROM MyCollegeList ORDER BY Common_App_Member ASC;")

    collegelist = [college for college in rawcollegelist]

    if request.method == "POST":

        isDuplicate = False
        isSubmitted = False
        isNoDate = True
        deadline = None
        calendarId = None

        CollegeName = request.form.get("college")
        deadline = request.form.get("deadline")

        RawCollegeInfo = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))
        RawCollegeInfo = RawCollegeInfo[0]
        RawCollegeInfo = {key: value for key, value in RawCollegeInfo.items() if value is not None}

        date = RawCollegeInfo[deadline].replace(" ", "T")
        college_name = RawCollegeInfo['Common_App_Member']

        if is_digit(date) == True:
            isNoDate = False


        if isNoDate == False:

            service = authentication()
            calendarId = check_for_calendar(service)

            if calendarId == False:
                calendarId = create_calendar(service)

            isDuplicate = check_for_events(college_name, deadline, date, calendarId)
            create_event(service, college_name, deadline, date, isDuplicate, isSubmitted, calendarId)

            if isDuplicate:
                isSubmitted = False
            else:
                isSubmitted = True

        if isNoDate:
            flash("No specfic dates available for "+CollegeName+"!")
        elif isDuplicate:
            flash("Event already exists for "+CollegeName+"!")
        elif isSubmitted:
            flash(deadline+" Deadline for "+CollegeName+" added for "+date+"!")

        return redirect("/calendar")

    else:

        return render_template("add_event.html", user_id=user_id, noDate=noDate, collegelist=collegelist, scrollable=scrollable)


@app.route("/remove_event", methods=["GET", "POST"])
@login_required
def remove_event():
    """Remove college deadline from calendar"""

    user_id = session["user_id"]
    scrollable = False
    noDate = False

    service = authentication()
    calendarId = check_for_calendar(service)

    if calendarId == False:
        calendarId = create_calendar(service)

    collegelist = sorted(events_in_calendar(calendarId), key=lambda x: x['name'])

    unique_names = set()
    unique_data = []

    for item in collegelist:
        name = item['name']
        if name not in unique_names:
            unique_names.add(name)
            unique_data.append(item)

    collegelist = unique_data

    if request.method == "POST":

        isDuplicate = False
        isSubmitted = False
        isNoDate = True
        deadline = None
        calendarId = None

        CollegeName = request.form.get("college")
        deadline = request.form.get("deadline")

        RawCollegeInfo = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))
        RawCollegeInfo = RawCollegeInfo[0]
        RawCollegeInfo = {key: value for key, value in RawCollegeInfo.items() if value is not None}

        date = RawCollegeInfo[deadline].replace(" ", "T")
        college_name = RawCollegeInfo['Common_App_Member']

        if is_digit(date) == True:
            isNoDate = False

        if isNoDate == False:

            service = authentication()
            calendarId = check_for_calendar(service)

            if calendarId == False:
                calendarId = create_calendar(service)

            isDuplicate = check_for_events(college_name, deadline, date, calendarId)
            delete_event(service, college_name, deadline, date, isDuplicate, isSubmitted, calendarId)

            if isDuplicate:
                isSubmitted = False
            else:
                isSubmitted = True

            if isNoDate:
                flash("No specfic dates available for "+CollegeName+"!")
            elif isDuplicate:
                flash("Event already exists for "+CollegeName+"!")
            elif isSubmitted:
                flash(deadline+" Deadline for "+CollegeName+" removed!")

        return redirect("/calendar")

    else:

        return render_template("remove_event.html", user_id=user_id, noDate=noDate, collegelist=collegelist, scrollable=scrollable)


@app.route("/edit_event", methods=["GET", "POST"])
@login_required
def edit_event():
    """Edit college deadlines from calendar"""

    user_id = session["user_id"]
    scrollable = False

    return render_template("edit_event.html", user_id=user_id, scrollable=scrollable)


@app.route("/calendar", methods=["GET", "POST"])
@login_required
def calendar():
    """ View College Calendar"""

    service = authentication()
    calendarId = check_for_calendar(service)

    if calendarId == False:
        calendarId = create_calendar(service)

    calendarId = calendarId.split('@')[0]
    calendarId = "https://calendar.google.com/calendar/embed?src="+calendarId+"%40group.calendar.google.com&ctz=Europe%2FBerlin"

    return render_template("calendar.html", calendarId=calendarId)


@app.route("/deadline", methods=["POST"])
def deadline():
    """deadlines"""

    selectedTerm = request.json['selectedTerm']
    currentEndpoint = request.json['currentEndpoint']

    deadlines = []

    if currentEndpoint == "add_event":

        RawCollegeInfo = db.execute("SELECT * FROM CollegeList WHERE Common_App_Member LIKE ? OR Common_App_Member LIKE ? OR Common_App_Member LIKE ?;", (selectedTerm + '%'), ('%' + selectedTerm + '%'), (selectedTerm + '%',))
        RawCollegeInfo = RawCollegeInfo[0]
        RawCollegeInfo = {key: value for key, value in RawCollegeInfo.items() if value is not None}

        deadlines = ['ED', 'EDII', 'EA', 'EAII', 'REA', 'RD_Rolling']
        deadlines = [{'key': key, 'date': RawCollegeInfo[key]} for key in deadlines if key in RawCollegeInfo and RawCollegeInfo[key] is not None]

    elif currentEndpoint == "remove_event":

        service = authentication()
        calendarId = check_for_calendar(service)

        if calendarId == False:
            calendarId = create_calendar(service)

        collegelist = events_in_calendar(calendarId)

        for college in collegelist:
            if college['name'] == selectedTerm:
                print("collegelist", college['name'])
                deadlines.append(college['deadline'].split()[0])

    return deadlines


@app.route("/all", methods=["GET"])
@login_required
def all():
    """Show all colleges"""

    user_id = session["user_id"]
    scrollable = True

    rawcollegelist = db.execute("SELECT Common_App_Member, School_Type, RD_Rolling, US, Personal_Essay_Req_d FROM CollegeList;")

    collegelist = [college for college in rawcollegelist]

    return render_template("all.html", collegelist=collegelist, scrollable=scrollable)


@app.route('/ranking', methods=['GET'])
@login_required
def ranking():
    """Displays Top US College Ranking from QS Data"""

    user_id = session["user_id"]
    scrollable = True

    RawCollegeList = db.execute("SELECT rank_display_2024, institution, size, focus, research, status, overall_score FROM CollegeRanking;")

    CollegeRank = [college for college in RawCollegeList]

    for college in CollegeRank:
        if college["status"] == "A":
            college["status"] = "Public"
        elif college["status"] == "B":
            college["status"] = "Private"
        elif college["status"] == "NULL":
            college["status"] = ""

    return render_template("ranking.html", CollegeRank=CollegeRank, scrollable=scrollable)


@app.route('/search_ranking', methods=['GET', 'POST'])
@login_required
def search_ranking():
    """Searches Ranking Info for Colleges"""

    user_id = session["user_id"]
    scrollable = False

    rawcollegelist = db.execute("SELECT institution FROM CollegeRanking ORDER BY institution ASC;")

    collegelist = [college for college in rawcollegelist]

    if request.method == "POST":

        CollegeName = request.form.get("collegeSelect")

        RawCollegeInfo = db.execute("SELECT rank_display_2024, institution, size, status, ar_score, er_score, fsr_score, cpf_score, ifr_score, isr_score, irn_score, ger_score, sus_score, overall_score FROM CollegeRanking WHERE institution LIKE ? OR institution LIKE ? OR institution LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))

        CollegeCount = db.execute("SELECT COUNT(institution) FROM CollegeRanking WHERE institution LIKE ? OR institution LIKE ? OR institution LIKE ?;", (CollegeName + '%'), ('%' + CollegeName + '%'), (CollegeName + '%',))
        CollegeCount = CollegeCount[0]['COUNT(institution)']

        CollegeInfo = [college for college in RawCollegeInfo]

        for college in CollegeInfo:
            if college["status"] == "A":
                college["status"] = "Public"
            elif college["status"] == "B":
                college["status"] = "Private"
            elif college["status"] == "NULL":
                college["status"] = "-"

        if CollegeCount == 0:

            return render_template("search_ranking.html", collegelist=collegelist, scrollable=scrollable)

        elif CollegeInfo is None:

            return render_template("search_ranking.html", collegelist=collegelist, scrollable=scrollable)

        else:

            return render_template("searched_ranking.html", CollegeInfo=CollegeInfo, scrollable=scrollable)

    else:

        return render_template("search_ranking.html", collegelist=collegelist, scrollable=scrollable)


@app.route("/breakdown")
@login_required
def breakdown():
    """Breakdown Page"""

    user_id = session["user_id"]
    scrollable = True

    return render_template("breakdown.html", scrollable=scrollable)


@app.route('/about', methods=['GET'])
@login_required
def about():
    """About Section"""

    user_id = session["user_id"]
    scrollable = True

    return render_template("about.html", scrollable=scrollable)


if __name__ == "__main__":
    app.run(port=3000, debug=True)