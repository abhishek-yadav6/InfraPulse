from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:Root%40123@localhost/infrapulse"

engine = create_engine(DATABASE_URL)