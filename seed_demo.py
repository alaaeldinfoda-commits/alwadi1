
import os
from dotenv import load_dotenv
import mysql.connector
from werkzeug.security import generate_password_hash
load_dotenv()
cfg = {
    'host': os.getenv('DB_HOST','localhost'),
    'user': os.getenv('DB_USER','root'),
    'password': os.getenv('DB_PASSWORD',''),
    'database': os.getenv('DB_NAME','enterprise_system'),
    'port': int(os.getenv('DB_PORT',3306))
}
conn = mysql.connector.connect(**cfg)
cur = conn.cursor()
cur.execute("INSERT IGNORE INTO roles (role_name) VALUES ('Admin'), ('Manager'), ('Engineer'), ('Viewer')")
conn.commit()
# create admin if not exists
cur.execute("SELECT user_id FROM users WHERE username='admin'")
if not cur.fetchone():
    cur.execute("INSERT INTO users (username,password,fullname,role_id) VALUES (%s,%s,%s,(SELECT role_id FROM roles WHERE role_name='Admin'))", ('admin', generate_password_hash('admin123'), 'System Administrator'))
    conn.commit()
# assign role_permissions for Admin (give everything)
perms = ['manage_users','site_view','site_add','site_edit','site_delete','contractor_view','contractor_add','contractor_edit','contractor_delete','report_view','report_add','report_edit','report_delete']
for p in perms:
    cur.execute("INSERT IGNORE INTO roles_permissions (role_id, permission) VALUES ((SELECT role_id FROM roles WHERE role_name='Admin'), %s)", (p,))
conn.commit()
cur.close(); conn.close()
print('Seeded roles and admin (password=admin123)') 
