from database import Base, engine
import models  # registers every table on Base

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("All tables dropped and recreated (empty).")