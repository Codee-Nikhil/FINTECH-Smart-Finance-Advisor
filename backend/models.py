from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ─────────────────────────────────────────
#  USER
# ─────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    city_type  = db.Column(db.String(20), default='metro')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    budgets    = db.relationship('Budget',   backref='user', lazy=True, cascade='all, delete-orphan')
    goals      = db.relationship('Goal',     backref='user', lazy=True, cascade='all, delete-orphan')
    chat_logs  = db.relationship('ChatLog',  backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id':        self.id,
            'name':      self.name,
            'email':     self.email,
            'city_type': self.city_type,
            'created_at': self.created_at.isoformat(),
        }


# ─────────────────────────────────────────
#  BUDGET  (one per user per month/year)
# ─────────────────────────────────────────
class Budget(db.Model):
    __tablename__ = 'budgets'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month      = db.Column(db.String(20), nullable=False)   # e.g. "December"
    year       = db.Column(db.Integer,   nullable=False)    # e.g. 2025
    income     = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    expenses   = db.relationship('Expense', backref='budget', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':       self.id,
            'month':    self.month,
            'year':     self.year,
            'income':   self.income,
            'expenses': [e.to_dict() for e in self.expenses],
        }


# ─────────────────────────────────────────
#  EXPENSE  (category rows inside a budget)
# ─────────────────────────────────────────
class Expense(db.Model):
    __tablename__ = 'expenses'

    id         = db.Column(db.Integer, primary_key=True)
    budget_id  = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category   = db.Column(db.String(100), nullable=False)
    actual     = db.Column(db.Float, default=0)
    budget_amt = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'category':   self.category,
            'actual':     self.actual,
            'budget_amt': self.budget_amt,
        }


# ─────────────────────────────────────────
#  GOAL
# ─────────────────────────────────────────
class Goal(db.Model):
    __tablename__ = 'goals'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name        = db.Column(db.String(150), nullable=False)
    target      = db.Column(db.Float, nullable=False)
    saved       = db.Column(db.Float, default=0)
    goal_type   = db.Column(db.String(50), default='other')
    target_date = db.Column(db.String(50))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'target':      self.target,
            'saved':       self.saved,
            'goal_type':   self.goal_type,
            'target_date': self.target_date,
            'progress':    round((self.saved / self.target) * 100, 1) if self.target else 0,
            'created_at':  self.created_at.isoformat(),
        }


# ─────────────────────────────────────────
#  CHAT LOG
# ─────────────────────────────────────────
class ChatLog(db.Model):
    __tablename__ = 'chat_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role       = db.Column(db.String(10), nullable=False)   # 'user' or 'assistant'
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'role':       self.role,
            'message':    self.message,
            'created_at': self.created_at.isoformat(),
        }
