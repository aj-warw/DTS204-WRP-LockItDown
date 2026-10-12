import re, tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from .db import Database
P='#7A3FF2';D='#4D2397';L='#F3ECFF';W='#FFFFFF';T='#1F1630';M='#6B6474';B='#D9CDED';G='#218739';R='#B42318';FONT='Segoe UI'
def lab(p,t,s=10,b=False,fg=T,bg=W):return tk.Label(p,text=t,font=(FONT,s,'bold' if b else 'normal'),fg=fg,bg=bg)
def btn(p,t,c,sec=False):return tk.Button(p,text=t,command=c,bg=L if sec else P,fg=D if sec else W,relief='flat',padx=14,pady=8,font=(FONT,10,'bold'),cursor='hand2')
def ent(p,v,show=None):return tk.Entry(p,textvariable=v,show=show,font=(FONT,11),relief='solid',bd=1)
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('Lock IT Down');self.geometry('1180x720');self.minsize(1050,650);self.configure(bg=W);self.db=Database(Path(__file__).parents[1]/'data'/'lockitdown.db');self.db.seed();self.user=None;self.course=1;self.show('welcome')
 def clear(self):
  for x in self.winfo_children():x.destroy()
 def show(self,n,**k):self.clear();getattr(self,'page_'+n)(**k)
 def menus(self):
  return {'employee':[('Dashboard','employee_dashboard'),('Available Modules','modules'),('My Progress','progress'),('Achievements','achievements')],'manager':[('Dashboard','manager_dashboard'),('Employees','employees'),('Assign Course','assign_course'),('Reports','reports')],'admin':[('Dashboard','admin_dashboard'),('Manage Users','manage_users'),('Assign Courses','admin_assign'),('Manage Courses','manage_courses'),('System Data','system_data')]}[self.user['role']]
 def shell(self,title):
  body=tk.Frame(self,bg=W);body.pack(fill='both',expand=True);side=tk.Frame(body,bg='#FBF9FF',width=210,highlightbackground=B,highlightthickness=1);side.pack(side='left',fill='y');side.pack_propagate(False);lab(side,'LOCK IT DOWN',13,True,D,'#FBF9FF').pack(anchor='w',padx=18,pady=(24,4));lab(side,self.user['role'].upper(),9,True,M,'#FBF9FF').pack(anchor='w',padx=18,pady=(0,16))
  for text,page in self.menus():tk.Button(side,text=text,command=lambda p=page:self.show(p),anchor='w',bg='#FBF9FF',fg=T,relief='flat',padx=15,pady=10).pack(fill='x',padx=10)
  tk.Button(side,text='Logout',command=self.logout,anchor='w',bg='#FBF9FF',fg=T,relief='flat',padx=15,pady=10).pack(fill='x',padx=10,pady=8)
  c=tk.Frame(body,bg=W);c.pack(fill='both',expand=True,padx=30,pady=28);lab(c,title,23,True,D).pack(anchor='w');return c
 def table(self,p,cols,rows,h=9):
  st=ttk.Style();st.theme_use('clam');st.configure('Treeview',rowheight=32,font=(FONT,10));st.configure('Treeview.Heading',background=L,foreground=D,font=(FONT,10,'bold'));t=ttk.Treeview(p,columns=cols,show='headings',height=h)
  for c in cols:t.heading(c,text=c);t.column(c,width=140,anchor='w')
  for r in rows:t.insert('','end',values=r)
  t.pack(fill='both',expand=True,pady=12);return t
 def statrow(self,c,items):
  r=tk.Frame(c,bg=W);r.pack(fill='x',pady=18)
  for name,val in items:x=tk.Frame(r,bg=W,highlightbackground=B,highlightthickness=1,height=105);x.pack(side='left',fill='x',expand=True,padx=(0,12));x.pack_propagate(False);lab(x,name,10,True).pack(pady=(18,4));lab(x,str(val),20,True,P).pack()
 def logout(self):self.user=None;self.show('login')
 def page_welcome(self):
  x=tk.Frame(self,bg=W);x.pack(fill='both',expand=True);y=tk.Frame(x,bg=W);y.place(relx=.5,rely=.46,anchor='center');lab(y,'◆',48,True,P).pack();lab(y,'LOCK IT DOWN',27,True,D).pack();lab(y,'Security Awareness Training Platform',11,False,M).pack();lab(y,'Role-based learning, progress tracking and reporting.',10,False,M).pack(pady=20);btn(y,'Get Started',lambda:self.show('login')).pack()
 def page_login(self):
  x=tk.Frame(self,bg=W);x.pack(fill='both',expand=True);y=tk.Frame(x,bg=W);y.place(relx=.5,rely=.46,anchor='center');lab(y,'Welcome Back',23,True,D).pack(pady=10);self.le=tk.StringVar();self.lp=tk.StringVar()
  for n,v,s in [('Company Email',self.le,None),('Password',self.lp,'•')]:lab(y,n,9,True,M).pack(anchor='w',pady=(10,4));ent(y,v,s).pack(fill='x',ipady=7)
  self.lmsg=lab(y,'',9,False,R);self.lmsg.pack(pady=7);btn(y,'Login',self.login).pack(fill='x');tk.Button(y,text='First time user? Set your password',command=lambda:self.show('set_password'),bg=W,fg=P,relief='flat').pack(pady=10)
 def login(self):
  u=self.db.authenticate(self.le.get(),self.lp.get())
  if not u:self.lmsg.config(text='Email or password is incorrect.');return
  self.user=u;self.show(u['role']+'_dashboard')
 def page_set_password(self):
  x=tk.Frame(self,bg=W);x.pack(fill='both',expand=True);y=tk.Frame(x,bg=W);y.place(relx=.5,rely=.45,anchor='center');lab(y,'Set Your Password',22,True,D).pack();self.se=tk.StringVar();self.s1=tk.StringVar();self.s2=tk.StringVar()
  for n,v,s in [('Company Email',self.se,None),('New Password',self.s1,'•'),('Confirm Password',self.s2,'•')]:lab(y,n,9,True,M).pack(anchor='w',pady=(10,4));ent(y,v,s).pack(fill='x',ipady=6)
  self.smsg=lab(y,'At least 8 characters with uppercase, lowercase and a number.',9,False,M);self.smsg.pack(pady=8);btn(y,'Set Password',self.setpw).pack(fill='x');tk.Button(y,text='Back to login',command=lambda:self.show('login'),bg=W,fg=P,relief='flat').pack(pady=8)
 def setpw(self):
  p=self.s1.get()
  if len(p)<8 or not any(x.isupper() for x in p) or not any(x.islower() for x in p) or not any(x.isdigit() for x in p):self.smsg.config(text='Password does not meet the guidance.',fg=R);return
  if p!=self.s2.get():self.smsg.config(text='Passwords do not match.',fg=R);return
  self.db.set_password(self.se.get(),p);self.smsg.config(text='Password updated. Return to login.',fg=G)
 def summary(self,uid):
  p=self.db.rows('SELECT * FROM progress WHERE user_id=?',(uid,));sc=[x['percent'] for x in p if x['score']!='-'];return len(p),sum(x['status']=='Complete' for x in p),round(sum(sc)/len(sc)) if sc else 0,sum(x['percent'] for x in p if x['status']=='Complete')
 def page_employee_dashboard(self):
  c=self.shell('Welcome, '+self.user['name']);a,done,avg,pts=self.summary(self.user['id']);self.statrow(c,[('Assigned',a),('Completed',done),('Average Score',str(avg)+'%'),('Points',pts)]);rows=self.db.rows('''SELECT c.title,a.due_date,p.status,p.percent FROM assignments a JOIN courses c ON c.id=a.course_id JOIN progress p ON p.user_id=a.user_id AND p.course_id=a.course_id WHERE a.user_id=?''',(self.user['id'],));self.table(c,['Course','Due Date','Status','Progress'],[(x['title'],x['due_date'],x['status'],str(x['percent'])+'%') for x in rows])
 def page_modules(self):
  c=self.shell('Available Training Modules');r=tk.Frame(c,bg=W);r.pack(fill='x',pady=20)
  for x in self.db.rows('SELECT * FROM courses'):
   z=tk.Frame(r,bg=W,width=245,height=260,highlightbackground=B,highlightthickness=1);z.pack(side='left',padx=(0,16));z.pack_propagate(False);lab(z,'◇',38,False,P).pack(pady=(20,5));lab(z,x['title'],13,True,D).pack();lab(z,x['description'],9,False,M).pack(pady=8);lab(z,x['duration'],9,False,M).pack();btn(z,'Start Course',lambda cid=x['id']:self.show('training',course_id=cid)).pack(pady=20)
 def page_training(self,course_id):self.course=course_id;self.step=1;self.tc=self.shell(self.db.one('SELECT title FROM courses WHERE id=?',(course_id,))['title']);self.render_training()
 def render_training(self):
  for w in self.tc.winfo_children()[1:]:w.destroy()
  x=self.db.one('SELECT * FROM courses WHERE id=?',(self.course,));parts=x['content'].split('|');lab(self.tc,'Progress '+str(self.step*20)+'%',10,True).pack(anchor='e');q=lab(self.tc,parts[self.step-1],13,False,T);q.config(wraplength=760,justify='left');q.pack(anchor='w',pady=60);n=tk.Frame(self.tc,bg=W);n.pack(side='bottom',fill='x');btn(n,'Previous',self.prev,True).pack(side='left');lab(n,f'{self.step} / 5',10,False,M).pack(side='left',expand=True);btn(n,'Start Quiz' if self.step==5 else 'Next',self.next).pack(side='right');self.db.module_progress(self.user['id'],self.course,self.step*20)
 def prev(self):self.step=max(1,self.step-1);self.render_training()
 def next(self):
  if self.step==5:self.show('quiz')
  else:self.step+=1;self.render_training()
 def qs(self):return [('Which is a common sign of phishing?',['Routine newsletter','Urgent request for login details','Expected calendar invite','Approved update'],1),('Before opening an unexpected link, you should:',['Verify it independently','Open it quickly','Disable protection','Forward it externally'],0),('The strongest choice is:',['A long unique passphrase','password123','Your name','One reused password'],0),('Social engineering targets:',['People and decision-making','Only hardware','Only backups','Printer settings'],0),('A suspected phish should be:',['Reported through the approved channel','Ignored','Posted publicly','Replied to'],0)]
 def page_quiz(self):self.qi=0;self.score=0;self.choice=tk.IntVar(value=-1);self.qc=self.shell('Quiz');self.render_q()
 def render_q(self):
  for w in self.qc.winfo_children()[1:]:w.destroy()
  q,o,correct=self.qs()[self.qi];lab(self.qc,f'Question {self.qi+1} of 5',10,False,M).pack(anchor='w');lab(self.qc,q,13,True).pack(anchor='w',pady=20);self.choice.set(-1)
  for i,v in enumerate(o):tk.Radiobutton(self.qc,text=f'{chr(65+i)}   {v}',variable=self.choice,value=i,indicatoron=False,anchor='w',bg=W,selectcolor=L,relief='solid',bd=1,padx=12,pady=10).pack(fill='x',pady=4)
  self.qmsg=lab(self.qc,'',9,False,R);self.qmsg.pack(anchor='w',pady=8);btn(self.qc,'Submit Answer',self.submit).pack(anchor='e')
 def submit(self):
  if self.choice.get()<0:self.qmsg.config(text='Select an answer.');return
  self.score+=self.choice.get()==self.qs()[self.qi][2];self.qi+=1
  if self.qi<5:self.render_q()
  else:pct,passed=self.db.save_quiz(self.user['id'],self.course,self.score,5);self.show('result',pct=pct,passed=passed)
 def page_result(self,pct,passed):
  c=self.shell('Quiz Result');x=tk.Frame(c,bg=W);x.place(relx=.5,rely=.42,anchor='center');lab(x,'✓' if passed else '↻',44,True,G if passed else P).pack();lab(x,'Passed' if passed else 'Review Required',22,True,D).pack();lab(x,f'Score: {self.score}/5 ({pct}%)',12).pack(pady=10);lab(x,'Your score and progress have been saved.',10,False,M).pack(pady=10);btn(x,'View Progress',lambda:self.show('progress')).pack()
 def page_progress(self):
  c=self.shell('My Progress');a,dn,av,pt=self.summary(self.user['id']);self.statrow(c,[('Completed',f'{dn}/{a}'),('Average Score',f'{av}%'),('Points',pt)]);r=self.db.rows('SELECT c.title,p.score,p.status,p.percent,p.updated FROM progress p JOIN courses c ON c.id=p.course_id WHERE p.user_id=?',(self.user['id'],));self.table(c,['Course','Score','Status','Progress','Updated'],[(x['title'],x['score'],x['status'],str(x['percent'])+'%',x['updated']) for x in r])
 def page_achievements(self):
  c=self.shell('Achievements');a,dn,av,pt=self.summary(self.user['id']);self.statrow(c,[('Learning Level',1+dn),('Courses Passed',dn),('Points',pt),('Average',f'{av}%')])
 def managed(self):return self.db.rows("SELECT * FROM users WHERE role='employee' AND manager_id=? AND active=1",(self.user['id'],))
 def page_manager_dashboard(self):
  c=self.shell('Manager Dashboard');emps=self.managed();s=[self.summary(x['id']) for x in emps];self.statrow(c,[('Employees',len(emps)),('Courses Completed',sum(x[1] for x in s)),('Average Score',f"{round(sum(x[2] for x in s)/len(s)) if s else 0}%")]);self.table(c,['Employee','Email','Assigned','Completed','Average'],[(u['name'],u['email'],*self.summary(u['id'])[:3]) for u in emps])
 def page_employees(self):
  c=self.shell('Employees');self.table(c,['Employee','Email','Assigned','Completed','Average'],[(u['name'],u['email'],*self.summary(u['id'])[:3]) for u in self.managed()])
 def page_assign_course(self):self.assignment_ui(self.shell('Assign Course'),self.managed())
 def assignment_ui(self,c,users):
  courses=self.db.rows('SELECT * FROM courses ORDER BY title');self.au=tk.StringVar();self.ac=tk.StringVar();self.ad=tk.StringVar(value='31/12/2026');lab(c,'User',9,True,M).pack(anchor='w',pady=(15,4));ttk.Combobox(c,textvariable=self.au,values=[f"{x['id']} | {x['name']}" for x in users],state='readonly').pack(fill='x',ipady=5);lab(c,'Course',9,True,M).pack(anchor='w',pady=(15,4));ttk.Combobox(c,textvariable=self.ac,values=[f"{x['id']} | {x['title']}" for x in courses],state='readonly').pack(fill='x',ipady=5);lab(c,'Due date (DD/MM/YYYY)',9,True,M).pack(anchor='w',pady=(15,4));ent(c,self.ad).pack(fill='x',ipady=6);self.amsg=lab(c,'',9,False,G);self.amsg.pack(pady=10);f=tk.Frame(c,bg=W);f.pack(anchor='e');btn(f,'Unassign',self.unassign,True).pack(side='left',padx=5);btn(f,'Assign / Update',self.assign).pack(side='left')
 def assign(self):
  try:uid=int(self.au.get().split('|')[0]);cid=int(self.ac.get().split('|')[0]);datetime.strptime(self.ad.get(),'%d/%m/%Y');self.db.assign(uid,cid,self.ad.get());self.amsg.config(text='Assignment saved.',fg=G)
  except Exception:self.amsg.config(text='Select a user, course and valid date.',fg=R)
 def unassign(self):
  try:self.db.unassign(int(self.au.get().split('|')[0]),int(self.ac.get().split('|')[0]));self.amsg.config(text='Course unassigned.',fg=G)
  except Exception:self.amsg.config(text='Select a user and course.',fg=R)
 def page_reports(self):
  c=self.shell('Reports');ids=[x['id'] for x in self.managed()];rows=[]
  for uid in ids:rows+=self.db.rows('SELECT u.name,c.title,p.score,p.status,p.updated FROM progress p JOIN users u ON u.id=p.user_id JOIN courses c ON c.id=p.course_id WHERE p.user_id=?',(uid,))
  self.table(c,['Employee','Course','Score','Status','Updated'],[(x['name'],x['title'],x['score'],x['status'],x['updated']) for x in rows])
 def page_admin_dashboard(self):
  c=self.shell('Admin Dashboard');self.statrow(c,[('Active Users',self.db.one('SELECT COUNT(*) n FROM users WHERE active=1')['n']),('Managers',self.db.one("SELECT COUNT(*) n FROM users WHERE role='manager'")['n']),('Courses',self.db.one('SELECT COUNT(*) n FROM courses')['n']),('Assignments',self.db.one('SELECT COUNT(*) n FROM assignments')['n'])])
 def page_manage_users(self):
  c=self.shell('Manage Users');left=tk.Frame(c,bg=W);left.pack(side='left',fill='both',expand=True);right=tk.Frame(c,bg=W,width=310,highlightbackground=B,highlightthickness=1);right.pack(side='left',fill='y',padx=(20,0));right.pack_propagate(False);self.ut=self.table(left,['ID','Name','Email','Role','Manager'],self.user_rows(),12);self.ut.bind('<<TreeviewSelect>>',self.pick_user);lab(right,'Create / Edit User',15,True,D).pack(pady=18);self.uid=None;self.un=tk.StringVar();self.ue=tk.StringVar();self.ur=tk.StringVar(value='employee');self.um=tk.StringVar();self.up=tk.StringVar()
  for n,v in [('Full name',self.un),('Email',self.ue),('Temporary password',self.up)]:lab(right,n,9,True,M).pack(anchor='w',padx=20,pady=(8,3));ent(right,v,'•' if 'password' in n else None).pack(fill='x',padx=20,ipady=5)
  lab(right,'Role',9,True,M).pack(anchor='w',padx=20,pady=(8,3));ttk.Combobox(right,textvariable=self.ur,values=['employee','manager','admin'],state='readonly').pack(fill='x',padx=20,ipady=4);lab(right,'Manager',9,True,M).pack(anchor='w',padx=20,pady=(8,3));self.mcb=ttk.Combobox(right,textvariable=self.um,values=[f"{x['id']} | {x['name']}" for x in self.db.rows("SELECT * FROM users WHERE role='manager' ORDER BY name")],state='readonly');self.mcb.pack(fill='x',padx=20,ipady=4);self.umsg=lab(right,'',9,False,G);self.umsg.pack(pady=8);f=tk.Frame(right,bg=W);f.pack();btn(f,'Clear',self.clear_user,True).pack(side='left',padx=3);btn(f,'Delete',self.delete_user,True).pack(side='left',padx=3);btn(f,'Save',self.save_user).pack(side='left',padx=3)
 def user_rows(self):
  return [(x['id'],x['name'],x['email'],x['role'],x['manager'] or '-') for x in self.db.rows('SELECT u.*,m.name manager FROM users u LEFT JOIN users m ON m.id=u.manager_id ORDER BY u.name')]
 def pick_user(self,_=None):
  if not self.ut.selection():return
  v=self.ut.item(self.ut.selection()[0],'values');self.uid=int(v[0]);u=self.db.one('SELECT * FROM users WHERE id=?',(self.uid,));self.un.set(u['name']);self.ue.set(u['email']);self.ur.set(u['role']);self.up.set('');mgr=self.db.one('SELECT * FROM users WHERE id=?',(u['manager_id'],)) if u['manager_id'] else None;self.um.set(f"{mgr['id']} | {mgr['name']}" if mgr else '')
 def clear_user(self):self.uid=None;self.un.set('');self.ue.set('');self.ur.set('employee');self.um.set('');self.up.set('')
 def save_user(self):
  if not self.un.get().strip() or not re.fullmatch(r'[^@ ]+@[^@ ]+\.[^@ ]+',self.ue.get()):self.umsg.config(text='Enter a valid name and email.',fg=R);return
  mid=int(self.um.get().split('|')[0]) if self.um.get() and self.ur.get()=='employee' else None
  try:self.db.save_user(self.uid,self.un.get().strip(),self.ue.get().strip(),self.ur.get(),mid,self.up.get() or None);self.umsg.config(text='User saved.',fg=G);self.show('manage_users')
  except Exception as e:self.umsg.config(text='Email already exists or data is invalid.',fg=R)
 def delete_user(self):
  if not self.uid:return
  if self.uid==self.user['id']:self.umsg.config(text='You cannot delete the logged-in account.',fg=R);return
  if messagebox.askyesno('Delete user','Delete this user and all related assignments and results?'):self.db.delete_user(self.uid);self.show('manage_users')
 def page_admin_assign(self):self.assignment_ui(self.shell('Assign Courses'),self.db.rows("SELECT * FROM users WHERE role='employee' ORDER BY name"))
 def page_manage_courses(self):
  c=self.shell('Manage Courses');self.ct=self.table(c,['ID','Title','Description','Duration'],[(x['id'],x['title'],x['description'],x['duration']) for x in self.db.rows('SELECT * FROM courses ORDER BY title')]);f=tk.Frame(c,bg=W);f.pack(fill='x');self.cn=tk.StringVar();self.cd=tk.StringVar();self.cdur=tk.StringVar(value='30 mins');
  for n,v in [('Title',self.cn),('Description',self.cd),('Duration',self.cdur)]:lab(f,n,9,True,M).pack(anchor='w',pady=(6,2));ent(f,v).pack(fill='x',ipady=5)
  btn(f,'Add Course',self.add_course).pack(anchor='e',pady=8)
 def add_course(self):
  if self.cn.get() and self.cd.get():self.db.execute("INSERT INTO courses(title,description,duration,content) VALUES(?,?,?,'Introduction.|Key risks.|Safe practice.|Reporting process.|Review.')",(self.cn.get(),self.cd.get(),self.cdur.get()));self.show('manage_courses')
 def page_system_data(self):
  c=self.shell('System Data');self.table(c,['Data','Records'],[(n,self.db.one(f'SELECT COUNT(*) n FROM {n}')['n']) for n in ['users','courses','assignments','progress','attempts']])
