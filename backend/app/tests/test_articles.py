import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_supabase():
    """Fixture to mock Supabase client."""
    with patch('app.api.articles.supabase') as mock_supabase:
        yield mock_supabase


@pytest.fixture
def sample_article_data():
    """Fixture providing sample article data."""
    article_id = uuid4()
    return {
        "id": str(article_id),
        "title": "Test Article",
        "content": "This is a test article content.",
        "author": "Test Author",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_article_list():
    """Fixture providing a list of sample articles."""
    article_id_1 = uuid4()
    article_id_2 = uuid4()
    return [
        {
            "id": str(article_id_1),
            "title": "First Article",
            "content": "Content of first article.",
            "author": "Author One",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(article_id_2),
            "title": "Second Article",
            "content": "Content of second article.",
            "author": "Author Two",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]


class TestCreateArticle:
    """Test cases for POST /api/articles endpoint."""
    
    def test_create_article_success(self, mock_supabase, sample_article_data):
        """Test successful article creation."""
        # Mock Supabase insert response
        mock_response = Mock()
        mock_response.data = [sample_article_data]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Make request
        response = client.post(
            "/api/articles",
            json={
                "title": sample_article_data["title"],
                "content": sample_article_data["content"],
                "author": sample_article_data["author"]
            }
        )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_article_data["title"]
        assert data["content"] == sample_article_data["content"]
        assert data["author"] == sample_article_data["author"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_article_without_author(self, mock_supabase, sample_article_data):
        """Test article creation without author field."""
        sample_article_data["author"] = None
        mock_response = Mock()
        mock_response.data = [sample_article_data]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        response = client.post(
            "/api/articles",
            json={
                "title": sample_article_data["title"],
                "content": sample_article_data["content"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_article_data["title"]
        assert data["author"] is None
    
    def test_create_article_missing_title(self, mock_supabase):
        """Test article creation with missing title."""
        response = client.post(
            "/api/articles",
            json={
                "content": "Some content"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_article_missing_content(self, mock_supabase):
        """Test article creation with missing content."""
        response = client.post(
            "/api/articles",
            json={
                "title": "Some title"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_article_empty_title(self, mock_supabase):
        """Test article creation with empty title."""
        response = client.post(
            "/api/articles",
            json={
                "title": "",
                "content": "Some content"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.articles.supabase', None)
    def test_create_article_no_database(self):
        """Test article creation when database is not available."""
        response = client.post(
            "/api/articles",
            json={
                "title": "Test",
                "content": "Content"
            }
        )
        
        assert response.status_code == 503


class TestListArticles:
    """Test cases for GET /api/articles endpoint."""
    
    def test_list_articles_success(self, mock_supabase, sample_article_list):
        """Test successful retrieval of all articles."""
        # Mock Supabase select response
        mock_response = Mock()
        mock_response.data = sample_article_list
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        # Make request
        response = client.get("/api/articles")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == sample_article_list[0]["title"]
        assert data[1]["title"] == sample_article_list[1]["title"]
    
    def test_list_articles_empty(self, mock_supabase):
        """Test listing articles when there are no articles."""
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        response = client.get("/api/articles")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('app.api.articles.supabase', None)
    def test_list_articles_no_database(self):
        """Test listing articles when database is not available."""
        response = client.get("/api/articles")
        
        assert response.status_code == 503


class TestGetArticle:
    """Test cases for GET /api/articles/{id} endpoint."""
    
    def test_get_article_success(self, mock_supabase, sample_article_data):
        """Test successful retrieval of a specific article."""
        article_id = sample_article_data["id"]
        
        # Mock Supabase select response
        mock_response = Mock()
        mock_response.data = [sample_article_data]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request
        response = client.get(f"/api/articles/{article_id}")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == sample_article_data["title"]
        assert data["content"] == sample_article_data["content"]
    
    def test_get_article_not_found(self, mock_supabase):
        """Test retrieval of non-existent article."""
        article_id = uuid4()
        
        # Mock Supabase select response with empty data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request
        response = client.get(f"/api/articles/{article_id}")
        
        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_article_invalid_uuid(self, mock_supabase):
        """Test retrieval with invalid UUID format."""
        response = client.get("/api/articles/invalid-uuid")
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.articles.supabase', None)
    def test_get_article_no_database(self):
        """Test getting article when database is not available."""
        article_id = uuid4()
        response = client.get(f"/api/articles/{article_id}")
        
        assert response.status_code == 503


class TestDeleteArticle:
    """Test cases for DELETE /api/articles/{id} endpoint."""
    
    def test_delete_article_success(self, mock_supabase, sample_article_data):
        """Test successful deletion of an article."""
        article_id = sample_article_data["id"]
        
        # Mock Supabase responses
        # First call for existence check
        check_response = Mock()
        check_response.data = [{"id": article_id}]
        # Second call for delete
        delete_response = Mock()
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.execute.return_value = check_response
        mock_table.delete.return_value.eq.return_value.execute.return_value = delete_response
        mock_supabase.table.return_value = mock_table
        
        # Make request
        response = client.delete(f"/api/articles/{article_id}")
        
        # Assertions
        assert response.status_code == 204
    
    def test_delete_article_not_found(self, mock_supabase):
        """Test deletion of non-existent article."""
        article_id = uuid4()
        
        # Mock Supabase select response with empty data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request
        response = client.delete(f"/api/articles/{article_id}")
        
        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_article_invalid_uuid(self, mock_supabase):
        """Test deletion with invalid UUID format."""
        response = client.delete("/api/articles/invalid-uuid")
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.articles.supabase', None)
    def test_delete_article_no_database(self):
        """Test deleting article when database is not available."""
        article_id = uuid4()
        response = client.delete(f"/api/articles/{article_id}")
        
        assert response.status_code == 503

