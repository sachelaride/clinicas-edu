from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession # Changed from Session
from typing import List
from uuid import UUID

from app.schemas.responsavel import ResponsavelCreate, ResponsavelUpdate, ResponsavelInDB
from app.crud import responsaveis as crud_responsaveis
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=ResponsavelInDB, status_code=status.HTTP_201_CREATED)
async def create_responsavel(responsavel: ResponsavelCreate, db: AsyncSession = Depends(get_db)):
    return await crud_responsaveis.create_responsavel(db=db, responsavel=responsavel)

@router.get("/{responsavel_id}", response_model=ResponsavelInDB)
async def read_responsavel(responsavel_id: UUID, db: AsyncSession = Depends(get_db)):
    db_responsavel = await crud_responsaveis.get_responsavel(db=db, responsavel_id=responsavel_id)
    if db_responsavel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsavel not found")
    return db_responsavel

@router.get("/", response_model=List[ResponsavelInDB])
async def read_responsaveis(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    responsaveis = await crud_responsaveis.get_responsaveis(db=db, skip=skip, limit=limit)
    return responsaveis

@router.put("/{responsavel_id}", response_model=ResponsavelInDB)
async def update_responsavel(responsavel_id: UUID, responsavel: ResponsavelUpdate, db: AsyncSession = Depends(get_db)):
    db_responsavel = await crud_responsaveis.update_responsavel(db=db, responsavel_id=responsavel_id, responsavel=responsavel)
    if db_responsavel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsavel not found")
    return db_responsavel

@router.delete("/{responsavel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_responsavel(responsavel_id: UUID, db: AsyncSession = Depends(get_db)):
    db_responsavel = await crud_responsaveis.delete_responsavel(db=db, responsavel_id=responsavel_id)
    if db_responsavel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsavel not found")
    return {"message": "Responsavel deleted successfully"}