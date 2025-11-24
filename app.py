from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from werkzeug.utils import secure_filename
import sqlite3, os, datetime
import pytz

def format_timestamp(ts):
    utc = datetime.datetime.fromisoformat(ts)
    denver = utc.replace(tzinfo=datetime.timezone.utc).astimezone(pytz.timezone("America/Denver"))
    return denver.strftime("%b %d, %Y — %I:%M %p")

=======
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB = 'jl.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def format_timestamp(ts):
    utc = datetime.datetime.fromisoformat(ts)
    denver = utc.replace(tzinfo=datetime.timezone.utc).astimezone(pytz.timezone("America/Denver"))
    return denver.strftime("%b %d, %Y — %I:%M %p")

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(open('init_schema.sql').read())
    conn.commit()
    conn.close()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'replace-with-a-random-secret-key'

AREAS = ['Upper Bay','Lower Bay','Lobby']
MANAGER_PASSWORD = "GriffinFL80601"

@app.route('/')
def index():
    return render_template('index.html', areas=AREAS)

@app.route('/form/<area>', methods=['GET','POST'])
def form(area):
    if area not in AREAS:
        return "Unknown area", 404

    conn = get_db()
    workers = [r['name'] for r in conn.execute("SELECT name FROM workers ORDER BY id").fetchall()]
    conn.close()

    default_checklists = {
        'Upper Bay': [
            'Take out all trash cans (put new bags in)',
            'Clean & put away tools',
            'Pick up dirty towels',
            'Restock empty oil BIBs & towels',
            'Fill window wash bucket',
            'Sweep & mop (empty mop buckets)'
        ],
        'Lower Bay': [
            'Take out all trash & used oil filter buckets',
            'Clean & put away tools',
            'Pick up dirty towels',
            'Restock empty filters & low towels',
            'Wipe down all oil tanks',
            'Sweep & mop (empty mop buckets)'
        ],
        'Lobby': [
            'Wipe down counters & chairs',
            'Restock cups & coffee',
            'Clean lobby windows & doors',
            'Restock invoice/printer paper',
            'Sweep & mop (empty mop water)'
        ]
    }

    if request.method == 'POST':
        worker = request.form.get('worker')
        checklist_text = request.form.get('checklist')
        note = request.form.get('notes')
        photo = request.files.get('photo')
        filename = None

        if photo and photo.filename:
            filename = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S_') + secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        ts = datetime.datetime.utcnow().isoformat()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
    "INSERT INTO submissions (area, worker, completed, photo, notes, timestamp, manager_initials) VALUES (?,?,?,?,?,?,?)",
    (area, worker, int('completed' in request.form), filename, note, ts, '')
)
        conn.commit()
        conn.close()
        flash('Submitted successfully!', 'success')
        return redirect(url_for('form', area=area))

    return render_template('form.html', area=area, workers=workers, checklist='\n'.join(['[ ] '+t for t in default_checklists[area]]))

def worker_initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get("manager_logged_in"):
        return redirect(url_for('manager_login'))

    conn = get_db()
    rows = conn.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 500").fetchall()
    conn.close()
    return render_template('dashboard.html', rows=rows, format_timestamp=format_timestamp)
   
@app.route('/manager-login', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        if request.form.get('password') == MANAGER_PASSWORD:
            session["manager_logged_in"] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect password", "danger")

    return render_template('manager_login.html')

@app.route('/approve/<int:submission_id>', methods=['POST'])
def approve(submission_id):
    mgr = request.form.get('manager_initials','').strip()
    if not mgr:
        flash('Manager initials required', 'danger')
        return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute("UPDATE submissions SET manager_initials=?, approved=1 WHERE id=?", (mgr, submission_id))
    conn.commit()
    conn.close()
    flash('Approved', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop("manager_logged_in", None)
    flash("Logged out", "info")
    return redirect(url_for('manager_login'))

if __name__ == '__main__':
    if not os.path.exists(DB):
        init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)

