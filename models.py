

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Numeric
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


SQLALCHEMY_DATABASE_URL = "sqlite:///mesh.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


class Account(Base):

    __tablename__ = "accounts"

    id = Column(
        Integer,
        primary_key=True
    )

    owner = Column(
        String(255),
        unique=True,
        nullable=False
    )

    balance = Column(
        Numeric(18, 2),
        nullable=False
    )


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True
    )

    packet_hash = Column(
        String(255),
        unique=True,
        nullable=False
    )

    sender = Column(
        String(255),
        nullable=False
    )

    receiver = Column(
        String(255),
        nullable=False
    )

    amount = Column(
        Numeric(18, 2),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )


Base.metadata.create_all(
    bind=engine
)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()