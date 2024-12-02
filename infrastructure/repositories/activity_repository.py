from sqlalchemy.orm import Session
from typing import List
from domain.models.activity import Activity

class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Activity]:
        return self.db.query(Activity).all()

    def save(self, activity: Activity) -> Activity:
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def save_many(self, activities: List[Activity]):
        self.db.add_all(activities)
        self.db.commit()

    def get_by_type(self, activity_type: str) -> List[Activity]:
        return self.db.query(Activity).filter(Activity.activity_type == activity_type).all() 