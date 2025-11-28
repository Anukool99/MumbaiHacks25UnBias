from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.db import supabase
from app.models.article import ArticleCreate, ArticleResponse

router = APIRouter()


@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article: ArticleCreate):
    """
    Create a new article.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    try:
        # Insert article into Supabase
        result = supabase.table("articles").insert({
            "title": article.title,
            "content": article.content,
            "author": article.author
        }).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create article"
            )
        
        return ArticleResponse(**result.data[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating article: {str(e)}"
        )


@router.get("/articles", response_model=List[ArticleResponse])
async def list_articles():
    """
    Get all articles.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    try:
        # Fetch all articles from Supabase, ordered by created_at descending
        result = supabase.table("articles").select("*").order("created_at", desc=True).execute()
        
        return [ArticleResponse(**article) for article in result.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching articles: {str(e)}"
        )


@router.get("/articles/{id}", response_model=ArticleResponse)
async def get_article(id: UUID):
    """
    Get a specific article by ID.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    try:
        # Fetch article by ID from Supabase
        result = supabase.table("articles").select("*").eq("id", str(id)).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id {id} not found"
            )
        
        return ArticleResponse(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching article: {str(e)}"
        )


@router.delete("/articles/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(id: UUID):
    """
    Delete an article by ID.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    try:
        # First check if article exists
        check_result = supabase.table("articles").select("id").eq("id", str(id)).execute()
        
        if not check_result.data or len(check_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id {id} not found"
            )
        
        # Delete article from Supabase
        supabase.table("articles").delete().eq("id", str(id)).execute()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting article: {str(e)}"
        )

