#!/usr/bin/env python3
import  json
from datetime import datetime, timezone
from functools import wraps
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4  
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib import colors

import arabic_reshaper
from bidi.algorithm import get_display

def rtl(text):
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)      # إصلاح الأحرف
    bidi_text = get_display(reshaped)             # عكس اتجاه السطر
    return bidi_text


# app.py - كامل متكامل (Permissions: Admin/Manager/Engineer + per-site permissions)
import os
import io
from flask import (
    Flask, render_template, request, redirect, session, url_for,
    flash, send_from_directory, send_file, jsonify
)
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# reportlab for PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'replace_this_secret')

# folders
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
PDF_FOLDER = os.path.join(BASE_DIR, 'static', 'pdf')
os.makedirs(PDF_FOLDER, exist_ok=True)

# DB config from .env or defaults
import os
import mysql.connector

def get_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        autocommit=True
    )
    return conn

# inject commonly used template variables
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'session': session
    }

# Audit log helper
def log_audit(user_id, action, object_type='', object_id='', details=''):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO audit_log (user_id, action, object_type, object_id, details) VALUES (%s,%s,%s,%s,%s)',
                    (user_id, action, object_type, str(object_id), details))
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

# ---------------------------
# Authentication & helpers
# ---------------------------
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def get_user_role_name(user_id):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("SELECT r.role_name FROM roles r JOIN users u ON u.role_id=r.role_id WHERE u.user_id=%s", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close(); conn.close()

def is_admin(user_id):
    rn = get_user_role_name(user_id)
    return rn and rn.lower() == 'admin'

def is_manager(user_id):
    rn = get_user_role_name(user_id)
    return rn and rn.lower() == 'manager'

def is_contractor_manager(user_id):
    rn = get_user_role_name(user_id)
    return rn and rn.lower() == 'contractor manager'

def user_has_site(user_id, site_id):
    """Return True if user assigned to site (or admin)."""
    if is_admin(user_id):
        return True
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM user_sites WHERE user_id=%s AND site_id=%s", (user_id, site_id))
        return cur.fetchone() is not None
    finally:
        cur.close(); conn.close()

def can_user_action(user_id, site_id, action):
    """
    action in ('can_view','can_add','can_edit','can_delete')
    Admin bypasses.
    """
    if is_admin(user_id):
        return True
    if action not in ('can_view','can_add','can_edit','can_delete'):
        return False
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(f"SELECT {action} FROM report_permissions WHERE user_id=%s AND site_id=%s", (user_id, site_id))
        r = cur.fetchone()
        return bool(r and r[0] == 1)
    finally:
        cur.close(); conn.close()

def permission_required(action):
    """
    Decorator to ensure current user has 'action' permission for target site.
    The site_id is resolved from kwargs, form data, or query params.
    If no site_id present, only admin allowed.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            uid = session.get('user_id')
            if not uid:
                return redirect(url_for('login'))
            # try resolve site_id
            site_id = None
            if 'site_id' in kwargs:
                site_id = kwargs['site_id']
            if not site_id:
                site_id = request.form.get('site_id') or request.args.get('site_id')
            if site_id is None:
                if not is_admin(uid):
                    flash('مطلوب تحديد الموقع للقيام بهذا الإجراء', 'warning')
                    return redirect(url_for('dashboard'))
                return f(*args, **kwargs)
            try:
                site_id = int(site_id)
            except Exception:
                flash('site_id غير صالح', 'danger')
                return redirect(url_for('dashboard'))
            if not user_has_site(uid, site_id):
                flash('لا تملك صلاحية الوصول لهذا الموقع', 'danger')
                return redirect(url_for('dashboard'))
            if not can_user_action(uid, site_id, action):
                flash('لا تملك صلاحية تنفيذ هذا الإجراء على هذا الموقع', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

### Brute force protection helpers##############
from datetime import datetime, timedelta

def register_failed_attempt(ip):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT attempts, last_attempt FROM failed_attempts WHERE ip=%s", (ip,))
    row = cur.fetchone()

    if row:
        attempts, last = row
        # reset after 15 min
        if datetime.now() - last > timedelta(minutes=15):
            cur.execute("UPDATE failed_attempts SET attempts=1, last_attempt=NOW() WHERE ip=%s", (ip,))
        else:
            cur.execute("UPDATE failed_attempts SET attempts=attempts+1, last_attempt=NOW() WHERE ip=%s", (ip,))
    else:
        cur.execute("INSERT INTO failed_attempts (ip, attempts) VALUES (%s,1)", (ip,))

    conn.commit()
    cur.close()
    conn.close()

def is_blocked_ip(ip):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT attempts, last_attempt FROM failed_attempts WHERE ip=%s", (ip,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return False

    attempts, last = row

    # block if > 5 attempts within 10 minutes
    if attempts >= 5 and datetime.now() - last < timedelta(minutes=10):
        return True

    return False
###############################################

# ---------------------------
# Auth routes
# ---------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        ip = request.remote_addr
        agent = request.headers.get('User-Agent')

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        # check brute force (added below)
        if is_blocked_ip(ip):
            return render_template("login.html",
                error="تم حظر هذا الجهاز مؤقتًا بسبب محاولات عديدة")

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], password):
            # log success
            cur2 = conn.cursor()
            cur2.execute("""
                INSERT INTO login_logs (user_id, username, status, ip_address, user_agent)
                VALUES (%s,%s,'success',%s,%s)
            """, (user['user_id'], username, ip, agent))
            conn.commit()
            cur2.close()

            # login user
            session.update({
                'user_id': user['user_id'],
                'username': user['username'],
                'fullname': user['fullname'],
                'role_id': user['role_id']
            })
            cur.close()
            conn.close()
            return redirect(url_for('dashboard'))

        else:
            # log failed
            cur2 = conn.cursor()
            cur2.execute("""
                INSERT INTO login_logs (username,status,ip_address,user_agent)
                VALUES (%s,'failed',%s,%s)
            """, (username, ip, agent))
            conn.commit()
            cur2.close()

            register_failed_attempt(ip)

            cur.close()
            conn.close()
            return render_template("login.html", error="خطأ في اسم المستخدم أو كلمة المرور")

    return render_template("login.html")


@app.route('/logout')
def logout():
    uid = session.get('user_id')
    session.clear()
    if uid:
        log_audit(uid, 'logout', 'user', uid, 'User logged out')
    return redirect(url_for('login'))

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/')
@login_required
def dashboard():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT COUNT(*) AS c FROM sites'); sites_count = cur.fetchone()['c']
        cur.execute('SELECT COUNT(*) AS c FROM contractors'); contractors_count = cur.fetchone()['c']
        cur.execute('SELECT COUNT(*) AS c FROM reports'); reports_count = cur.fetchone()['c']
        cur.execute('SELECT COUNT(*) AS c FROM users'); users_count = cur.fetchone()['c']
        # latest reports (admin sees all; others see those they can view)
        uid = session.get('user_id')
        if is_admin(uid):
            cur.execute('SELECT r.report_id, r.title, r.date_created, s.site_name, u.fullname FROM reports r JOIN sites s ON r.site_id=s.site_id LEFT JOIN users u ON r.engineer_id=u.user_id ORDER BY r.report_id DESC LIMIT 10')
            latest_reports = cur.fetchall()
        else:
            # join with report_permissions or user_sites
            cur.execute("""
                SELECT r.report_id, r.title, r.date_created, s.site_name, u.fullname
                FROM reports r
                JOIN sites s ON r.site_id=s.site_id
                LEFT JOIN users u ON r.engineer_id=u.user_id
                WHERE r.site_id IN (SELECT site_id FROM user_sites WHERE user_id=%s)
                ORDER BY r.report_id DESC LIMIT 10
            """, (uid,))
            latest_reports = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('dashboard.html',
                           sites_count=sites_count, contractors_count=contractors_count,
                           reports_count=reports_count, users_count=users_count,
                           latest_reports=latest_reports)





# ---------------------------
# Users CRUD (Admin only for create/delete; view allowed to managers+admins)
# ---------------------------
@app.route('/users')
@login_required
def users():
    uid = session.get('user_id')
    if not (is_admin(uid) or is_manager(uid)):
        flash('غير مصرح', 'danger'); return redirect(url_for('dashboard'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT u.user_id AS id, u.username, u.fullname, r.role_name FROM users u LEFT JOIN roles r ON u.role_id=r.role_id')
        users = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET','POST'])
@login_required
def add_user():
    uid = session.get('user_id')
    if not is_admin(uid):
        flash('غير مصرح', 'danger'); return redirect(url_for('users'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            username = request.form['username'].strip()
            fullname = request.form.get('fullname')
            password_hash = generate_password_hash(request.form['password'])
            role_id = int(request.form.get('role_id')) if request.form.get('role_id') else None
            cur.execute('INSERT INTO users (username,password,fullname,role_id) VALUES (%s,%s,%s,%s)', (username, password_hash, fullname, role_id))
            conn.commit()
            new_id = cur.lastrowid
            log_audit(uid, 'create_user', 'user', new_id, f'Created user {username}')
            flash('تم الإضافة', 'success')
            return redirect(url_for('users'))
        cur.execute('SELECT role_id, role_name FROM roles')
        roles = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('user_form.html', roles=roles)

@app.route('/users/edit/<int:uid_to_edit>', methods=['GET','POST'])
@login_required
def edit_user(uid_to_edit):
    uid = session.get('user_id')
    if not (is_admin(uid) or uid == uid_to_edit):
        flash('غير مصرح', 'danger'); return redirect(url_for('users'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            fullname = request.form.get('fullname')
            role_id = int(request.form.get('role_id')) if request.form.get('role_id') else None
            cur.execute('UPDATE users SET fullname=%s, role_id=%s WHERE user_id=%s', (fullname, role_id, uid_to_edit))
            conn.commit()
            log_audit(uid, 'edit_user', 'user', uid_to_edit, f'Edited user {uid_to_edit}')
            flash('تم الحفظ', 'success')
            return redirect(url_for('users'))
        cur.execute('SELECT * FROM users WHERE user_id=%s', (uid_to_edit,))
        user = cur.fetchone()
        cur.execute('SELECT role_id, role_name FROM roles')
        roles = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('user_form.html', user=user, roles=roles)

@app.route('/users/delete/<int:uid_to_delete>')
@login_required
def delete_user(uid_to_delete):
    uid = session.get('user_id')
    if not is_admin(uid):
        flash('غير مصرح', 'danger'); return redirect(url_for('users'))
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute('DELETE FROM users WHERE user_id=%s', (uid_to_delete,))
        conn.commit()
        log_audit(uid, 'delete_user', 'user', uid_to_delete, 'Deleted user')
        flash('تم الحذف', 'success')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('users'))

# ---------------------------
# Roles
# ---------------------------
@app.route('/roles')
@login_required
def roles():
    if not is_admin(session.get('user_id')):
        flash('غير مصرح', 'danger'); return redirect(url_for('dashboard'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT * FROM roles')
        roles = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('roles.html', roles=roles)

@app.route('/roles/add', methods=['GET','POST'])
@login_required
def add_role():
    if not is_admin(session.get('user_id')):
        flash('غير مصرح', 'danger'); return redirect(url_for('roles'))
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute('INSERT INTO roles (role_name) VALUES (%s)', (request.form['role_name'],))
            conn.commit()
            flash('تم إضافة الدور', 'success')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('roles'))
    return render_template('role_form.html')

# ---------------------------
# Sites & Contractors
# ---------------------------
@app.route('/sites')
@login_required
def sites():
    # list sites (managers/admins can see all; engineers see assigned)
    uid = session.get('user_id')
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if is_admin(uid) or is_manager(uid):
            cur.execute('SELECT s.*, c.contractor_name FROM sites s LEFT JOIN contractors c ON s.contractor_id=c.contractor_id')
            sites = cur.fetchall()
        else:
            cur.execute('SELECT s.*, c.contractor_name FROM sites s LEFT JOIN contractors c ON s.contractor_id=c.contractor_id WHERE s.site_id IN (SELECT site_id FROM user_sites WHERE user_id=%s)', (uid,))
            sites = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('sites.html', sites=sites)

@app.route('/sites/add', methods=['GET','POST'])
@login_required
def add_site():
    if not (is_admin(session.get('user_id')) or is_manager(session.get('user_id')) or is_contractor_manager(session.get('user_id'))  ):
        flash('غير مصرح', 'danger'); return redirect(url_for('sites'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            cur.execute('INSERT INTO sites (site_code, site_name, address, latitude, longitude, contractor_id) VALUES (%s,%s,%s,%s,%s,%s)',
                        (request.form.get('site_code'), request.form.get('site_name'), request.form.get('address'), request.form.get('latitude'), request.form.get('longitude'), request.form.get('contractor_id') or None))
            conn.commit()
            flash('تم إضافة الموقع', 'success')
            return redirect(url_for('sites'))
        cur.execute('SELECT contractor_id, contractor_name FROM contractors')
        contractors = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('site_form.html', contractors=contractors)

@app.route('/sites/edit/<int:sid>', methods=['GET','POST'])
@login_required
def edit_site(sid):
    if not (is_admin(session.get('user_id')) or is_manager(session.get('user_id'))):
        flash('غير مصرح', 'danger'); return redirect(url_for('sites'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            cur.execute('UPDATE sites SET site_code=%s, site_name=%s, address=%s, latitude=%s, longitude=%s, contractor_id=%s WHERE site_id=%s',
                        (request.form.get('site_code'), request.form.get('site_name'), request.form.get('address'), request.form.get('latitude'), request.form.get('longitude'), request.form.get('contractor_id') or None, sid))
            conn.commit()
            flash('تم التحديث', 'success')
            return redirect(url_for('sites'))
        cur.execute('SELECT * FROM sites WHERE site_id=%s', (sid,))
        site = cur.fetchone()
        cur.execute('SELECT contractor_id, contractor_name FROM contractors')
        contractors = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('site_form.html', site=site, contractors=contractors)

@app.route('/sites/delete/<int:sid>')
@login_required
def delete_site(sid):
    if not is_admin(session.get('user_id')):
        flash('غير مصرح', 'danger'); return redirect(url_for('sites'))
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute('DELETE FROM sites WHERE site_id=%s', (sid,))
        conn.commit()
        flash('تم الحذف', 'success')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('sites'))

# Contractors
@app.route('/contractors')
@login_required
def contractors():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT * FROM contractors')
        items = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('contractors.html', contractors=items)

@app.route('/contractors/add', methods=['GET','POST'])
@login_required
def add_contractor():
    if not (is_admin(session.get('user_id')) or is_manager(session.get('user_id'))):
        flash('غير مصرح', 'danger'); return redirect(url_for('contractors'))
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute('INSERT INTO contractors (contractor_name, phone) VALUES (%s,%s)', (request.form.get('name'), request.form.get('phone')))
            conn.commit()
            flash('تم الإضافة', 'success')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('contractors'))
    return render_template('contractor_form.html')

# ---------------------------
# Reports (create/view/list)
# ---------------------------
@app.route('/reports')
@login_required
def reports():
    uid = session.get('user_id')
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if is_admin(uid):
            cur.execute('SELECT r.*, s.site_name, c.contractor_name, u.fullname FROM reports r JOIN sites s ON r.site_id=s.site_id LEFT JOIN contractors c ON c.contractor_id = r.contractor_id LEFT JOIN users u ON r.engineer_id=u.user_id ORDER BY r.report_id DESC')
            
            rows = cur.fetchall()
        else:
            # show reports for sites user assigned to OR created by user
            cur.execute("""
                SELECT r.*, s.site_name, u.fullname
                FROM reports r
                JOIN sites s ON r.site_id=s.site_id
                LEFT JOIN users u ON r.engineer_id=u.user_id
                WHERE r.site_id IN (SELECT site_id FROM user_sites WHERE user_id=%s)
                OR r.engineer_id=%s
                ORDER BY r.report_id DESC
            """, (uid, uid))
            rows = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('reports.html', reports=rows)

@app.route('/reports/add', methods=['GET','POST'])
@login_required
def add_report():
    uid = session.get('user_id')
    # require can_add on the chosen site
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            site_id = int(request.form.get('site_id'))
            if not can_user_action(uid, site_id, 'can_add'):
                flash('ليس لديك صلاحية إضافة تقرير لهذا الموقع', 'danger'); return redirect(url_for('reports'))
            title = request.form.get('title')
            description = request.form.get('description')
            contractor_id = request.form.get('contractor_id') or None
            gps_lat = request.form.get('gps_lat') or None
            gps_lon = request.form.get('gps_lon') or None
            cur.execute('INSERT INTO reports (site_id, contractor_id, engineer_id, title, description, gps_lat, gps_lon) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                        (site_id, contractor_id, uid, title, description, gps_lat, gps_lon))
            conn.commit()
            report_id = cur.lastrowid
            # workers saved from arrays
            names = request.form.getlist('worker_name[]')
            jobs = request.form.getlist('job_title[]')
            tasks = request.form.getlist('task_details[]')
            notes = request.form.getlist('notes[]')
            for n,j,t,nt in zip(names, jobs, tasks, notes):
                if n.strip():
                    cur.execute('INSERT INTO workers (report_id, worker_name, job_title, task_details, notes) VALUES (%s,%s,%s,%s,%s)',
                                (report_id, n, j, t, nt))
            # handle photos
            ##### Camera Upload Handling ###########
            #####
            files = request.files.getlist('photos')
            for f in files:
                if f and f.filename:
                    fname = f"report_{report_id}_{int(datetime.utcnow().timestamp())}_{secure_filename(f.filename)}"
                    path = os.path.join(UPLOAD_FOLDER, fname)
                    #f.save(path)
                    #cur.execute('INSERT INTO report_images (report_id, image_path) VALUES (%s,%s)', (report_id, fname))
                    # save file
                    # inside add_report POST, when saving a file
                    try:
                        f.save(path)
                        cur.execute('INSERT INTO report_images (report_id, image_path) VALUES (%s,%s)', (report_id, fname))
                    except Exception as e:
                        conn.rollback()
                        log_audit(session['user_id'], 'upload_error', 'report_image', report_id, str(e))
                        # for AJAX request return JSON:
                        if request.is_json or request.headers.get('X-Requested-With')=='XMLHttpRequest':
                            return jsonify({'error':'camera_upload_failed'}), 500
                        else:
                            return render_template('camera_error.html')

            conn.commit()
            log_audit(uid, 'create_report', 'report', report_id, f'Created on site {site_id}')
            flash('تم إنشاء التقرير', 'success')
            return redirect(url_for('reports'))
        # GET: load selection lists
        cur.execute('SELECT site_id, site_name FROM sites')
        sites = cur.fetchall()
        cur.execute('SELECT contractor_id, contractor_name FROM contractors')
        contractors = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('report_form.html', sites=sites, contractors=contractors)

# helper to secure file names
def secure_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ','.','_','-')).strip().replace(' ','_')

   

@app.route('/reports/view/<int:report_id>')
@login_required
def view_report(report_id):
    uid = session.get('user_id')
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT r.*, s.site_name, c.contractor_name, u.fullname AS engineer_name
            FROM reports r
            LEFT JOIN sites s ON s.site_id = r.site_id
            LEFT JOIN contractors c ON c.contractor_id = r.contractor_id
            LEFT JOIN users u ON u.user_id = r.engineer_id
            WHERE r.report_id=%s
        """, (report_id,))
        report = cur.fetchone()
        if not report:
            flash('التقرير غير موجود', 'danger'); return redirect(url_for('reports'))
        # permission: admin OR report owner OR can_view on site
        if not (is_admin(uid) or report.get('engineer_id')==uid or can_user_action(uid, report['site_id'], 'can_view')):
            flash('غير مصرح بمشاهدة هذا التقرير', 'danger'); return redirect(url_for('reports'))
        cur.execute('SELECT * FROM workers WHERE report_id=%s', (report_id,))
        workers = cur.fetchall()
        cur.execute('SELECT * FROM report_images WHERE report_id=%s', (report_id,))
        images = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('report_view.html', report=report, workers=workers, images=images)

