from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import crud, schemas, auth, models
from database import get_db
from celery_app import celery_app
import shutil
import os
import uuid

router = APIRouter()

@router.post("/upload", response_model=dict)
def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Invalid file type. Only images are allowed.")

    # Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"static/uploads/{filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return URL (relative or absolute, relative is easier for now)
    # Assuming the frontend knows where the backend is hosted
    return {"url": f"/static/uploads/{filename}"}

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

@router.get("/{task_id}", response_model=schemas.SwapTask)
def get_swap_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    task = crud.get_swap_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task
