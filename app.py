\
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "railway_system"),
        port=int(os.getenv("DB_PORT", "3306")),
        autocommit=True,
    )

def query(sql, args=None, fetch="all"):
    conn = get_db()
    cur = conn.cursor(dictionary=True, buffered=True)
    cur.execute(sql, args or ())
    rows = None
    if fetch == "one":
        rows = cur.fetchone()
    elif fetch == "all":
        rows = cur.fetchall()
    else:
        rows = None
    cur.close()
    conn.close()
    return rows

def execute(sql, args=None):
    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.execute(sql, args or ())
    conn.commit()
    cur.close()
    conn.close()

def call_proc(name, args):
    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.callproc(name, args)
    # Stored procs may return OUT params; fetch from cur.stored_results() or args itself
    results = []
    for result in cur.stored_results():
        results.append(result.fetchall())
    cur.close()
    conn.close()
    return results

@app.route("/")
def home():
    if session.get("role") == "admin":
        return redirect(url_for("admin"))
    if session.get("role") == "passenger":
        return redirect(url_for("user_dashboard"))
    return redirect(url_for("login"))

# ----------------- Auth -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # Admin via env bypass
        if email == os.getenv("ADMIN_EMAIL") and password == os.getenv("ADMIN_PASSWORD"):
            session["user_id"] = "ADMIN"
            session["name"] = "Administrator"
            session["role"] = "admin"
            flash("Logged in as admin.", "success")
            return redirect(url_for("admin"))

        # Otherwise from user table
        row = query("SELECT * FROM user WHERE email=%s AND password=%s", (email, password), fetch="one")
        if row:
            session["user_id"] = row["user_id"]
            session["name"] = row["name"]
            session["role"] = row["role"] or "passenger"
            flash("Login successful.", "success")
            return redirect(url_for("user_dashboard" if session["role"] != "admin" else "admin"))
        else:
            flash("Invalid credentials.", "error")

    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        try:
            execute(
                "INSERT INTO user (user_id, name, email, password, dob, gender, city, state, pin_code, role) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'passenger')",
                (
                    f.get("user_id"), f.get("name"), f.get("email"), f.get("password"),
                    f.get("dob") or None, f.get("gender") or None,
                    f.get("city"), f.get("state"), f.get("pin_code")
                )
            )
            if f.get("mobile"):
                execute("INSERT INTO user_mobile (user_id, mobile_no) VALUES (%s,%s)", (f.get("user_id"), f.get("mobile")))
            flash("Account created. Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as e:
            flash(f"Registration error: {e}", "error")
    return render_template("register.html", title="Register")

# --------------- User --------------------
def login_required(role=None):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please login.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("home"))
            return fn(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/user")
@login_required(role="passenger")
def user_dashboard():
    return render_template("user_dashboard.html", title="User")

@app.route("/search", methods=["GET"])
@login_required(role="passenger")
def search_trains():
    trains = None
    source = request.args.get("source")
    destination = request.args.get("destination")
    date = request.args.get("date")

    if source and destination and date:
        # use stored procedure search_trains
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        try:
            cur.callproc("search_trains", (source, destination, date))
            for result in cur.stored_results():
                trains = result.fetchall()
                break
        except mysql.connector.Error as e:
            flash(f"Search error: {e}", "error")
        finally:
            cur.close(); conn.close()
    return render_template("search_trains.html", title="Search Trains", trains=trains)

@app.route("/train/<train_no>")
@login_required(role="passenger")
def train_detail(train_no):
    source = request.args.get("source")
    destination = request.args.get("destination")
    date = request.args.get("date")

    train = query("SELECT * FROM train WHERE train_no=%s", (train_no,), fetch="one")
    if not train:
        flash("Train not found", "error")
        return redirect(url_for("search_trains"))

    # fetch classes for the train and availability via function get_available_seats
    classes = query("SELECT class_id, class_name, coach_type FROM class WHERE train_no=%s", (train_no,))
    classes_info = []
    for c in classes:
        available = 0
        if date:
            row = query("SELECT get_available_seats(%s,%s,%s) AS seats", (train_no, c["class_id"], date), fetch="one")
            available = (row["seats"] if row and row["seats"] is not None else 0)
        classes_info.append({
            "class_id": c["class_id"],
            "class_name": c["class_name"],
            "coach_type": c["coach_type"],
            "available": available
        })

    return render_template("train_detail.html",
                           title="Train Detail",
                           train=train, classes=classes_info,
                           source=source, destination=destination, date=date)

@app.route("/book/<train_no>", methods=["POST"])
@login_required(role="passenger")
def book_train(train_no):
    user_id = session.get("user_id")
    date = request.form.get("date")
    source = request.form.get("source")
    destination = request.form.get("destination")
    class_id = request.form.get("class_id")
    passenger_name = request.form.get("passenger_name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    berth_pref = request.form.get("berth_pref") or None

    # Generate PNR like PNRxxx
    pnr = "PNR" + uuid.uuid4().hex[:6].upper()

    # Call stored procedure book_ticket with OUT param via workaround (use IN OUT through SELECT)
    # Our procedure signature ends with OUT p_result; we need to read it. We'll call using cursor.callproc.
    conn = get_db()
    try:
        cur = conn.cursor()
        # Prepare OUT parameter as placeholder; mysql-connector requires supplying initial value
        args = (pnr, train_no, user_id, source, destination, date, class_id, "")
        cur.callproc("book_ticket", args)
        # Fetch OUT value from cur.stored_results() or parameters
        result_msg = None
        for res in cur.stored_results():
            # not used here; procedure doesn't SELECT
            pass
        # After callproc, connector updates args in cur (not directly accessible), so we refetch ticket existence
        # Check if ticket was created
        cur2 = conn.cursor()
        cur2.execute("SELECT pnr_no FROM ticket WHERE pnr_no=%s", (pnr,))
        created = cur2.fetchone()
        cur2.close()
        if created:
            # Insert passenger row
            passenger_id = "P" + uuid.uuid4().hex[:6].upper()
            cur.execute("INSERT INTO passenger (passenger_id, pnr_no, passenger_name, age, gender, berth_pref) VALUES (%s,%s,%s,%s,%s,%s)",
                        (passenger_id, pnr, passenger_name, age, gender, berth_pref))
            conn.commit()
            flash(f"Ticket booked! PNR: {pnr}", "success")
        else:
            flash("Booking failed (possibly no seats).", "error")
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Booking error: {e}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("my_tickets"))

@app.route("/tickets")
@login_required(role="passenger")
def my_tickets():
    uid = session.get("user_id")
    rows = query("""
        SELECT t.pnr_no, t.train_no, tr.train_name, t.source_station, t.destination_station,
               t.travel_date, t.total_fare, t.status
        FROM ticket t JOIN train tr ON t.train_no=tr.train_no
        WHERE t.user_id=%s ORDER BY t.booking_time DESC
    """, (uid,))
    return render_template("my_tickets.html", title="My Tickets", tickets=rows)

@app.route("/cancel", methods=["POST"])
@login_required(role="passenger")
def cancel_ticket():
    pnr = request.form.get("pnr_no")
    reason = request.form.get("reason") or "No reason"
    cancel_id = "CN" + uuid.uuid4().hex[:6].upper()

    conn = get_db()
    try:
        cur = conn.cursor()
        # call cancel_ticket(p_pnr, p_cancel_id, p_reason, OUT p_message)
        args = (pnr, cancel_id, reason, "")
        cur.callproc("cancel_ticket", args)
        conn.commit()
        flash(f"Cancellation requested for {pnr}.", "success")
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Cancel error: {e}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("my_tickets"))