# ---------------------------
# Export PDF (Report) - FULL PROFESSIONAL VERSION (with Timeline + Charts)
# ---------------------------
@app.route('/report/<int:report_id>/pdf')
@login_required
def export_pdf(report_id):

    # ===== Arabic Support =====
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import arabic_reshaper
    from bidi.algorithm import get_display

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Flowable
    )
    from reportlab.graphics.shapes import Drawing, Line, String, Circle
    from reportlab.graphics.barcode import qr
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    # charts
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    import os

    W, H = A4

    def rtl(text):
        if not text:
            return ""
        return get_display(arabic_reshaper.reshape(str(text)))

    # Fonts - register Arabic font (Amiri recommended)
    FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "Amiri-Regular.ttf")
    if os.path.exists(FONT_PATH):
        try:
            pdfmetrics.registerFont(TTFont("Arabic", FONT_PATH))
        except Exception:
            pass

    # Styles
    styles = getSampleStyleSheet()
    # fallback to Helvetica-based if Arabic not registered
    arabic_fontname = "Arabic" if "Arabic" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    styles.add(ParagraphStyle(name="AR_Title", fontName=arabic_fontname, alignment=2, fontSize=16, leading=20))
    styles.add(ParagraphStyle(name="AR_Header", fontName=arabic_fontname, alignment=2, fontSize=20, leading=24))
    styles.add(ParagraphStyle(name="AR_Normal", fontName=arabic_fontname, alignment=2, fontSize=12))

    # ========================================
    #   DATABASE
    # ========================================
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT r.*, s.site_name, c.contractor_name, u.fullname AS engineer_name
        FROM reports r
        LEFT JOIN sites s ON s.site_id=r.site_id
        LEFT JOIN contractors c ON c.contractor_id=r.contractor_id
        LEFT JOIN users u ON u.user_id=r.engineer_id
        WHERE report_id=%s
    """, (report_id,))
    report = cur.fetchone()

    cur.execute("SELECT * FROM workers WHERE report_id=%s", (report_id,))
    workers = cur.fetchall()

    cur.execute("SELECT * FROM report_images WHERE report_id=%s", (report_id,))
    images = cur.fetchall()

    cur.close()
    conn.close()

    # ========================================
    #   FILE PATHS
    # ========================================
    pdf_path = os.path.join(PDF_FOLDER, f"report_{report_id}.pdf")

    LOGO = os.path.join(BASE_DIR, "static", "logo.png")
    STAMP = os.path.join(BASE_DIR, "static", "stamp.png")      # ختم دائري شفاف
    SIGNATURE = os.path.join(BASE_DIR, "static", "sign.png")   # توقيع المهندس
    BG_IMAGE = os.path.join(BASE_DIR, "static", "bg.png")      # خلفية PDF
    WATERMARK = os.path.join(BASE_DIR, "static", "watermark.png")  # علامة مائية كبيرة

    # ========================================
    #   PAGE DECORATOR (background/stamp/footer)
    # ========================================
    def decorate_page(canv, doc):
        # background
        if os.path.exists(BG_IMAGE):
            try:
                canv.drawImage(BG_IMAGE, 0, 0, width=W, height=H, mask="auto")
            except Exception:
                pass

        # watermark
        if os.path.exists(WATERMARK):
            try:
                canv.saveState()
                canv.translate(W/2, H/2)
                canv.rotate(30)
                try:
                    canv.setFillAlpha(0.06)
                except Exception:
                    pass
                canv.drawImage(WATERMARK, -250, -250, width=500, height=500, mask="auto")
                canv.restoreState()
            except Exception:
                pass

        # stamp
        if os.path.exists(STAMP):
            try:
                canv.drawImage(STAMP, W - 5*cm, 1.5*cm, width=3.5*cm, height=3.5*cm, mask="auto")
            except Exception:
                pass

        # page number (use Arabic font if available)
        try:
            canv.setFont(arabic_fontname, 10)
        except Exception:
            canv.setFont("Helvetica", 10)
        # show arabic page label
        try:
            # show as "صفحة X"
            page_label = rtl(f"صفحة {doc.page}")
            canv.drawRightString(W - 1*cm, 1*cm, page_label)
        except Exception:
            canv.drawRightString(W - 1*cm, 1*cm, f"Page {doc.page}")

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,
        bottomMargin=60
    )

    story = []

    # ========= LOGO + HEADER ==========
    if os.path.exists(LOGO):
        try:
            story.append(Image(LOGO, width=130, height=55))
        except Exception:
            pass

    story.append(Paragraph(rtl("نظام التقارير الهندسية – تقرير رسمي"), styles["AR_Header"]))
    story.append(Spacer(1, 12))

    # ========= TITLE ==========
    title_text = report.get('title') if report else ''
    story.append(Paragraph(rtl(f"تقرير رقم {report_id} — {title_text}"), styles["AR_Title"]))
    story.append(Spacer(1, 10))

    # ========= INFO TABLE ==========
    info = [
        [rtl("الموقع"), rtl(report.get('site_name') if report else '')],
        [rtl("المقاول"), rtl(report.get('contractor_name') or "—")],
        [rtl("المهندس"), rtl(report.get('engineer_name') or "")],
        [rtl("التاريخ"), rtl(str(report.get('date_created')) if report else "")],
    ]
    info = [r[::-1] for r in info]

    info_table = Table(info, colWidths=[350, 120])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d2e3fc")),
        ("FONTNAME", (0,0), (-1,-1), arabic_fontname),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # ========= WORKERS ==========
    story.append(Paragraph(rtl("العمالة"), styles["AR_Title"]))

    worker_data = [[rtl("الاسم"), rtl("الوظيفة"), rtl("المهمة"), rtl("ملاحظات")]]
    for w in workers:
        worker_data.append([rtl(w.get('worker_name')), rtl(w.get('job_title')), rtl(w.get('task_details')), rtl(w.get('notes'))])
    worker_data = [row[::-1] for row in worker_data]

    w_table = Table(worker_data, colWidths=[100, 100, 180, 120])
    w_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#b0d4ff")),
        ("FONTNAME", (0,0), (-1,-1), arabic_fontname),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "RIGHT"),
    ]))
    story.append(w_table)
    story.append(Spacer(1, 20))

    # ========= Timeline (simple vertical timeline) ==========
    def build_timeline_drawing(events, width=400, start_y=160):
        d = Drawing(width, 200)
        y = start_y
        circle_x = 30
        line_bottom = 10
        for i, (tlabel, label) in enumerate(events):
            # circle
            d.add(Circle(circle_x, y, 5, fillColor=colors.HexColor("#0d6efd"), strokeColor=colors.HexColor("#0d6efd")))
            # label (to the right)
            s = String(circle_x + 15, y - 4, rtl(f"{tlabel} — {label}"), fontName=arabic_fontname, fontSize=10, fillColor=colors.black)
            # align right by shifting (approx)
            d.add(s)
            # vertical line
            if i < len(events) - 1:
                d.add(Line(circle_x, y - 6, circle_x, y - 40, strokeColor=colors.grey))
            y -= 40
        return d

    timeline_events = []
    if report:
        timeline_events.append((str(report.get('date_created')), "إنشاء التقرير"))
    for w in workers:
        timeline_events.append(("—", f"إضافة عامل: {w.get('worker_name')}"))
    if images:
        timeline_events.append(("—", "تم رفع صور التقرير"))

    if timeline_events:
        story.append(Paragraph(rtl("المخطط الزمني للتقرير"), styles['AR_Title']))
        story.append(Spacer(1, 6))
        tdraw = build_timeline_drawing(timeline_events, width=420)
        story.append(tdraw)
        story.append(Spacer(1, 12))

    # ========= Description ==========
    story.append(Paragraph(rtl("الوصف"), styles["AR_Title"]))
    story.append(Paragraph(rtl(report.get("description") or ""), styles["AR_Normal"]))
    story.append(Spacer(1, 20))

    # ========= Images ==========
    if images:
        story.append(Paragraph(rtl("صور التقرير"), styles["AR_Title"]))
        story.append(Spacer(1, 10))
        for img in images:
            path = os.path.join(UPLOAD_FOLDER, img.get("image_path", ""))
            if os.path.exists(path):
                try:
                    story.append(Image(path, width=400, height=250))
                    story.append(Spacer(1, 8))
                except Exception:
                    pass

    # ========= Charts ==========
    # Pie chart: distribution by job_title
    job_count = {}
    for w in workers:
        job = w.get('job_title') or "غير محدد"
        job_count[job] = job_count.get(job, 0) + 1

    if job_count:
        story.append(Paragraph(rtl("توزيع العمالة حسب الوظيفة"), styles['AR_Title']))
        chart_draw = Drawing(420, 200)
        pie = Pie()
        pie.x = 160
        pie.y = 10
        pie.width = 120
        pie.height = 120
        pie.data = list(job_count.values())
        pie.labels = [rtl(k) for k in job_count.keys()]
        # choose slice colors
        pie.slices.strokeWidth = 0.5
        chart_draw.add(pie)

        # legend
        legend = Legend()
        legend.x = 10
        legend.y = 140
        legend.fontName = arabic_fontname
        legend.colorNamePairs = []
        # create simple color pairs for legend (matching pie slices)
        colors_palette = [colors.HexColor(c) for c in ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#6610f2", "#0dcaf0"]]
        for i, lbl in enumerate(pie.labels):
            col = colors_palette[i % len(colors_palette)]
            # mimic slices color assignment (reportlab assigns by slice index)
            pie.slices[i].fillColor = col
            legend.colorNamePairs.append((col, lbl))
        chart_draw.add(legend)

        story.append(chart_draw)
        story.append(Spacer(1, 12))

    # Bar chart: count per task (task_details)
    task_count = {}
    for w in workers:
        t = w.get('task_details') or "غير محدد"
        task_count[t] = task_count.get(t, 0) + 1

    if task_count:
        story.append(Paragraph(rtl("عدد العمال لكل مهمة"), styles['AR_Title']))
        bar_draw = Drawing(420, 220)
        bar = VerticalBarChart()
        bar.x = 40
        bar.y = 30
        bar.height = 140
        bar.width = 330
        bar.data = [list(task_count.values())]
        # category names
        bar.categoryAxis.categoryNames = [rtl(k) for k in task_count.keys()]
        # style axis labels to use Arabic font if possible
        try:
            bar.categoryAxis.labels.boxAnchor = 'end'
            bar.categoryAxis.labels.angle = 45
            bar.categoryAxis.labels.fontName = arabic_fontname
            bar.categoryAxis.labels.fontSize = 8
        except Exception:
            pass
        bar.groupSpacing = 10
        bar.barSpacing = 2
        bar_draw.add(bar)
        story.append(bar_draw)
        story.append(Spacer(1, 12))

    # ========= Signature ==========
    if os.path.exists(SIGNATURE):
        story.append(Spacer(1, 10))
        story.append(Paragraph(rtl("توقيع المهندس"), styles["AR_Title"]))
        try:
            story.append(Image(SIGNATURE, width=180, height=80, mask="auto"))
        except Exception:
            pass
        story.append(Spacer(1, 12))

    # ========= QR ==========
    story.append(Paragraph(rtl("التحقق من التقرير"), styles["AR_Title"]))
    qr_code = qr.QrCodeWidget(f"Report {report_id}")
    d = Drawing(120, 120)
    d.add(qr_code)
    story.append(d)
    story.append(Spacer(1, 12))

    # ========= Footer ==========
    story.append(Paragraph(rtl("تم إنشاء التقرير بواسطة النظام — جميع الحقوق محفوظة © 2025"), styles["AR_Normal"]))

    # Save PDF with decorations (decorate_page draws background, watermark, stamp, footer page number)
    doc.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)

    return send_file(pdf_path, as_attachment=True)





# ---------------------------
# Admin: assign per-user per-site permissions
# ---------------------------
@app.route('/admin/user_permissions', methods=['GET','POST'])
@login_required
def admin_user_permissions():
    uid = session.get('user_id')
    # admins or managers (managers limited to their sites)
    if not (is_admin(uid) or is_manager(uid)):
        flash('غير مصرح', 'danger'); return redirect(url_for('dashboard'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT user_id, username, fullname FROM users')
        users = cur.fetchall()
        cur.execute('SELECT site_id, site_name FROM sites')
        sites = cur.fetchall()

        if request.method == 'POST':
            target_user = int(request.form.get('target_user'))
            site_id = int(request.form.get('site_id'))
            # managers may only manage sites they have
            if is_manager(uid) and not user_has_site(uid, site_id):
                flash('ليس لديك صلاحية لتعديل هذا الموقع', 'danger'); return redirect(url_for('admin_user_permissions'))
            allow_site = request.form.get('allow_site') == 'on'
            if allow_site:
                cur.execute('REPLACE INTO user_sites (user_id, site_id) VALUES (%s,%s)', (target_user, site_id))
            else:
                cur.execute('DELETE FROM user_sites WHERE user_id=%s AND site_id=%s', (target_user, site_id))
            can_view = 1 if request.form.get('can_view')=='on' else 0
            can_add  = 1 if request.form.get('can_add')=='on' else 0
            can_edit = 1 if request.form.get('can_edit')=='on' else 0
            can_delete= 1 if request.form.get('can_delete')=='on' else 0
            cur.execute('REPLACE INTO report_permissions (user_id, site_id, can_view, can_add, can_edit, can_delete) VALUES (%s,%s,%s,%s,%s,%s)',
                        (target_user, site_id, can_view, can_add, can_edit, can_delete))
            conn.commit()
            log_audit(uid, 'assign_permissions', 'user', target_user, f'site:{site_id} perms:{can_view}{can_add}{can_edit}{can_delete}')
            flash('تم التحديث', 'success')
            return redirect(url_for('admin_user_permissions'))

        selected_user = request.args.get('user_id', type=int)
        perms = []
        if selected_user:
            cur.execute('SELECT * FROM report_permissions WHERE user_id=%s', (selected_user,))
            perms = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template('admin_user_permissions.html', users=users, sites=sites, perms=perms, selected_user=selected_user)

# ---------------------------
# Reports search (filter by site, contractor, engineer, date range)
# ---------------------------
@app.route('/reports/search', methods=['GET','POST'])
@login_required
def reports_search():
    uid = session.get('user_id')
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute('SELECT site_id, site_name FROM sites'); sites = cur.fetchall()
        cur.execute('SELECT contractor_id, contractor_name FROM contractors'); contractors = cur.fetchall()
        cur.execute('SELECT user_id, fullname FROM users'); engineers = cur.fetchall()

        query = """SELECT r.*, s.site_name, c.contractor_name, u.fullname AS engineer_name
                   FROM reports r
                   LEFT JOIN sites s ON s.site_id = r.site_id
                   LEFT JOIN contractors c ON c.contractor_id = r.contractor_id
                   LEFT JOIN users u ON u.user_id = r.engineer_id
                   WHERE 1=1"""
        params = []
        if request.method == 'POST':
            if request.form.get('site_id'):
                query += " AND r.site_id=%s"; params.append(request.form['site_id'])
            if request.form.get('contractor_id'):
                query += " AND r.contractor_id=%s"; params.append(request.form['contractor_id'])
            if request.form.get('engineer_id'):
                query += " AND r.engineer_id=%s"; params.append(request.form['engineer_id'])
            if request.form.get('date_from'):
                query += " AND DATE(r.date_created) >= %s"; params.append(request.form['date_from'])
            if request.form.get('date_to'):
                query += " AND DATE(r.date_created) <= %s"; params.append(request.form['date_to'])
        query += " ORDER BY r.report_id DESC"
        cur.execute(query, params)
        results = cur.fetchall()
    finally:
        cur.close(); conn.close()
    # Filter results client-side for users who shouldn't see certain sites (non-admin)
    if not is_admin(uid):
        results = [r for r in results if (r['site_id'] in [s['site_id'] for s in sites if True and True]) and (r['site_id'] in [ss['site_id'] for ss in get_user_sites(uid)]) or r['engineer_id']==uid] if False else results
        # Simpler approach: let template handle hiding; or we can filter by user_sites.
        # For performance in large installs, move this filter into SQL using JOIN on user_sites.
    return render_template('reports_search.html', reports=results, sites=sites, contractors=contractors, engineers=engineers)

def get_user_sites(user_id):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute('SELECT site_id FROM user_sites WHERE user_id=%s', (user_id,))
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close(); conn.close()

# ---------------------------
# Serve uploaded files
# ---------------------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------------------
# API for GPS logs (simple)
# ---------------------------
@app.route('/api/gps_logs', methods=['POST'])
@login_required
def api_gps_logs():
    data = request.get_json() or {}
    report_id = data.get('report_id'); user_id = data.get('user_id'); lat = data.get('lat'); lon = data.get('lon')
    if not all([report_id, user_id, lat, lon]):
        return jsonify({'error':'missing'}), 400
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute('INSERT INTO gps_logs (report_id, user_id, lat, lon) VALUES (%s,%s,%s,%s)', (report_id, user_id, lat, lon))
        conn.commit()
    finally:
        cur.close(); conn.close()
    return jsonify({'ok': True}), 201


################################
############################

# -------------------------------
# Notifications backend (Flask)
# -------------------------------
from flask import g

def create_notification(db_conn, title, body=None, url=None, actor_id=None, target_user_ids=None):
    """
    Creates notification record and maps to user(s).
    target_user_ids: list of user_id or None meaning broadcast to all users.
    """
    cur = db_conn.cursor()
    cur.execute("INSERT INTO notifications (title, body, url, actor_id) VALUES (%s,%s,%s,%s)",
                (title, body, url, actor_id))
    nid = cur.lastrowid

    if target_user_ids is None:
        # broadcast: create entries for all users
        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()
        rows = [(nid, u[0]) for u in users]
    else:
        rows = [(nid, uid) for uid in target_user_ids]

    if rows:
        cur.executemany("INSERT INTO notification_users (notification_id, user_id) VALUES (%s,%s)", rows)

    db_conn.commit()
    cur.close()
    return nid

# helper: get unread count
def get_unread_count(user_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notification_users WHERE user_id=%s AND is_read=0", (user_id,))
    cnt = cur.fetchone()[0]
    cur.close(); conn.close()
    return cnt

# API: list newest notifications for current user
@app.route('/api/notifications/list')
@login_required
def api_notifications_list():
    uid = session['user_id']
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT n.notification_id, n.title, n.body, n.url, n.actor_id, n.created_at, nu.is_read
        FROM notification_users nu
        JOIN notifications n ON n.notification_id = nu.notification_id
        WHERE nu.user_id=%s
        ORDER BY n.created_at DESC
        LIMIT 50
    """, (uid,))
    notifs = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(notifs)

