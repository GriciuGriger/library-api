from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.db import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, LoanRequest

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[BookResponse])
async def get_books(db: AsyncSession = Depends(get_db)):
    """Get all books"""
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return books


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    """Create a new book"""
    # Check if book with this serial already exists
    result = await db.execute(select(Book).where(Book.serial == book.serial))
    existing_book = result.scalar_one_or_none()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with serial number {book.serial} already exists"
        )
    
    # Create new book
    db_book = Book(
        serial=book.serial,
        title=book.title,
        author=book.author,
        is_borrowed=False,
        borrowed_by=None,
        borrowed_at=None
    )
    
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    
    return db_book


@router.delete("/{serial}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(serial: str, db: AsyncSession = Depends(get_db)):
    """Delete a book by serial number"""
    result = await db.execute(select(Book).where(Book.serial == serial))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with serial number {serial} not found"
        )
    
    await db.delete(book)
    await db.commit()
    
    return None


@router.patch("/{serial}/loan", response_model=BookResponse)
async def update_loan_status(
    serial: str,
    loan_request: LoanRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update book loan status (borrow/return)"""
    # Get book by serial
    result = await db.execute(select(Book).where(Book.serial == serial))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with serial number {serial} not found"
        )
    
    # Handle borrow action
    if loan_request.action == "borrow":
        if book.is_borrowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with serial number {serial} is already borrowed"
            )
        
        book.is_borrowed = True
        book.borrowed_by = loan_request.card_number
        book.borrowed_at = datetime.utcnow()
    
    # Handle return action
    elif loan_request.action == "return":
        if not book.is_borrowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with serial number {serial} is not currently borrowed"
            )
        
        book.is_borrowed = False
        book.borrowed_by = None
        book.borrowed_at = None
    
    await db.commit()
    await db.refresh(book)
    
    return book
