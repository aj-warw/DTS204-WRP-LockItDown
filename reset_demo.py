from pathlib import Path
from app.db import Database
Database(Path(__file__).parent/'data'/'lockitdown.db').seed(force=True)
print('Demo database reset.')
