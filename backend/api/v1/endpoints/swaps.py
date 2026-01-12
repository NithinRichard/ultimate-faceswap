from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas, auth, models
from database import get_db
from celery_app import celery_app

router = APIRouter()

@router.post("/", response_model=schemas.SwapTask)
def create_swap(
    task: schemas.SwapTaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check gem balance
    cost = 1 if task.type == models.TaskType.IMAGE else 10
    if current_user.gem_balance < cost:
        raise HTTPException(status_code=402, detail="Insufficient gems")

    # Deduct gems
    crud.update_user_gems(db, current_user.id, -cost)

    # Create task
    db_task = crud.create_swap_task(db, current_user.id, task, cost)

    # Trigger Celery task
    celery_app.send_task("process_swap_task", args=[db_task.id])

    return db_task

@router.get("/history", response_model=list[schemas.SwapTask])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_tasks(db, current_user.id)
