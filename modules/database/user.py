import sqlalchemy as sql
import sqlalchemy.orm as orm
from typing import Optional

DATABASE_PATH = "./local_only/databases/user.db"

class Base(orm.DeclarativeBase):
    pass

class Driver:
    BASE = Base
    engine = sql.create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    SessionMaker = orm.sessionmaker(bind=engine, expire_on_commit=False)

class User(Driver.BASE):
    __tablename__ = "User"
    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    preferred_language: orm.Mapped[Optional[str]]
    # money: orm.Mapped[Optional[int]]
    

    def __init__(self, **kw: sql.Any):
        super().__init__(**kw)

    def to_dict(self):
        _dict = {}
        _dict["id"] = self.id
        _dict["preferred_language"] = self.preferred_language
        
        return _dict
