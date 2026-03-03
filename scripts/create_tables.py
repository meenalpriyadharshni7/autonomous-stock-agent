from app.memory.db import engine
from app.memory.models import Base

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully.")

if __name__ == "__main__":
    create_tables()