from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Ipod12345@localhost/fastpai"

engine = create_engine( SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# while True:
#     try:
#         conn= psycopg2.connect(host='localhost',database='fastpai', user='postgres',password='Ipod12345',cursor_factory=RealDictCursor)
#         cursor= conn.cursor()
#         break
#     except Exception as error:
#         print(error)
#         time.sleep(2)