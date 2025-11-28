from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.db import supabase
from app.models.article import ArticleCreate, ArticleResponse

router = APIRouter()


@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article: ArticleCreate):
    print("➡️ [CREATE] Incoming article payload:", article.dict())

    if not supabase:
        print("❌ [CREATE] Supabase client is None")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection not available")
    
    try:
        print("🔄 [CREATE] Inserting into Supabase...")
        result = supabase.table("articles").insert({
            "title": article.title,
            "content": article.content,
            "author": article.author
        }).execute()
        print("🟢 [CREATE] Insert result:", result)

        if not result.data:
            print("❌ [CREATE] Insert returned empty data")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create article")
        
        print("✅ [CREATE] Returning created article")
        return ArticleResponse(**result.data[0])
    except Exception as e:
        print("💥 [CREATE] Error:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating article: {e}")


@router.get("/articles", response_model=List[ArticleResponse])
async def list_articles():
    print("➡️ [LIST] Request to get all articles")

    if not supabase:
        print("❌ [LIST] Supabase client is None")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection not available")

    try:
        print("🔄 [LIST] Fetching from Supabase...")
        result = supabase.table("articles").select("*").order("created_at", desc=True).execute()
        print("🟢 [LIST] Fetch result:", result)

        return [ArticleResponse(**article) for article in result.data]
    except Exception as e:
        print("💥 [LIST] Error:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching articles: {e}")


@router.get("/articles/{id}", response_model=ArticleResponse)
async def get_article(id: UUID):
    print(f"➡️ [GET] Fetch request for article id: {id}")

    if not supabase:
        print("❌ [GET] Supabase client is None")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection not available")
    
    try:
        print("🔄 [GET] Querying Supabase...")
        result = supabase.table("articles").select("*").eq("id", str(id)).execute()
        print("🟢 [GET] Query result:", result)

        if not result.data:
            print(f"⚠️ [GET] No article found for: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article with id {id} not found")

        print("✅ [GET] Returning fetched article")
        return ArticleResponse(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        print("💥 [GET] Error:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching article: {e}")


@router.delete("/articles/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(id: UUID):
    print(f"➡️ [DELETE] Request to delete article id: {id}")

    if not supabase:
        print("❌ [DELETE] Supabase client is None")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection not available")
    
    try:
        print("🔍 [DELETE] Checking if article exists...")
        check_result = supabase.table("articles").select("id").eq("id", str(id)).execute()
        print("🟢 [DELETE] Check result:", check_result)

        if not check_result.data:
            print(f"⚠️ [DELETE] Article not found for id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article with id {id} not found")

        print("🔄 [DELETE] Deleting from Supabase...")
        delete_result = supabase.table("articles").delete().eq("id", str(id)).execute()
        print("🟢 [DELETE] Delete result:", delete_result)

        print("✅ [DELETE] Article deleted successfully")
        return None
    except HTTPException:
        raise
    except Exception as e:
        print("💥 [DELETE] Error:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting article: {e}")
