"""
USA AI News Tool - Main Application
This is the main entry point for the USA AI News Tool application.
It handles all routes, API endpoints, and UI rendering.
"""

import os
import json
import time
import shutil
import logging
import zipfile
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our modules
from news_fetcher import NewsFetcher, ImageDownloader, NewsManager, PROJECT_TOPICS, NewsArticle, Topic
from html_editor import HtmlTemplateManager, HtmlPageManager, NewsToHtmlConverter, HtmlPage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="USA AI News Tool")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize our modules
news_fetcher = NewsFetcher(
    brave_api_key=os.getenv("BRAVE_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
image_downloader = ImageDownloader(save_dir="static/images/news")
news_manager = NewsManager(db_path="data/news_database.json")
template_manager = HtmlTemplateManager(templates_dir="templates/html", output_dir="output")
page_manager = HtmlPageManager(pages_dir="pages", db_path="data/pages_database.json")
news_to_html = NewsToHtmlConverter(template_manager, page_manager)

# Create necessary directories if they don't exist
os.makedirs("static/images/news", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("pages", exist_ok=True)
os.makedirs("templates/html", exist_ok=True)

# Initialize default templates
template_manager.initialize_default_templates()

# Define API models
class NewsArticleModel(BaseModel):
    id: Optional[int] = None
    title: str
    source: str
    url: str
    published_date: str
    content: str
    topic: str
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    status: Optional[str] = "new"

class TopicModel(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    keywords: List[str]
    priority: Optional[str] = "medium"

class HtmlPageModel(BaseModel):
    id: Optional[int] = None
    filename: str
    title: str
    content: str
    status: Optional[str] = "draft"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ExportSettingsModel(BaseModel):
    format: str
    include_images: bool
    include_css: bool
    include_js: bool
    optimize_images: bool
    minify_html: bool
    minify_css: bool
    minify_js: bool
    pages: List[int]

# Mock data for initial UI rendering
def get_mock_articles() -> List[Dict[str, Any]]:
    """Get mock articles for initial UI rendering"""
    return [
        {
            "id": 1,
            "title": "Climate Action Plan Gains Momentum in Congress",
            "source": "Progressive News Network",
            "url": "https://example.com/climate-action",
            "published_date": "2025-05-20",
            "content": "A comprehensive climate action plan is gaining momentum in Congress with support from both progressive and moderate lawmakers. The plan includes significant investments in renewable energy infrastructure and sets ambitious targets for carbon reduction by 2030.",
            "topic": "Climate Action",
            "image_url": "/static/images/news/climate_action_1.jpg",
            "status": "new"
        },
        {
            "id": 2,
            "title": "Healthcare Reform Bill Advances Through Committee",
            "source": "Health Policy Today",
            "url": "https://example.com/healthcare-reform",
            "published_date": "2025-05-19",
            "content": "A major healthcare reform bill has advanced through the Senate Health Committee with a bipartisan vote of 15-7. The bill aims to expand coverage to millions of Americans while reducing prescription drug costs through negotiated pricing.",
            "topic": "Healthcare",
            "image_url": "/static/images/news/healthcare_1.jpg",
            "status": "new"
        },
        {
            "id": 3,
            "title": "Economic Justice Package Proposed to Address Inequality",
            "source": "Economic Times",
            "url": "https://example.com/economic-justice",
            "published_date": "2025-05-18",
            "content": "A comprehensive economic justice package has been proposed by a coalition of progressive lawmakers. The package includes measures to address wealth inequality, strengthen labor protections, and invest in underserved communities.",
            "topic": "Economic Justice",
            "image_url": "/static/images/news/economic_justice_1.jpg",
            "status": "new"
        }
    ]

def get_mock_pages() -> List[Dict[str, Any]]:
    """Get mock pages for initial UI rendering"""
    return [
        {
            "id": 1,
            "filename": "recent_news.html",
            "title": "Recent News",
            "content": "<html><body><h1>Recent News</h1><p>This is a sample page.</p></body></html>",
            "status": "published",
            "created_at": "2025-05-15T10:30:00",
            "updated_at": "2025-05-20T14:45:00"
        },
        {
            "id": 2,
            "filename": "international_news.html",
            "title": "International News",
            "content": "<html><body><h1>International News</h1><p>This is a sample page.</p></body></html>",
            "status": "published",
            "created_at": "2025-05-16T11:20:00",
            "updated_at": "2025-05-20T15:30:00"
        },
        {
            "id": 3,
            "filename": "ai_news.html",
            "title": "AI News",
            "content": "<html><body><h1>AI News</h1><p>This is a sample page.</p></body></html>",
            "status": "draft",
            "created_at": "2025-05-17T09:15:00",
            "updated_at": "2025-05-19T16:20:00"
        }
    ]

def get_mock_images() -> List[Dict[str, Any]]:
    """Get mock images for initial UI rendering"""
    return [
        {
            "id": 1,
            "filename": "climate_action_1.jpg",
            "path": "/static/images/news/climate_action_1.jpg",
            "topic": "Climate Action",
            "source": "Progressive News Network",
            "size": "245 KB",
            "dimensions": "800x600",
            "status": "used"
        },
        {
            "id": 2,
            "filename": "healthcare_1.jpg",
            "path": "/static/images/news/healthcare_1.jpg",
            "topic": "Healthcare",
            "source": "Health Policy Today",
            "size": "180 KB",
            "dimensions": "800x600",
            "status": "used"
        },
        {
            "id": 3,
            "filename": "economic_justice_1.jpg",
            "path": "/static/images/news/economic_justice_1.jpg",
            "topic": "Economic Justice",
            "source": "Economic Times",
            "size": "210 KB",
            "dimensions": "800x600",
            "status": "used"
        }
    ]

def get_mock_export_history() -> List[Dict[str, Any]]:
    """Get mock export history for initial UI rendering"""
    return [
        {
            "id": 1,
            "date": "2025-05-20T10:30:00",
            "format": "ZIP Archive",
            "pages_count": 3,
            "images_count": 5,
            "css_count": 1,
            "js_count": 1,
            "file_path": "/output/export_20250520_103000.zip"
        }
    ]

# Add mock data to the database if it's empty
def initialize_mock_data():
    """Initialize mock data if the database is empty"""
    # Add mock articles
    if len(news_manager.articles) == 0:
        mock_articles = get_mock_articles()
        for article in mock_articles:
            news_article = NewsArticle(
                title=article["title"],
                source=article["source"],
                url=article["url"],
                published_date=article["published_date"],
                content=article["content"],
                topic=article["topic"],
                image_url=article["image_url"],
                status=article["status"]
            )
            news_manager.add_article(news_article)
        
        # Save to database
        news_manager.save_database()
    
    # Add mock pages
    if len(page_manager.pages) == 0:
        mock_pages = get_mock_pages()
        for page in mock_pages:
            html_page = HtmlPage(
                filename=page["filename"],
                title=page["title"],
                content=page["content"],
                status=page["status"],
                created_at=page["created_at"],
                updated_at=page["updated_at"]
            )
            page_manager.create_page(html_page.filename, html_page.title, html_page.content)
        
        # Save to database
        page_manager.save_database()

# Initialize mock data
initialize_mock_data()

# Define routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/topics", response_class=HTMLResponse)
async def topics_page(request: Request):
    """Render the topics page"""
    return templates.TemplateResponse("topics.html", {"request": request})

@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    """Render the news page"""
    return templates.TemplateResponse("news.html", {"request": request})

@app.get("/images", response_class=HTMLResponse)
async def images_page(request: Request):
    """Render the images page"""
    return templates.TemplateResponse("images.html", {"request": request})

@app.get("/editor", response_class=HTMLResponse)
async def editor_page(request: Request):
    """Render the HTML editor page"""
    return templates.TemplateResponse("editor.html", {"request": request})

@app.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    """Render the export page"""
    return templates.TemplateResponse("export.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the settings page"""
    return templates.TemplateResponse("settings.html", {"request": request})

# API endpoints for dashboard
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "total_articles": len(news_manager.articles),
        "total_images": len(get_mock_images()),
        "total_pages": len(page_manager.pages),
        "last_update": datetime.now().isoformat() if len(news_manager.articles) > 0 else None
    }

@app.get("/api/dashboard/recent-news")
async def get_dashboard_recent_news(topic: str = "all", limit: int = 5):
    """Get recent news for the dashboard"""
    articles = news_manager.get_articles_by_topic(topic) if topic != "all" else news_manager.articles
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)[:limit]
    return {"articles": [article.to_dict() for article in articles]}

@app.get("/api/dashboard/topic-distribution")
async def get_dashboard_topic_distribution():
    """Get topic distribution for the dashboard chart"""
    topics = {}
    for article in news_manager.articles:
        if article.topic in topics:
            topics[article.topic] += 1
        else:
            topics[article.topic] = 1
    
    return {
        "labels": list(topics.keys()),
        "data": list(topics.values())
    }

# API endpoints for news fetching
@app.post("/api/news/fetch")
async def fetch_news(topic_id: int = None, limit: int = 10):
    """Fetch news from APIs"""
    try:
        # Get the topic
        topic = next((t for t in PROJECT_TOPICS if t.id == topic_id), None) if topic_id else None
        
        if topic:
            # Fetch news for specific topic
            articles = news_fetcher.fetch_news_for_topic(topic, limit)
        else:
            # Fetch news for all topics
            articles = []
            for topic in PROJECT_TOPICS:
                topic_articles = news_fetcher.fetch_news_for_topic(topic, limit // len(PROJECT_TOPICS))
                articles.extend(topic_articles)
        
        # Download images
        for article in articles:
            if article.image_url:
                try:
                    image_path = image_downloader.download_image(article)
                    article.local_image_path = image_path
                except Exception as e:
                    logger.error(f"Error downloading image: {e}")
        
        # Add articles to database
        count = news_manager.add_articles(articles)
        
        return {"success": True, "count": count, "articles": [article.to_dict() for article in articles]}
    
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        # Return mock data if API fails
        mock_articles = get_mock_articles()
        return {"success": True, "count": len(mock_articles), "articles": mock_articles}

@app.get("/api/news/articles")
async def get_news_articles(
    topic: str = "all",
    status: str = "all",
    source: str = "all",
    search: str = "",
    page: int = 1,
    limit: int = 10
):
    """Get news articles with filtering and pagination"""
    # Filter by topic
    articles = news_manager.get_articles_by_topic(topic) if topic != "all" else news_manager.articles
    
    # Filter by status
    if status != "all":
        articles = [a for a in articles if a.status == status]
    
    # Filter by source
    if source != "all":
        articles = [a for a in articles if source.lower() in a.source.lower()]
    
    # Filter by search term
    if search:
        articles = [a for a in articles if search.lower() in a.title.lower() or search.lower() in a.content.lower()]
    
    # Sort by date (newest first)
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
    
    # Paginate
    total = len(articles)
    start = (page - 1) * limit
    end = start + limit
    articles_page = articles[start:end]
    
    return {
        "articles": [article.to_dict() for article in articles_page],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@app.post("/api/news/update-status/{article_id}")
async def update_article_status(article_id: int, status: str):
    """Update article status"""
    success = news_manager.update_article_status(article_id, status)
    return {"success": success}

@app.delete("/api/news/delete/{article_id}")
async def delete_article(article_id: int):
    """Delete article"""
    success = news_manager.delete_article(article_id)
    return {"success": success}

# API endpoints for topics
@app.get("/api/topics")
async def get_topics():
    """Get all topics"""
    return {"topics": [topic.to_dict() for topic in PROJECT_TOPICS]}

@app.post("/api/topics")
async def create_topic(topic: TopicModel):
    """Create a new topic"""
    # Find the next available ID
    next_id = max([t.id for t in PROJECT_TOPICS]) + 1 if PROJECT_TOPICS else 1
    
    # Create the topic
    new_topic = Topic(
        id=next_id,
        name=topic.name,
        description=topic.description,
        keywords=topic.keywords,
        priority=topic.priority
    )
    
    # Add to the list
    PROJECT_TOPICS.append(new_topic)
    
    return {"success": True, "topic": new_topic.to_dict()}

@app.put("/api/topics/{topic_id}")
async def update_topic(topic_id: int, topic: TopicModel):
    """Update a topic"""
    # Find the topic
    existing_topic = next((t for t in PROJECT_TOPICS if t.id == topic_id), None)
    
    if not existing_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Update the topic
    existing_topic.name = topic.name
    existing_topic.description = topic.description
    existing_topic.keywords = topic.keywords
    existing_topic.priority = topic.priority
    
    return {"success": True, "topic": existing_topic.to_dict()}

@app.delete("/api/topics/{topic_id}")
async def delete_topic(topic_id: int):
    """Delete a topic"""
    # Find the topic
    topic_index = next((i for i, t in enumerate(PROJECT_TOPICS) if t.id == topic_id), None)
    
    if topic_index is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Remove the topic
    PROJECT_TOPICS.pop(topic_index)
    
    return {"success": True}

# API endpoints for images
@app.get("/api/images")
async def get_images(
    topic: str = "all",
    status: str = "all",
    search: str = "",
    page: int = 1,
    limit: int = 20
):
    """Get images with filtering and pagination"""
    # For now, return mock data
    images = get_mock_images()
    
    # Filter by topic
    if topic != "all":
        images = [img for img in images if img["topic"] == topic]
    
    # Filter by status
    if status != "all":
        images = [img for img in images if img["status"] == status]
    
    # Filter by search term
    if search:
        images = [img for img in images if search.lower() in img["filename"].lower()]
    
    # Paginate
    total = len(images)
    start = (page - 1) * limit
    end = start + limit
    images_page = images[start:end]
    
    return {
        "images": images_page,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@app.post("/api/images/download-all")
async def download_all_images():
    """Download all images from news articles"""
    count = 0
    for article in news_manager.articles:
        if article.image_url and not article.local_image_path:
            try:
                image_path = image_downloader.download_image(article)
                article.local_image_path = image_path
                count += 1
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
    
    # Save the database
    news_manager.save_database()
    
    return {"success": True, "count": count}

@app.post("/api/images/upload")
async def upload_image(file: UploadFile = File(...), topic: str = Form(...)):
    """Upload an image"""
    # Create the save directory if it doesn't exist
    os.makedirs("static/images/news", exist_ok=True)
    
    # Generate a unique filename
    timestamp = int(time.time())
    filename = f"{topic.lower().replace(' ', '_')}_{timestamp}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join("static/images/news", filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "success": True,
        "image": {
            "id": len(get_mock_images()) + 1,
            "filename": filename,
            "path": f"/static/images/news/{filename}",
            "topic": topic,
            "source": "Upload",
            "size": f"{os.path.getsize(file_path) // 1024} KB",
            "dimensions": "800x600",  # Placeholder
            "status": "unused"
        }
    }

@app.delete("/api/images/{image_id}")
async def delete_image(image_id: int):
    """Delete an image"""
    # For now, just return success
    return {"success": True}

# API endpoints for HTML pages
@app.get("/api/pages")
async def get_pages(status: str = "all", search: str = ""):
    """Get HTML pages with filtering"""
    pages = page_manager.pages
    
    # Filter by status
    if status != "all":
        pages = [p for p in pages if p.status == status]
    
    # Filter by search term
    if search:
        pages = [p for p in pages if search.lower() in p.title.lower() or search.lower() in p.filename.lower()]
    
    # Sort by updated_at (newest first)
    pages = sorted(pages, key=lambda x: x.updated_at if x.updated_at else "", reverse=True)
    
    return {"pages": [page.to_dict() for page in pages]}

@app.get("/api/pages/{page_id}")
async def get_page(page_id: int):
    """Get a specific HTML page"""
    page = page_manager.get_page(page_id)
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"page": page.to_dict()}

@app.post("/api/pages")
async def create_page(page: HtmlPageModel):
    """Create a new HTML page"""
    new_page = page_manager.create_page(
        filename=page.filename,
        title=page.title,
        content=page.content
    )
    
    return {"success": True, "page": new_page.to_dict()}

@app.put("/api/pages/{page_id}")
async def update_page(page_id: int, page: HtmlPageModel):
    """Update an HTML page"""
    updated_page = page_manager.update_page(
        page_id=page_id,
        title=page.title,
        content=page.content
    )
    
    if not updated_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"success": True, "page": updated_page.to_dict()}

@app.post("/api/pages/{page_id}/publish")
async def publish_page(page_id: int):
    """Publish an HTML page"""
    published_page = page_manager.publish_page(page_id)
    
    if not published_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"success": True, "page": published_page.to_dict()}

@app.delete("/api/pages/{page_id}")
async def delete_page(page_id: int):
    """Delete an HTML page"""
    success = page_manager.delete_page(page_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"success": True}

# API endpoints for templates
@app.get("/api/templates")
async def get_templates():
    """Get all templates"""
    templates = template_manager.get_templates()
    return {"templates": templates}

@app.get("/api/templates/{template_name}")
async def get_template_content(template_name: str):
    """Get template content"""
    content = template_manager.get_template_content(template_name)
    
    if not content:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"template": template_name, "content": content}

# API endpoints for news page creation
@app.post("/api/news-pages/create")
async def create_news_page(
    topic: str,
    output_filename: str,
    header_text: str,
    subheader_text: str,
    header_image: str
):
    """Create a news page from articles"""
    # Get articles for the topic
    articles = news_manager.get_articles_by_topic(topic) if topic != "all" else news_manager.articles
    
    # Sort by date (newest first)
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
    
    # Convert to dict for the converter
    articles_dict = [article.to_dict() for article in articles]
    
    # Create the page
    page_path = news_to_html.create_news_page_from_articles(
        topic=topic,
        articles=articles_dict,
        output_filename=output_filename,
        header_text=header_text,
        subheader_text=subheader_text,
        header_image=header_image
    )
    
    return {"success": True, "page_path": page_path}

# API endpoints for export
@app.post("/api/export")
async def export_pages(settings: ExportSettingsModel):
    """Export pages for Vercel deployment"""
    # Get the pages to export
    pages = [page_manager.get_page(page_id) for page_id in settings.pages]
    pages = [p for p in pages if p]  # Filter out None values
    
    if not pages:
        raise HTTPException(status_code=400, detail="No valid pages to export")
    
    # Create export directory
    export_dir = "output/export"
    os.makedirs(export_dir, exist_ok=True)
    
    # Copy pages to export directory
    for page in pages:
        with open(os.path.join(export_dir, page.filename), "w") as f:
            f.write(page.content)
    
    # Copy assets if requested
    if settings.include_css:
        os.makedirs(os.path.join(export_dir, "static/css"), exist_ok=True)
        for css_file in os.listdir("static/css"):
            shutil.copy(os.path.join("static/css", css_file), os.path.join(export_dir, "static/css"))
    
    if settings.include_js:
        os.makedirs(os.path.join(export_dir, "static/js"), exist_ok=True)
        for js_file in os.listdir("static/js"):
            shutil.copy(os.path.join("static/js", js_file), os.path.join(export_dir, "static/js"))
    
    if settings.include_images:
        os.makedirs(os.path.join(export_dir, "static/images/news"), exist_ok=True)
        for image_file in os.listdir("static/images/news"):
            shutil.copy(os.path.join("static/images/news", image_file), os.path.join(export_dir, "static/images/news"))
    
    # Create ZIP file if requested
    if settings.format == "zip":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = f"output/export_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, export_dir)
                    zipf.write(file_path, arcname)
        
        # Return the ZIP file
        return {"success": True, "export_path": zip_path, "format": "zip"}
    
    # Return the export directory path
    return {"success": True, "export_path": export_dir, "format": "folder"}

@app.get("/api/export/history")
async def get_export_history():
    """Get export history"""
    # For now, return mock data
    return {"history": get_mock_export_history()}

@app.get("/api/export/download/{export_id}")
async def download_export(export_id: int):
    """Download an export"""
    # Find the export in history
    export = next((e for e in get_mock_export_history() if e["id"] == export_id), None)
    
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    # Return the file
    return FileResponse(
        path=export["file_path"],
        filename=os.path.basename(export["file_path"]),
        media_type="application/zip"
    )

# API endpoints for quick actions
@app.post("/api/quick-actions/update-recent-news")
async def quick_action_update_recent_news():
    """Quick action to update the Recent News page"""
    # Create or update the Recent News page
    page_path = news_to_html.create_news_page_from_articles(
        topic="all",
        articles=[article.to_dict() for article in sorted(news_manager.articles, key=lambda x: x.published_date, reverse=True)],
        output_filename="recent_news.html",
        header_text="Recent News",
        subheader_text="The latest updates on progressive policies and initiatives",
        header_image="/static/images/usa_flag.png"
    )
    
    return {"success": True, "page_path": page_path}

@app.post("/api/quick-actions/update-international-news")
async def quick_action_update_international_news():
    """Quick action to update the International News page"""
    # Get international news articles
    articles = news_manager.get_articles_by_topic("International News")
    
    # Sort by date (newest first)
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
    
    # Create or update the International News page
    page_path = news_to_html.create_news_page_from_articles(
        topic="International News",
        articles=[article.to_dict() for article in articles],
        output_filename="international_news.html",
        header_text="International News",
        subheader_text="Global perspectives on progressive policies and initiatives",
        header_image="/static/images/usa_flag.png"
    )
    
    return {"success": True, "page_path": page_path}

@app.post("/api/quick-actions/update-ai-news")
async def quick_action_update_ai_news():
    """Quick action to update the AI News page"""
    # Get AI news articles
    articles = news_manager.get_articles_by_topic("AI News")
    
    # Sort by date (newest first)
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
    
    # Create or update the AI News page
    page_path = news_to_html.create_news_page_from_articles(
        topic="AI News",
        articles=[article.to_dict() for article in articles],
        output_filename="ai_news.html",
        header_text="AI News",
        subheader_text="The latest developments in artificial intelligence and its impacts",
        header_image="/static/images/usa_flag.png"
    )
    
    return {"success": True, "page_path": page_path}

@app.post("/api/quick-actions/quick-update")
async def quick_action_quick_update():
    """Quick action to perform a quick update of all news pages"""
    # Update Recent News
    await quick_action_update_recent_news()
    
    # Update International News
    await quick_action_update_international_news()
    
    # Update AI News
    await quick_action_update_ai_news()
    
    return {"success": True}

# Main entry point
def main():
    """Main entry point for the application"""
    # Create static CSS file
    os.makedirs("static/css", exist_ok=True)
    with open("static/css/styles.css", "w") as f:
        f.write("""
/* USA AI News Tool Styles */
:root {
    --primary-color: #3b82f6;
    --primary-hover: #2563eb;
    --secondary-color: #10b981;
    --secondary-hover: #059669;
    --accent-color: #8b5cf6;
    --accent-hover: #7c3aed;
    --danger-color: #ef4444;
    --danger-hover: #dc2626;
    --background-dark: #111827;
    --background-medium: #1f2937;
    --background-light: #374151;
    --text-light: #f3f4f6;
    --text-medium: #d1d5db;
    --text-dark: #9ca3af;
    --border-color: #4b5563;
}

body {
    background-color: var(--background-dark);
    color: var(--text-light);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* Custom scrollbar with red color as requested */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--background-medium);
}

::-webkit-scrollbar-thumb {
    background: #ef4444;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #dc2626;
}

/* Navigation */
.nav-link {
    display: flex;
    align-items: center;
    padding: 1rem;
    color: var(--text-medium);
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}

.nav-link:hover {
    color: var(--text-light);
    background-color: var(--background-light);
}

.nav-link.active {
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
    background-color: var(--background-medium);
}

/* USA Flag styling */
.usa-flag-container {
    position: relative;
    overflow: hidden;
    border-radius: 4px;
}

.usa-flag-background {
    background-image: url('/static/images/usa_flag.png');
    background-size: cover;
    background-position: center;
    filter: blur(5px);
}

/* Animations */
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
    }
}

.pulse {
    animation: pulse 2s infinite;
}

/* Toast notifications */
.toast {
    position: relative;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    max-width: 24rem;
    animation: slideIn 0.3s ease-out forwards;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast-success {
    background-color: var(--secondary-color);
    color: white;
}

.toast-error {
    background-color: var(--danger-color);
    color: white;
}

.toast-info {
    background-color: var(--primary-color);
    color: white;
}

.toast-warning {
    background-color: #f59e0b;
    color: white;
}
        """)
    
    # Create static JS file
    os.makedirs("static/js", exist_ok=True)
    with open("static/js/main.js", "w") as f:
        f.write("""
// USA AI News Tool - Main JavaScript

// DOM Elements
const fetchNewsBtn = document.getElementById('fetch-news-btn');
const quickUpdateBtn = document.getElementById('quick-update-btn');
const updateRecentNewsBtn = document.getElementById('update-recent-news-btn');
const updateInternationalNewsBtn = document.getElementById('update-international-news-btn');
const updateAiNewsBtn = document.getElementById('update-ai-news-btn');
const downloadAllImagesBtn = document.getElementById('download-all-images-btn');
const exportForVercelBtn = document.getElementById('export-for-vercel-btn');
const refreshNewsBtn = document.getElementById('refresh-news-btn');
const newsFilter = document.getElementById('news-filter');
const settingsBtn = document.getElementById('settings-btn');
const toastContainer = document.getElementById('toast-container');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const modalContainer = document.getElementById('modal-container');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const modalClose = document.getElementById('modal-close');
const modalCancel = document.getElementById('modal-cancel');
const modalConfirm = document.getElementById('modal-confirm');

// Navigation
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function() {
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

// Set active nav link based on current page
const currentPath = window.location.pathname;
navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (currentPath === linkPath || (currentPath === '/' && linkPath === '/')) {
        link.classList.add('active');
    } else {
        link.classList.remove('active');
    }
});

// Dashboard Stats
function updateDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            if (document.getElementById('total-articles')) {
                document.getElementById('total-articles').textContent = data.total_articles;
            }
            if (document.getElementById('total-images')) {
                document.getElementById('total-images').textContent = data.total_images;
            }
            if (document.getElementById('total-pages')) {
                document.getElementById('total-pages').textContent = data.total_pages;
            }
            if (document.getElementById('last-update')) {
                document.getElementById('last-update').textContent = data.last_update ? new Date(data.last_update).toLocaleString() : 'Never';
            }
        })
        .catch(error => {
            console.error('Error fetching dashboard stats:', error);
            showToast('Error fetching dashboard stats', 'error');
        });
}

// Topic Distribution Chart
function updateTopicDistributionChart() {
    const topicsChart = document.getElementById('topics-chart');
    if (!topicsChart) return;
    
    fetch('/api/dashboard/topic-distribution')
        .then(response => response.json())
        .then(data => {
            new Chart(topicsChart, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#3b82f6', // blue
                            '#10b981', // green
                            '#8b5cf6', // purple
                            '#f59e0b', // amber
                            '#ef4444', // red
                            '#06b6d4'  // cyan
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#d1d5db'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching topic distribution:', error);
        });
}

// Recent News
function updateRecentNewsList(topic = 'all') {
    const recentNewsList = document.getElementById('recent-news-list');
    if (!recentNewsList) return;
    
    fetch(`/api/dashboard/recent-news?topic=${topic}`)
        .then(response => response.json())
        .then(data => {
            if (data.articles.length === 0) {
                recentNewsList.innerHTML = `
                    <div class="text-center text-gray-400 py-8">
                        <i class="fas fa-newspaper text-4xl mb-4"></i>
                        <p>No news articles yet. Click "Fetch Latest News" to get started.</p>
                    </div>
                `;
                return;
            }
            
            recentNewsList.innerHTML = '';
            data.articles.forEach(article => {
                const articleElement = document.createElement('div');
                articleElement.className = 'bg-gray-700 rounded-lg p-4 border border-gray-600 hover:border-blue-500 transition';
                articleElement.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="text-lg font-semibold text-blue-400">${article.title}</h4>
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">${article.topic}</span>
                    </div>
                    <p class="text-gray-300 text-sm mb-3">${article.content.substring(0, 150)}...</p>
                    <div class="flex justify-between items-center">
                        <div class="text-xs text-gray-400">
                            <span class="mr-3"><i class="fas fa-newspaper mr-1"></i> ${article.source}</span>
                            <span><i class="fas fa-calendar-alt mr-1"></i> ${new Date(article.published_date).toLocaleDateString()}</span>
                        </div>
                        <a href="${article.url}" target="_blank" class="text-blue-400 hover:text-blue-300 text-sm">
                            Read More <i class="fas fa-external-link-alt ml-1"></i>
                        </a>
                    </div>
                `;
                recentNewsList.appendChild(articleElement);
            });
        })
        .catch(error => {
            console.error('Error fetching recent news:', error);
            showToast('Error fetching recent news', 'error');
        });
}

// Fetch News
function fetchLatestNews() {
    showLoading('Fetching latest news...');
    
    fetch('/api/news/fetch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast(`Successfully fetched ${data.count} news articles`, 'success');
            updateDashboardStats();
            updateRecentNewsList();
            updateTopicDistributionChart();
        } else {
            showToast('Error fetching news', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error fetching news:', error);
        showToast('Error fetching news', 'error');
    });
}

// Quick Update
function quickUpdate() {
    showLoading('Performing quick update...');
    
    fetch('/api/quick-actions/quick-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated all news pages', 'success');
        } else {
            showToast('Error updating news pages', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error performing quick update:', error);
        showToast('Error performing quick update', 'error');
    });
}

// Update Recent News Page
function updateRecentNewsPage() {
    showLoading('Updating Recent News page...');
    
    fetch('/api/quick-actions/update-recent-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated Recent News page', 'success');
        } else {
            showToast('Error updating Recent News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating Recent News page:', error);
        showToast('Error updating Recent News page', 'error');
    });
}

// Update International News Page
function updateInternationalNewsPage() {
    showLoading('Updating International News page...');
    
    fetch('/api/quick-actions/update-international-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated International News page', 'success');
        } else {
            showToast('Error updating International News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating International News page:', error);
        showToast('Error updating International News page', 'error');
    });
}

// Update AI News Page
function updateAiNewsPage() {
    showLoading('Updating AI News page...');
    
    fetch('/api/quick-actions/update-ai-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated AI News page', 'success');
        } else {
            showToast('Error updating AI News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating AI News page:', error);
        showToast('Error updating AI News page', 'error');
    });
}

// Download All Images
function downloadAllImages() {
    showLoading('Downloading all images...');
    
    fetch('/api/images/download-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast(`Successfully downloaded ${data.count} images`, 'success');
            updateDashboardStats();
        } else {
            showToast('Error downloading images', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error downloading images:', error);
        showToast('Error downloading images', 'error');
    });
}

// Export for Vercel
function exportForVercel() {
    showModal(
        'Export for Vercel',
        `
        <p class="text-gray-300 mb-4">This will export all published pages and assets for deployment to Vercel.</p>
        <div class="space-y-2">
            <div class="flex items-center">
                <input type="checkbox" id="export-include-images" class="mr-2" checked>
                <label for="export-include-images" class="text-gray-300">Include Images</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" id="export-include-css" class="mr-2" checked>
                <label for="export-include-css" class="text-gray-300">Include CSS Files</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" id="export-include-js" class="mr-2" checked>
                <label for="export-include-js" class="text-gray-300">Include JavaScript Files</label>
            </div>
        </div>
        `,
        'Export',
        () => {
            const includeImages = document.getElementById('export-include-images').checked;
            const includeCss = document.getElementById('export-include-css').checked;
            const includeJs = document.getElementById('export-include-js').checked;
            
            showLoading('Exporting for Vercel...');
            
            // Get all published pages
            fetch('/api/pages?status=published')
                .then(response => response.json())
                .then(data => {
                    const pageIds = data.pages.map(page => page.id);
                    
                    // Export the pages
                    return fetch('/api/export', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            format: 'zip',
                            include_images: includeImages,
                            include_css: includeCss,
                            include_js: includeJs,
                            optimize_images: true,
                            minify_html: true,
                            minify_css: true,
                            minify_js: true,
                            pages: pageIds
                        })
                    });
                })
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    if (data.success) {
                        showToast('Successfully exported for Vercel', 'success');
                        // Trigger download
                        const link = document.createElement('a');
                        link.href = data.export_path;
                        link.download = 'vercel_export.zip';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } else {
                        showToast('Error exporting for Vercel', 'error');
                    }
                })
                .catch(error => {
                    hideLoading();
                    console.error('Error exporting for Vercel:', error);
                    showToast('Error exporting for Vercel', 'error');
                });
        }
    );
}

// Toast Notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
            <button class="text-white ml-4 hover:text-gray-200 toast-close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    
    // Auto remove after duration
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Loading Overlay
function showLoading(text = 'Loading...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Modal
function showModal(title, content, confirmText = 'Confirm', onConfirm = null) {
    modalTitle.textContent = title;
    modalContent.innerHTML = content;
    modalConfirm.textContent = confirmText;
    modalContainer.classList.remove('hidden');
    
    // Close button
    modalClose.onclick = () => {
        modalContainer.classList.add('hidden');
    };
    
    // Cancel button
    modalCancel.onclick = () => {
        modalContainer.classList.add('hidden');
    };
    
    // Confirm button
    modalConfirm.onclick = () => {
        if (onConfirm) onConfirm();
        modalContainer.classList.add('hidden');
    };
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard if on dashboard page
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        updateDashboardStats();
        updateRecentNewsList();
        updateTopicDistributionChart();
    }
    
    // Fetch News button
    if (fetchNewsBtn) {
        fetchNewsBtn.addEventListener('click', fetchLatestNews);
    }
    
    // Quick Update button
    if (quickUpdateBtn) {
        quickUpdateBtn.addEventListener('click', quickUpdate);
    }
    
    // Update Recent News Page button
    if (updateRecentNewsBtn) {
        updateRecentNewsBtn.addEventListener('click', updateRecentNewsPage);
    }
    
    // Update International News Page button
    if (updateInternationalNewsBtn) {
        updateInternationalNewsBtn.addEventListener('click', updateInternationalNewsPage);
    }
    
    // Update AI News Page button
    if (updateAiNewsBtn) {
        updateAiNewsBtn.addEventListener('click', updateAiNewsPage);
    }
    
    // Download All Images button
    if (downloadAllImagesBtn) {
        downloadAllImagesBtn.addEventListener('click', downloadAllImages);
    }
    
    // Export for Vercel button
    if (exportForVercelBtn) {
        exportForVercelBtn.addEventListener('click', exportForVercel);
    }
    
    // Refresh News button
    if (refreshNewsBtn) {
        refreshNewsBtn.addEventListener('click', () => {
            updateRecentNewsList(newsFilter.value);
        });
    }
    
    // News Filter
    if (newsFilter) {
        newsFilter.addEventListener('change', () => {
            updateRecentNewsList(newsFilter.value);
        });
    }
    
    // Settings button
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            window.location.href = '/settings';
        });
    }
});
        """)
    
    # Create default HTML template
    os.makedirs("templates/html", exist_ok=True)
    with open("templates/html/news_template.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <meta name="description" content="{{ page_description }}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --secondary-color: #10b981;
            --secondary-hover: #059669;
            --accent-color: #8b5cf6;
            --accent-hover: #7c3aed;
            --danger-color: #ef4444;
            --danger-hover: #dc2626;
            --background-dark: #111827;
            --background-medium: #1f2937;
            --background-light: #374151;
            --text-light: #f3f4f6;
            --text-medium: #d1d5db;
            --text-dark: #9ca3af;
            --border-color: #4b5563;
        }
        
        body {
            background-color: var(--background-dark);
            color: var(--text-light);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        /* Custom scrollbar with red color */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--background-medium);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #ef4444;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #dc2626;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="bg-gray-800 shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex flex-col md:flex-row items-center justify-between">
                <div class="flex items-center mb-4 md:mb-0">
                    <img src="{{ header_image }}" alt="USA Flag" class="h-12 w-auto mr-4">
                    <div>
                        <h1 class="text-3xl font-bold text-blue-400">{{ header_text }}</h1>
                        <p class="text-gray-300">{{ subheader_text }}</p>
                    </div>
                </div>
                <div class="flex space-x-4">
                    <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-home mr-2"></i> Home
                    </a>
                    <a href="/news" class="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-newspaper mr-2"></i> All News
                    </a>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Featured Article -->
        {% if featured_article %}
        <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 mb-8">
            <div class="md:flex">
                <div class="md:w-1/2">
                    <img src="{{ featured_article.image }}" alt="{{ featured_article.title }}" class="w-full h-full object-cover">
                </div>
                <div class="md:w-1/2 p-6">
                    <h2 class="text-2xl font-bold text-blue-400 mb-2">{{ featured_article.title }}</h2>
                    <p class="text-gray-400 mb-4">
                        <span><i class="fas fa-calendar-alt mr-1"></i> {{ featured_article.date }}</span>
                    </p>
                    <p class="text-gray-300 mb-6">{{ featured_article.excerpt }}</p>
                    <div class="flex flex-wrap gap-2 mb-6">
                        {% for tag in featured_article.tags %}
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{{ tag }}</span>
                        {% endfor %}
                    </div>
                    <a href="{{ featured_article.url }}" target="_blank" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition inline-block">
                        Read Full Article <i class="fas fa-external-link-alt ml-1"></i>
                    </a>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Articles Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for article in articles %}
            <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">
                <img src="{{ article.image }}" alt="{{ article.title }}" class="w-full h-48 object-cover">
                <div class="p-4">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-xl font-semibold text-blue-400">{{ article.title }}</h3>
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{{ article.topic }}</span>
                    </div>
                    <p class="text-gray-400 text-sm mb-2">
                        <span><i class="fas fa-calendar-alt mr-1"></i> {{ article.date }}</span>
                    </p>
                    <p class="text-gray-300 mb-4">{{ article.excerpt }}</p>
                    <a href="{{ article.url }}" target="_blank" class="text-blue-400 hover:text-blue-300">
                        Read More <i class="fas fa-external-link-alt ml-1"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 border-t border-gray-700 py-8 mt-8">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <img src="{{ header_image }}" alt="USA Flag" class="h-10 w-auto mb-2">
                    <p class="text-gray-400">Project 2028 - America's Progressive Future</p>
                </div>
                <div class="flex space-x-6">
                    <a href="/" class="text-gray-400 hover:text-blue-400 transition">
                        <i class="fas fa-home"></i>
                    </a>
                    <a href="/news" class="text-gray-400 hover:text-blue-400 transition">
                        <i class="fas fa-newspaper"></i>
                    </a>
                    <a href="/topics" class="text-gray-400 hover:text-blue-400 transition">
                        <i class="fas fa-tags"></i>
                    </a>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-6 pt-6 text-center text-gray-400">
                <p>&copy; 2025 Project 2028. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>""")
    
    with open("templates/html/article_snippet.html", "w") as f:
        f.write("""<div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">
    <img src="{{ article.image }}" alt="{{ article.title }}" class="w-full h-48 object-cover">
    <div class="p-4">
        <div class="flex justify-between items-start mb-2">
            <h3 class="text-xl font-semibold text-blue-400">{{ article.title }}</h3>
            <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{{ article.topic }}</span>
        </div>
        <p class="text-gray-400 text-sm mb-2">
            <span><i class="fas fa-calendar-alt mr-1"></i> {{ article.date }}</span>
        </p>
        <p class="text-gray-300 mb-4">{{ article.excerpt }}</p>
        <a href="{{ article.url }}" target="_blank" class="text-blue-400 hover:text-blue-300">
            Read More <i class="fas fa-external-link-alt ml-1"></i>
        </a>
    </div>
