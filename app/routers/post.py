from typing import List, Optional
from fastapi import Depends, FastAPI, Response,status, HTTPException, APIRouter
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, utils,oauth2
from ..database import engine , get_db

router =APIRouter(prefix= "/posts", tags= [ "posts"])
@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user),limit : int = 10 , skip : int =0, search : Optional[str] =""):
    # cursor.execute("""SELECT * FROM posts""")
    # post = cursor.fetchall()
    post= db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id,  isouter=True).group_by(models.Post.id).all()

    return result

@router.get("/{id}",response_model=schemas.PostOut)
def get_postID(id : int, db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user) ):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post= cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id,  isouter=True).group_by(models.Post.id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"the post with id {id} not found")
        #responses.status_code=status.HTTP_404_NOT_FOUND
        #return {"massege": f"the post with id {id} not found"}

    return post
@router.post("/",response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def get_post(post: schemas.PostCreate, db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title,post.content,post.published))
    # new_post=cursor.fetchone()
    # conn.commit()
    new_post= models.Post(owner_id=cureent_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post




@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # delete_post=cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"id {id} not found")
    if post.owner_id != cureent_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"not allowed")
    post.delete(synchronize_session = False)
    db.commit()
    return {Response(status_code=status.HTTP_204_NO_CONTENT)}

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int,post:schemas.PostCreate,db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user)):
    # cursor.execute("""UPDATE posts SET title = %s , content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    # updated_post=cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    updated_post=post_query.first()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"id {id} not found")

    if post.owner_id != cureent_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"not allowed")
    post_query.update(post.dict(),synchronize_session = False)
    db.commit()
    return updated_post