# --------------- Admin -------------------
@app.route("/admin")
@login_required(role="admin")
def admin():
    return render_template("admin_dashboard.html", title="Admin")

@app.route("/admin/users")
@login_required(role="admin")
def admin_users():
    users = query("SELECT user_id, name, email, role FROM user ORDER BY name")
    return render_template("admin_users.html", title="Manage Users", users=users)

@app.route("/admin/add-user", methods=["GET", "POST"])
@login_required(role="admin")
def admin_add_user():
    if request.method == "POST":
        f = request.form
        try:
            execute(
                "INSERT INTO user (user_id, name, email, password, dob, gender, city, state, pin_code, role) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    f.get("user_id"), f.get("name"), f.get("email"), f.get("password"),
                    f.get("dob") or None, f.get("gender") or None,
                    f.get("city"), f.get("state"), f.get("pin_code"), f.get("role", "passenger")
                )
            )
            if f.get("mobile"):
                execute("INSERT INTO user_mobile (user_id, mobile_no) VALUES (%s,%s)", (f.get("user_id"), f.get("mobile")))
            flash("User created successfully.", "success")
            return redirect(url_for("admin_users"))
        except mysql.connector.Error as e:
            flash(f"Error creating user: {e}", "error")
    return render_template("admin_add_user.html", title="Add User")

