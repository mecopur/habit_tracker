from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# initialize db engine
Base = declarative_base()
engine = create_engine("sqlite:///Habit_Tracker.db")

# configure job scheduler
job_stores = {
    'default': SQLAlchemyJobStore(url='sqlite:///Habit_Tracker.db')
}

job_defaults = {
    'coalesce': True,
    'max_instances': 4,
}

update_scheduler = BackgroundScheduler(jobstores=job_stores, job_defaults=job_defaults)