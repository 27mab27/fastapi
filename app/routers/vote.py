from typing import List, Optional
from fastapi import Depends, FastAPI, Response,status, HTTPException, APIRouter
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from .. import models, schemas, utils,oauth2
from ..database import engine , get_db
router = APIRouter(prefix="/vote", tags=["Vote"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def get_post(vote: schemas.Vote, db: Session = Depends(get_db), cureent_user : int =Depends(oauth2.get_cureent_user)):
    post = db.query(models.Post).filter(vote.post_id==models.Post.id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {vote.post_id} does not exsit")
    vote_query= db.query(models.Vote).filter(models.Vote.post_id==vote.post_id, models.Vote.user_id== cureent_user.id)
    found_vote =vote_query.first()
    if (vote.dir==1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user {cureent_user.id} has alrdy vote on pos {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=cureent_user.id)
        db.add(new_vote)
        db.commit()
        return { "massege":"sucsees"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vote doe not exsits")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return { "massege":"sucsees"}