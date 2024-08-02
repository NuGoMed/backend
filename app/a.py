# test_crud.py
from sqlalchemy.orm import Session
from sql_app import crud, database, models

def test_get_tier_lists():
    # Create a database session
    db = database.SessionLocal()
    
    try:
        # Call the CRUD function
        tier_lists = crud.get_tier_lists(db, skip=0, limit=10)
        
        # Print the results
        for tier_list in tier_lists:
            print(tier_list)
    finally:
        # Ensure the session is closed
        db.close()

if __name__ == "__main__":
    test_get_tier_lists()
