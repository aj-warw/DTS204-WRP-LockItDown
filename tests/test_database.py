from pathlib import Path
from tempfile import TemporaryDirectory
from app.db import Database

def test_auth_and_progress():
 with TemporaryDirectory() as d:
  db=Database(Path(d)/'test.db');db.seed();assert db.authenticate('employee@company.com','Password1!');pct,passed=db.save_quiz(5,1,4,5);assert pct==80 and passed
