from sqlalchemy.orm import Session
import models, schemas
from models import TaskStatus, TaskType

def get_user_by_clerk_id(db: Session, clerk_id: str):
    return db.query(models.User).filter(models.User.clerk_id == clerk_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        clerk_id=user.clerk_id,
        email=user.email,
        gem_balance=5 # Default free gems
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_gems(db: Session, user_id: int, amount: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.gem_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def create_swap_task(db: Session, user_id: int, task: schemas.SwapTaskCreate, cost: int):
    db_task = models.SwapTask(
        user_id=user_id,
        type=task.type,
        cost=cost,
        source_url=task.source_url,
        template_url=task.template_url,
        status=TaskStatus.PENDING
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: int, status: TaskStatus, result_url: str = None, error_message: str = None):
    db_task = db.query(models.SwapTask).filter(models.SwapTask.id == task_id).first()
    if db_task:
        db_task.status = status
        if result_url:
            db_task.result_url = result_url
        if error_message:
            db_task.error_message = error_message
        db.commit()
        db.refresh(db_task)
    return db_task

def get_user_tasks(db: Session, user_id: int):
    return db.query(models.SwapTask).filter(models.SwapTask.user_id == user_id).all()

def get_swap_task(db: Session, task_id: int):
    return db.query(models.SwapTask).filter(models.SwapTask.id == task_id).first()

def get_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Template).offset(skip).limit(limit).all()

def get_template(db: Session, template_id: int):
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def create_template(db: Session, template: schemas.TemplateCreate):
    # Ensure type is Enum
    task_type = models.TaskType[template.type.upper()]
    db_template = models.Template(
        title=template.title,
        type=task_type,
        thumbnail=template.thumbnail,
        source_url=template.source_url or template.thumbnail, # Fallback to thumbnail if no source provided (e.g. images)
        cost=template.cost
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template