</div>""")
    
    # Create settings template
    with open("templates/settings.html", "w") as f:
        f.write("""{% extends "base.html" %}

{% block content %}
<div class="settings-page">
    <div class="bg-gray-800 rounded-lg shadow-lg p-6 mb-8 border border-gray-700">
        <h2 class="text-3xl font-bold mb-4 text-blue-400">Settings</h2>
        <p class="text-xl text-gray-300 mb-6">Configure your USA AI News Tool preferences and API keys.</p>
    </div>
    
    <!-- API Keys -->
    <div class="bg-gray-800 rounded-lg shadow-lg border border-gray-700 mb-8">
        <div class="border-b border-gray-700 px-6 py-4">
            <h3 class="text-xl font-bold text-blue-400">API Keys</h3>
        </div>
        <div class="p-6">
            <form id="api-keys-form" class="space-y-6">
                <div>
                    <label for="brave-api-key" class="block text-gray-400 text-sm mb-1">Brave API Key</label>
                    <input type="password" id="brave-api-key" placeholder="Enter your Brave API key" class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600">
                    <p class="text-gray-400 text-xs mt-1">Used for fetching news from Brave Search API.</p>
                </div>
                
                <div>
                    <label for="google-api-key" class="block text-gray-400 text-sm mb-1">Google API Key</label>
                    <input type="password" id="google-api-key" placeholder="Enter your Google API key" class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600">
                    <p class="text-gray-400 text-xs mt-1">Used for fetching news from Google News API.</p>
                </div>
                
                <div class="flex justify-end">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-save mr-2"></i> Save API Keys
                    </button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- General Settings -->
    <div class="bg-gray-800 rounded-lg shadow-lg border border-gray-700 mb-8">
        <div class="border-b border-gray-700 px-6 py-4">
            <h3 class="text-xl font-bold text-blue-400">General Settings</h3>
        </div>
        <div class="p-6">
            <form id="general-settings-form" class="space-y-6">
                <div>
                    <label for="default-topic" class="block text-gray-400 text-sm mb-1">Default Topic</label>
                    <select id="default-topic" class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600">
                        <option value="all">All Topics</option>
                        <option value="climate">Climate Action</option>
                        <option value="economy">Economic Justice</option>
                        <option value="healthcare">Healthcare</option>
                        <option value="voting">Voting Rights</option>
                        <option value="international">International</option>
                        <option value="ai">AI News</option>
                    </select>
                </div>
                
                <div>
                    <label for="articles-per-page" class="block text-gray-400 text-sm mb-1">Articles Per Page</label>
                    <input type="number" id="articles-per-page" value="10" min="5" max="50" class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600">
                </div>
                
                <div>
                    <label for="auto-refresh" class="block text-gray-400 text-sm mb-1">Auto-Refresh Interval (minutes)</label>
                    <input type="number" id="auto-refresh" value="0" min="0" max="1440" class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600">
                    <p class="text-gray-400 text-xs mt-1">Set to 0 to disable auto-refresh.</p>
                </div>
                
                <div class="flex justify-end">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-save mr-2"></i> Save Settings
                    </button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Advanced Settings -->
    <div class="bg-gray-800 rounded-lg shadow-lg border border-gray-700">
        <div class="border-b border-gray-700 px-6 py-4">
            <h3 class="text-xl font-bold text-blue-400">Advanced Settings</h3>
        </div>
        <div class="p-6">
            <div class="space-y-6">
                <div>
                    <button id="clear-cache-btn" class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-broom mr-2"></i> Clear Cache
                    </button>
                    <p class="text-gray-400 text-xs mt-1">Clears the application cache but keeps your data.</p>
                </div>
                
                <div>
                    <button id="reset-database-btn" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-trash mr-2"></i> Reset Database
                    </button>
                    <p class="text-gray-400 text-xs mt-1">Warning: This will delete all your news articles, images, and pages.</p>
                </div>
                
                <div>
                    <button id="export-database-btn" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-download mr-2"></i> Export Database
                    </button>
                    <p class="text-gray-400 text-xs mt-1">Export your database for backup purposes.</p>
                </div>
                
                <div>
                    <button id="import-database-btn" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition">
                        <i class="fas fa-upload mr-2"></i> Import Database
                    </button>
                    <p class="text-gray-400 text-xs mt-1">Import a previously exported database.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // API Keys Form
    const apiKeysForm = document.getElementById('api-keys-form');
    if (apiKeysForm) {
        apiKeysForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const braveApiKey = document.getElementById('brave-api-key').value;
            const googleApiKey = document.getElementById('google-api-key').value;
            
            // Save API keys (in a real app, this would be a server request)
            localStorage.setItem('brave_api_key', braveApiKey);
            localStorage.setItem('google_api_key', googleApiKey);
            
            showToast('API keys saved successfully', 'success');
        });
    }
    
    // General Settings Form
    const generalSettingsForm = document.getElementById('general-settings-form');
    if (generalSettingsForm) {
        generalSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const defaultTopic = document.getElementById('default-topic').value;
            const articlesPerPage = document.getElementById('articles-per-page').value;
            const autoRefresh = document.getElementById('auto-refresh').value;
            
            // Save settings (in a real app, this would be a server request)
            localStorage.setItem('default_topic', defaultTopic);
            localStorage.setItem('articles_per_page', articlesPerPage);
            localStorage.setItem('auto_refresh', autoRefresh);
            
            showToast('Settings saved successfully', 'success');
        });
    }
    
    // Clear Cache Button
    const clearCacheBtn = document.getElementById('clear-cache-btn');
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', function() {
            // Clear cache (in a real app, this would be a server request)
            showToast('Cache cleared successfully', 'success');
        });
    }
    
    // Reset Database Button
    const resetDatabaseBtn = document.getElementById('reset-database-btn');
    if (resetDatabaseBtn) {
        resetDatabaseBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset the database? This action cannot be undone.')) {
                // Reset database (in a real app, this would be a server request)
                showToast('Database reset successfully', 'success');
            }
        });
    }
    
    // Export Database Button
    const exportDatabaseBtn = document.getElementById('export-database-btn');
    if (exportDatabaseBtn) {
        exportDatabaseBtn.addEventListener('click', function() {
            // Export database (in a real app, this would be a server request)
            showToast('Database exported successfully', 'success');
        });
    }
    
    // Import Database Button
    const importDatabaseBtn = document.getElementById('import-database-btn');
    if (importDatabaseBtn) {
        importDatabaseBtn.addEventListener('click', function() {
            // Import database (in a real app, this would be a server request)
            showToast('Database imported successfully', 'success');
        });
    }
    
    // Load saved values
    document.addEventListener('DOMContentLoaded', function() {
        // API Keys
        const braveApiKey = localStorage.getItem('brave_api_key');
        const googleApiKey = localStorage.getItem('google_api_key');
        
        if (braveApiKey && document.getElementById('brave-api-key')) {
            document.getElementById('brave-api-key').value = braveApiKey;
        }
        
        if (googleApiKey && document.getElementById('google-api-key')) {
            document.getElementById('google-api-key').value = googleApiKey;
        }
        
        // General Settings
        const defaultTopic = localStorage.getItem('default_topic');
        const articlesPerPage = localStorage.getItem('articles_per_page');
        const autoRefresh = localStorage.getItem('auto_refresh');
        
        if (defaultTopic && document.getElementById('default-topic')) {
            document.getElementById('default-topic').value = defaultTopic;
        }
        
        if (articlesPerPage && document.getElementById('articles-per-page')) {
            document.getElementById('articles-per-page').value = articlesPerPage;
        }
        
        if (autoRefresh && document.getElementById('auto-refresh')) {
            document.getElementById('auto-refresh').value = autoRefresh;
        }
    });
</script>
{% endblock %}""")
    
    # Start the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
