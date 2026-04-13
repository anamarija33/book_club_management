# Označava "models" kao Python paket.
# Ovdje žive SQLAlchemy ORM modeli — Python klase koje predstavljaju
# tablice u bazi podataka.
# Primjer (dolazi u predavanju 2):
#   class User(Base):
#       __tablename__ = "users"
#       id = Column(Integer, primary_key=True)
#       email = Column(String, unique=True)
from app.core.database import Base
from app.models.book import Book
from app.models.club import Club
from app.models.membership import Membership
from app.models.user import User
from app.models.user_book import UserBook

__all__ = ["Base", "Book", "Club", "Membership", "User", "UserBook"]