# API: unread count
@app.route('/api/notifications/unread_count')
@login_required
def api_notifications_unread_count():
    uid = session['user_id']
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notification_users WHERE user_id=%s AND is_read=0", (uid,))
    cnt = cur.fetchone()[0]
    cur.close(); conn.close()
    return jsonify({'unread': cnt})

# API: mark one as read
@app.route('/api/notifications/mark_read', methods=['POST'])
@login_required
def api_notifications_mark_read():
    data = request.get_json() or {}
    nid = data.get('notification_id')
    uid = session['user_id']
    if not nid:
        return jsonify({'error': 'missing notification_id'}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE notification_users SET is_read=1 WHERE notification_id=%s AND user_id=%s", (nid, uid))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True})

# API: mark all read
@app.route('/api/notifications/mark_all_read', methods=['POST'])
@login_required
def api_notifications_mark_all_read():
    uid = session['user_id']
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE notification_users SET is_read=1 WHERE user_id=%s AND is_read=0", (uid,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True})

# API: create notification (admin only)
@app.route('/admin/notifications/create', methods=['POST'])
@login_required
def admin_create_notification():
    if not is_admin(session['user_id']):
        return jsonify({'error':'forbidden'}), 403
    data = request.form or request.get_json() or {}
    title = data.get('title')
    body = data.get('body')
    url  = data.get('url')
    target = data.get('target')  # 'all' or comma-separated user ids
    conn = get_db()
    current_user_id = session['user_id']
    if target == 'all' or not target:
        create_notification(conn, title, body, url, actor_id=current_user_id, target_user_ids=None)
    else:
        ids = [int(x) for x in str(target).split(',') if x.strip().isdigit()]
        create_notification(conn, title, body, url, actor_id=current_user_id, target_user_ids=ids)
    conn.close()
    return redirect(url_for('admin_notifications'))


@app.route("/api/server_time")
def api_server_time():
    return jsonify({"server_time": datetime.now(timezone.utc).isoformat()})
#############################   

# ---------------------------
# Utilities & run
# ---------------------------

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

@app.errorhandler(503)
def maintenance(e):
    return render_template("503.html"), 503

@app.route("/offline")
def offline():
    return render_template("offline.html")

# --- imports ---
import csv, io
from flask import make_response

# --- helper: audit logging (reuse existing log_audit if present) ---
def log_audit(user_id, action, object_type='', object_id='', details=''):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute('INSERT INTO audit_log (user_id, action, object_type, object_id, details) VALUES (%s,%s,%s,%s,%s)',
                    (user_id, action, object_type, str(object_id), details))
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        print('Audit log failed:', e)

# --- system config helpers ---
def set_config(key, value):
    conn = get_db(); cur = conn.cursor()
    cur.execute("REPLACE INTO system_config (`key`,`value`) VALUES (%s,%s)", (key, str(value)))
    conn.commit(); cur.close(); conn.close()

def get_config(key, default=None):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT `value` FROM system_config WHERE `key`=%s", (key,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else default

def is_maintenance_mode():
    return str(get_config('maintenance_mode','0')) == '1'

# --- middleware: check maintenance before each request ---
@app.before_request
def check_maintenance():
    # allow admin to bypass maintenance, and allow static + login
    if request.endpoint and request.endpoint.startswith('static'):
        return
    if is_maintenance_mode():
        uid = session.get('user_id')
        if not uid or not is_admin(uid):
            return render_template('503.html'), 503

# --- Alerts endpoints (admin can create) ---
@app.route('/admin/alerts', methods=['GET','POST'])
@login_required
def admin_alerts():
    uid = session.get('user_id')
    if not is_admin(uid):
        flash('غير مصرح'); return redirect(url_for('dashboard'))
    conn = get_db(); cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cur.execute('INSERT INTO alerts (title,body,level,created_by) VALUES (%s,%s,%s,%s)',
                    (request.form['title'], request.form['body'], request.form.get('level','info'), uid))
        conn.commit(); log_audit(uid,'create_alert','alert','','title='+request.form['title'])
        return redirect(url_for('admin_alerts'))
    cur.execute('SELECT * FROM alerts ORDER BY created_at DESC')
    alerts = cur.fetchall(); cur.close(); conn.close()
    return render_template('admin_alerts.html', alerts=alerts)

@app.route('/alerts/active')
@login_required
def alerts_active():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM alerts WHERE is_active=1 ORDER BY created_at DESC")
    a = cur.fetchall(); cur.close(); conn.close()
    return jsonify(a)

# --- Maintenance toggle (admin) ---
@app.route('/admin/maintenance/toggle', methods=['POST'])
@login_required
def admin_maintenance_toggle():
    if not is_admin(session.get('user_id')):
        return jsonify({'error':'forbidden'}), 403
    mode = request.form.get('mode','0')
    set_config('maintenance_mode', '1' if mode=='1' else '0')
    log_audit(session['user_id'], 'toggle_maintenance', 'system', '', f'mode={mode}')
    flash('تم تحديث حالة الصيانة')
    return redirect(url_for('admin_alerts'))

# --- Audit export (CSV) ---
@app.route('/admin/audit/export')
@login_required
def admin_audit_export():
    if not is_admin(session.get('user_id')):
        flash('غير مصرح'); return redirect(url_for('dashboard'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id, user_id, action, object_type, object_id, details, created_at FROM audit_log ORDER BY created_at DESC")
    rows = cur.fetchall(); cur.close(); conn.close()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','user_id','action','object_type','object_id','details','created_at'])
    cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=audit_log.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output



if __name__ == '__main__':
    # set debug via env var DEBUG=1
    debug = os.getenv('DEBUG','0') == '1'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
