import sqlite3, hashlib, hmac, os
from pathlib import Path
from datetime import date

class Database:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.init()
    def con(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
    @staticmethod
    def hash_password(password,salt=None):
        salt=salt or os.urandom(16).hex(); digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),120000).hex(); return digest,salt
    def init(self):
        with self.con() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,role TEXT NOT NULL CHECK(role IN ('employee','manager','admin')),manager_id INTEGER REFERENCES users(id) ON DELETE SET NULL,password_hash TEXT NOT NULL,salt TEXT NOT NULL,must_change INTEGER DEFAULT 1,active INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT UNIQUE NOT NULL,description TEXT NOT NULL,duration TEXT NOT NULL,content TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,due_date TEXT NOT NULL,UNIQUE(user_id,course_id));
            CREATE TABLE IF NOT EXISTS progress(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,status TEXT NOT NULL DEFAULT 'Not Started',percent INTEGER DEFAULT 0,score TEXT DEFAULT '-',updated TEXT DEFAULT '-',PRIMARY KEY(user_id,course_id));
            CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,score INTEGER,total INTEGER,percent INTEGER,result TEXT,attempted TEXT);
            ''')
    def seed(self,force=False):
        with self.con() as c:
            if force:c.executescript('DELETE FROM attempts;DELETE FROM progress;DELETE FROM assignments;DELETE FROM courses;DELETE FROM users;')
            if c.execute('SELECT COUNT(*) FROM users').fetchone()[0]:return
            people=[('Morgan Roberts','manager.roberts@company.com','manager',None),('Priya Shah','manager.shah@company.com','manager',None),('Daniel Hughes','manager.hughes@company.com','manager',None),('System Administrator','admin@company.com','admin',None)]
            for n,e,r,m in people:
                h,s=self.hash_password('Password1!');c.execute('INSERT INTO users(name,email,role,manager_id,password_hash,salt,must_change) VALUES(?,?,?,?,?,?,0)',(n,e,r,m,h,s))
            mgr=c.execute("SELECT id FROM users WHERE email='manager.roberts@company.com'").fetchone()[0]
            for n,e in [('Employee User','employee@company.com'),('Alex Brown','alex.brown@company.com'),('Sam Jones','sam.jones@company.com'),('Taylor Green','taylor.green@company.com'),('Jamie Smith','jamie.smith@company.com')]:
                h,s=self.hash_password('Password1!');c.execute('INSERT INTO users(name,email,role,manager_id,password_hash,salt,must_change) VALUES(?,?,?,?,?,?,0)',(n,e,'employee',mgr,h,s))
            courses=[('Phishing Awareness','Identify suspicious emails','30 mins','Understand phishing and urgency.|Check senders, domains and links.|Verify unusual requests independently.|Report suspicious messages correctly.|Review the warning signs.'),('Password Hygiene','Create and protect secure passwords','25 mins','Use long unique passphrases.|Never reuse workplace passwords.|Use approved password managers.|Enable multi-factor authentication.|Review password safety.'),('Social Engineering','Recognise manipulation tactics','35 mins','Recognise authority and urgency tactics.|Verify identity before disclosure.|Protect sensitive workplace information.|Challenge unexpected requests safely.|Review reporting routes.')]
            c.executemany('INSERT INTO courses(title,description,duration,content) VALUES(?,?,?,?)',courses)
            employee=c.execute("SELECT id FROM users WHERE email='employee@company.com'").fetchone()[0]
            for cid,due in [(1,'12/11/2026'),(2,'19/11/2026'),(3,'26/11/2026')]:
                c.execute('INSERT INTO assignments(user_id,course_id,due_date) VALUES(?,?,?)',(employee,cid,due));c.execute('INSERT INTO progress(user_id,course_id) VALUES(?,?)',(employee,cid))
    def authenticate(self,email,password):
        with self.con() as c:r=c.execute('SELECT * FROM users WHERE lower(email)=lower(?) AND active=1',(email.strip(),)).fetchone()
        if not r:return None
        digest=self.hash_password(password,r['salt'])[0]
        return dict(r) if hmac.compare_digest(digest,r['password_hash']) else None
    def rows(self,q,p=()):
        with self.con() as c:return [dict(x) for x in c.execute(q,p).fetchall()]
    def one(self,q,p=()):
        with self.con() as c:r=c.execute(q,p).fetchone();return dict(r) if r else None
    def execute(self,q,p=()):
        with self.con() as c:cur=c.execute(q,p);return cur.lastrowid
    def save_user(self,user_id,name,email,role,manager_id,password=None):
        manager_id=manager_id or None
        if user_id:
            self.execute('UPDATE users SET name=?,email=?,role=?,manager_id=? WHERE id=?',(name,email,role,manager_id,user_id))
            if password:
                h,s=self.hash_password(password);self.execute('UPDATE users SET password_hash=?,salt=?,must_change=1 WHERE id=?',(h,s,user_id))
            return user_id
        h,s=self.hash_password(password or 'ChangeMe123!');return self.execute('INSERT INTO users(name,email,role,manager_id,password_hash,salt,must_change) VALUES(?,?,?,?,?,?,1)',(name,email,role,manager_id,h,s))
    def delete_user(self,user_id):self.execute('DELETE FROM users WHERE id=?',(user_id,))
    def set_password(self,email,password):
        h,s=self.hash_password(password);return self.execute('UPDATE users SET password_hash=?,salt=?,must_change=0 WHERE lower(email)=lower(?)',(h,s,email.strip()))
    def assign(self,user_id,course_id,due):
        self.execute('INSERT INTO assignments(user_id,course_id,due_date) VALUES(?,?,?) ON CONFLICT(user_id,course_id) DO UPDATE SET due_date=excluded.due_date',(user_id,course_id,due));self.execute("INSERT INTO progress(user_id,course_id,status,percent,score,updated) VALUES(?,?,'Not Started',0,'-','-') ON CONFLICT(user_id,course_id) DO NOTHING",(user_id,course_id))
    def unassign(self,user_id,course_id):
        self.execute('DELETE FROM assignments WHERE user_id=? AND course_id=?',(user_id,course_id));self.execute('DELETE FROM progress WHERE user_id=? AND course_id=?',(user_id,course_id))
    def module_progress(self,uid,cid,pct):self.execute("UPDATE progress SET status=CASE WHEN status='Complete' THEN status ELSE 'In Progress' END,percent=CASE WHEN percent>? THEN percent ELSE ? END,updated=? WHERE user_id=? AND course_id=?",(pct,pct,date.today().strftime('%d/%m/%Y'),uid,cid))
    def save_quiz(self,uid,cid,score,total):
        pct=round(score/total*100);passed=pct>=80;today=date.today().strftime('%d/%m/%Y');self.execute('INSERT INTO attempts(user_id,course_id,score,total,percent,result,attempted) VALUES(?,?,?,?,?,?,?)',(uid,cid,score,total,pct,'Passed' if passed else 'Review Required',today));self.execute('UPDATE progress SET status=?,percent=?,score=?,updated=? WHERE user_id=? AND course_id=?',('Complete' if passed else 'Review Required',pct,f'{score}/{total}',today,uid,cid));return pct,passed
