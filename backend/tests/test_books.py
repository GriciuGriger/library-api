import pytest
from httpx import AsyncClient
from datetime import datetime

from app.models import Book


@pytest.mark.asyncio
async def test_get_books_empty(client: AsyncClient):
    """Test getting all books when database is empty"""
    response = await client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_books_with_data(client: AsyncClient, sample_book):
    """Test getting all books when books exist"""
    response = await client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["serial"] == "123456"
    assert data[0]["title"] == "Test Book"
    assert data[0]["author"] == "Test Author"
    assert data[0]["is_borrowed"] is False


@pytest.mark.asyncio
async def test_create_book_success(client: AsyncClient):
    """Test creating a new book successfully"""
    book_data = {
        "serial": "111111",
        "title": "New Book",
        "author": "New Author"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["serial"] == "111111"
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"
    assert data["is_borrowed"] is False
    assert data["borrowed_by"] is None
    assert data["borrowed_at"] is None


@pytest.mark.asyncio
async def test_create_book_duplicate_serial(client: AsyncClient, sample_book):
    """Test creating a book with duplicate serial number"""
    book_data = {
        "serial": "123456",
        "title": "Another Book",
        "author": "Another Author"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_book_invalid_serial_too_short(client: AsyncClient):
    """Test creating a book with serial number too short"""
    book_data = {
        "serial": "12345",
        "title": "Test",
        "author": "Test"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_invalid_serial_not_numeric(client: AsyncClient):
    """Test creating a book with non-numeric serial"""
    book_data = {
        "serial": "abc123",
        "title": "Test",
        "author": "Test"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_missing_fields(client: AsyncClient):
    """Test creating a book with missing required fields"""
    book_data = {
        "serial": "123456"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_book_success(client: AsyncClient, sample_book):
    """Test deleting a book successfully"""
    response = await client.delete("/books/123456")
    assert response.status_code == 204
    
    # Verify book is deleted
    get_response = await client.get("/books/")
    assert len(get_response.json()) == 0


@pytest.mark.asyncio
async def test_delete_book_not_found(client: AsyncClient):
    """Test deleting a non-existent book"""
    response = await client.delete("/books/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_borrow_book_success(client: AsyncClient, sample_book):
    """Test borrowing a book successfully"""
    loan_data = {
        "action": "borrow",
        "card_number": "654321"
    }
    response = await client.patch("/books/123456/loan", json=loan_data)
    assert response.status_code == 200
    data = response.json()
    assert data["is_borrowed"] is True
    assert data["borrowed_by"] == "654321"
    assert data["borrowed_at"] is not None


@pytest.mark.asyncio
async def test_borrow_book_already_borrowed(client: AsyncClient, sample_book):
    """Test borrowing an already borrowed book"""
    # First borrow
    loan_data = {
        "action": "borrow",
        "card_number": "111111"
    }
    await client.patch("/books/123456/loan", json=loan_data)
    
    # Try to borrow again
    loan_data2 = {
        "action": "borrow",
        "card_number": "222222"
    }
    response = await client.patch("/books/123456/loan", json=loan_data2)
    assert response.status_code == 409
    assert "already borrowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_borrow_book_not_found(client: AsyncClient):
    """Test borrowing a non-existent book"""
    loan_data = {
        "action": "borrow",
        "card_number": "654321"
    }
    response = await client.patch("/books/999999/loan", json=loan_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_borrow_book_missing_card_number(client: AsyncClient, sample_book):
    """Test borrowing without card number"""
    loan_data = {
        "action": "borrow"
    }
    response = await client.patch("/books/123456/loan", json=loan_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_return_book_success(client: AsyncClient, sample_book):
    """Test returning a borrowed book successfully"""
    # First borrow
    loan_data_borrow = {
        "action": "borrow",
        "card_number": "654321"
    }
    await client.patch("/books/123456/loan", json=loan_data_borrow)
    
    # Then return
    loan_data_return = {
        "action": "return"
    }
    response = await client.patch("/books/123456/loan", json=loan_data_return)
    assert response.status_code == 200
    data = response.json()
    assert data["is_borrowed"] is False
    assert data["borrowed_by"] is None
    assert data["borrowed_at"] is None


@pytest.mark.asyncio
async def test_return_book_not_borrowed(client: AsyncClient, sample_book):
    """Test returning a book that is not borrowed"""
    loan_data = {
        "action": "return"
    }
    response = await client.patch("/books/123456/loan", json=loan_data)
    assert response.status_code == 409
    assert "not currently borrowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_return_book_not_found(client: AsyncClient):
    """Test returning a non-existent book"""
    loan_data = {
        "action": "return"
    }
    response = await client.patch("/books/999999/loan", json=loan_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_return_book_with_card_number(client: AsyncClient, sample_book):
    """Test returning a book with card_number (should fail validation)"""
    # First borrow
    loan_data_borrow = {
        "action": "borrow",
        "card_number": "654321"
    }
    await client.patch("/books/123456/loan", json=loan_data_borrow)
    
    # Try to return with card_number (should fail)
    loan_data_return = {
        "action": "return",
        "card_number": "654321"
    }
    response = await client.patch("/books/123456/loan", json=loan_data_return)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_loan_invalid_action(client: AsyncClient, sample_book):
    """Test loan with invalid action"""
    loan_data = {
        "action": "invalid_action"
    }
    response = await client.patch("/books/123456/loan", json=loan_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_loan_invalid_card_number_format(client: AsyncClient, sample_book):
    """Test borrowing with invalid card number format"""
    loan_data = {
        "action": "borrow",
        "card_number": "12345"  # Too short
    }
    response = await client.patch("/books/123456/loan", json=loan_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_full_workflow(client: AsyncClient):
    """Test complete workflow: create, borrow, return, delete"""
    # Create book
    book_data = {
        "serial": "999999",
        "title": "Workflow Book",
        "author": "Workflow Author"
    }
    create_response = await client.post("/books/", json=book_data)
    assert create_response.status_code == 201
    
    # Get all books
    get_response = await client.get("/books/")
    assert len(get_response.json()) == 1
    
    # Borrow book
    borrow_data = {
        "action": "borrow",
        "card_number": "888888"
    }
    borrow_response = await client.patch("/books/999999/loan", json=borrow_data)
    assert borrow_response.status_code == 200
    assert borrow_response.json()["is_borrowed"] is True
    
    # Return book
    return_data = {
        "action": "return"
    }
    return_response = await client.patch("/books/999999/loan", json=return_data)
    assert return_response.status_code == 200
    assert return_response.json()["is_borrowed"] is False
    
    # Delete book
    delete_response = await client.delete("/books/999999")
    assert delete_response.status_code == 204
    
    # Verify deleted
    final_get_response = await client.get("/books/")
    assert len(final_get_response.json()) == 0