@app.route("/admin/delete-user/<user_id>")
@login_required(role="admin")
def admin_delete_user(user_id):
    try:
        execute("DELETE FROM user WHERE user_id = %s", (user_id,))
        flash("User deleted successfully.", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting user: {e}", "error")
    return redirect(url_for("admin_users"))

@app.route("/admin/trains")
@login_required(role="admin")
def admin_trains():
    trains = query("SELECT * FROM train ORDER BY train_no")
    return render_template("admin_trains.html", title="All Trains", trains=trains)

@app.route("/admin/add-train", methods=["GET", "POST"])
@login_required(role="admin")
def admin_add_train():
    if request.method == "POST":
        f = request.form
        try:
            execute("INSERT INTO train (train_no, train_name, type, base_fare_multiplier, route_id) VALUES (%s,%s,%s,%s,%s)",
                    (f["train_no"], f["train_name"], f["type"], f["base_fare_multiplier"], f["route_id"]))
            execute("INSERT INTO schedule (schedule_id, train_no, start_time, end_time, running_days) VALUES (%s,%s,%s,%s,%s)",
                    (f["schedule_id"], f["train_no"], f["start_time"], f["end_time"], f.get("running_days")))
            if f.get("class_id"):
                execute("INSERT INTO class (class_id, class_name, coach_type, no_of_coaches, c_multiplier, train_no) VALUES (%s,%s,%s,%s,%s,%s)",
                        (f["class_id"], f.get("class_name"), f.get("coach_type") or None,
                         f.get("no_of_coaches") or 1, f.get("c_multiplier") or 1.0, f["train_no"]))
            flash("Train created.", "success")
            return redirect(url_for("admin_trains"))
        except mysql.connector.Error as e:
            flash(f"Error adding train: {e}", "error")
    return render_template("admin_add_train.html", title="Add Train")

@app.route("/admin/edit-train/<train_no>", methods=["GET", "POST"])
@login_required(role="admin")
def admin_edit_train(train_no):
    if request.method == "POST":
        f = request.form
        try:
            # Update train table
            execute("UPDATE train SET train_name=%s, type=%s, base_fare_multiplier=%s, route_id=%s WHERE train_no=%s",
                    (f["train_name"], f["type"], f["base_fare_multiplier"], f["route_id"], train_no))
            
            # Update or insert schedule
            schedule_exists = query("SELECT COUNT(*) as count FROM schedule WHERE train_no=%s", (train_no,))[0]['count']
            if schedule_exists > 0:
                execute("UPDATE schedule SET start_time=%s, end_time=%s, running_days=%s WHERE train_no=%s",
                        (f["start_time"], f["end_time"], f.get("running_days"), train_no))
            else:
                execute("INSERT INTO schedule (schedule_id, train_no, start_time, end_time, running_days) VALUES (%s,%s,%s,%s,%s)",
                        (f["schedule_id"], train_no, f["start_time"], f["end_time"], f.get("running_days")))
            
            # Handle class update/insert
            if f.get("class_id"):
                class_exists = query("SELECT COUNT(*) as count FROM class WHERE train_no=%s", (train_no,))[0]['count']
                if class_exists > 0:
                    execute("UPDATE class SET class_name=%s, coach_type=%s, no_of_coaches=%s, c_multiplier=%s WHERE train_no=%s",
                            (f.get("class_name"), f.get("coach_type") or None, f.get("no_of_coaches") or 1, f.get("c_multiplier") or 1.0, train_no))
                else:
                    execute("INSERT INTO class (class_id, class_name, coach_type, no_of_coaches, c_multiplier, train_no) VALUES (%s,%s,%s,%s,%s,%s)",
                            (f["class_id"], f.get("class_name"), f.get("coach_type") or None, f.get("no_of_coaches") or 1, f.get("c_multiplier") or 1.0, train_no))
            
            flash("Train updated successfully.", "success")
            return redirect(url_for("admin_trains"))
        except mysql.connector.Error as e:
            flash(f"Error updating train: {e}", "error")
    
    # GET request - fetch existing data
    train = query("SELECT * FROM train WHERE train_no=%s", (train_no,), fetch="one")
    if not train:
        flash("Train not found.", "error")
        return redirect(url_for("admin_trains"))
    
    schedule = query("SELECT * FROM schedule WHERE train_no=%s", (train_no,), fetch="one")
    train_class = query("SELECT * FROM class WHERE train_no=%s", (train_no,), fetch="one")
    
    # Convert timedelta objects to time objects if necessary
    if schedule:
        from datetime import time, timedelta
        if isinstance(schedule['start_time'], timedelta):
            total_seconds = int(schedule['start_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            schedule['start_time'] = time(hours, minutes)
        if isinstance(schedule['end_time'], timedelta):
            total_seconds = int(schedule['end_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            schedule['end_time'] = time(hours, minutes)
    
    return render_template("admin_edit_train.html", title="Edit Train", 
                         train=train, schedule=schedule, train_class=train_class)

@app.route("/admin/delete-train/<train_no>")
@login_required(role="admin")
def admin_delete_train(train_no):
    try:
        # Delete related records first (in order of dependencies)
        execute("DELETE FROM connected WHERE train_no = %s", (train_no,))
        execute("DELETE FROM train_status WHERE train_no = %s", (train_no,))
        
        # Get all PNR numbers for this train's tickets
        tickets = query("SELECT pnr_no FROM ticket WHERE train_no = %s", (train_no,))
        for ticket in tickets:
            pnr_no = ticket['pnr_no']
            # Delete payment and cancellation records for each ticket
            execute("DELETE FROM payment WHERE pnr_no = %s", (pnr_no,))
            execute("DELETE FROM cancellation WHERE pnr_no = %s", (pnr_no,))
        
        # Now delete tickets (passenger table has ON DELETE CASCADE)
        execute("DELETE FROM ticket WHERE train_no = %s", (train_no,))
        execute("DELETE FROM seat_availability WHERE train_no = %s", (train_no,))
        execute("DELETE FROM class WHERE train_no = %s", (train_no,))
        # schedule table has ON DELETE CASCADE, so it will be deleted automatically
        execute("DELETE FROM train WHERE train_no = %s", (train_no,))
        flash("Train deleted successfully.", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting train: {e}", "error")
    return redirect(url_for("admin_trains"))

@app.route("/database-objects")
@login_required(role="admin")
def database_objects():
    return render_template("database_objects.html", title="Database Objects")

@app.route("/view-triggers")
@login_required(role="admin")
def view_triggers():
    # Get trigger definitions
    triggers = query("""
    SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, ACTION_TIMING, EVENT_MANIPULATION, ACTION_STATEMENT
    FROM information_schema.TRIGGERS 
    WHERE TRIGGER_SCHEMA = DATABASE()
    ORDER BY TRIGGER_NAME
    """)
    return render_template("view_triggers.html", title="Database Triggers", triggers=triggers)

@app.route("/view-procedures")
@login_required(role="admin")
def view_procedures():
    # Get procedure definitions
    procedures = query("""
    SELECT ROUTINE_NAME, ROUTINE_TYPE, ROUTINE_DEFINITION
    FROM information_schema.ROUTINES 
    WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE'
    ORDER BY ROUTINE_NAME
    """)
    return render_template("view_procedures.html", title="Stored Procedures", procedures=procedures)

@app.route("/view-functions")
@login_required(role="admin")
def view_functions():
    # Get function definitions
    functions = query("""
    SELECT ROUTINE_NAME, ROUTINE_TYPE, ROUTINE_DEFINITION
    FROM information_schema.ROUTINES 
    WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'FUNCTION'
    ORDER BY ROUTINE_NAME
    """)
    return render_template("view_functions.html", title="Database Functions", functions=functions)

# --------------- Queries -------------------
@app.route("/queries")
@login_required(role="admin")
def queries():
    return render_template("queries.html", title="Database Queries")

@app.route("/nested-query", methods=["GET", "POST"])
@login_required(role="admin")
def nested_query():
    results = None
    if request.method == "POST":
        # Nested Query: Find users who have booked tickets on trains that have available seats > 10
        sql = """
        SELECT DISTINCT u.name, u.email, t.train_no, tr.train_name
        FROM user u
        JOIN ticket t ON u.user_id = t.user_id
        JOIN train tr ON t.train_no = tr.train_no
        WHERE t.train_no IN (
            SELECT sa.train_no
            FROM seat_availability sa
            WHERE sa.available_seats > 10
        )
        ORDER BY u.name
        """
        results = query(sql)
    return render_template("nested_query.html", title="Nested Query", results=results)

@app.route("/join-query", methods=["GET", "POST"])
@login_required(role="admin")
def join_query():
    results = None
    if request.method == "POST":
        # Join Query: Show booking details with user and train info
        sql = """
        SELECT t.pnr_no, u.name, u.email, tr.train_name, t.source_station, t.destination_station, 
               t.travel_date, t.total_fare, t.status
        FROM ticket t
        JOIN user u ON t.user_id = u.user_id
        JOIN train tr ON t.train_no = tr.train_no
        ORDER BY t.booking_time DESC
        """
        results = query(sql)
    return render_template("join_query.html", title="Join Query", results=results)

@app.route("/aggregate-query", methods=["GET", "POST"])
@login_required(role="admin")
def aggregate_query():
    results = None
    if request.method == "POST":
        # Aggregate Query: Total bookings and revenue per train
        sql = """
        SELECT tr.train_name, COUNT(t.pnr_no) as total_bookings, 
               SUM(t.total_fare) as total_revenue
        FROM train tr
        LEFT JOIN ticket t ON tr.train_no = t.train_no AND t.status = 'booked'
        GROUP BY tr.train_no, tr.train_name
        ORDER BY total_bookings DESC
        """
        results = query(sql)
    return render_template("aggregate_query.html", title="Aggregate Query", results=results)

# --------------- Misc -------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", title="Not Found"), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
