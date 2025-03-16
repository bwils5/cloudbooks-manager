from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://bpu333:Landmark123!@localhost:3306/cloudbooks_db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Ensure tables are created
def init_db():
    metadata.create_all(engine)

init_db()
