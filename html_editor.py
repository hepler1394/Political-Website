"""
USA AI News Tool - HTML Editor Module
This module handles HTML page creation, editing, and management.
"""

import os
import json
import logging
import shutil
from typing import List, Dict, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HtmlPage:
    """Class representing an HTML page"""
    
    def __init__(
        self,
        filename: str,
        title: str,
        content: str,
        status: str = "draft",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[int] = None
    ):
        """Initialize an HTML page"""
        self.id = id
        self.filename = filename
        self.title = title
        self.content = content
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HtmlPage':
        """Create from dictionary"""
        return cls(
            id=data.get("id"),
            filename=data["filename"],
            title=data["title"],
            content=data["content"],
            status=data.get("status", "draft"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

class HtmlTemplateManager:
    """Class for managing HTML templates"""
    
    def __init__(self, templates_dir: str, output_dir: str):
        """Initialize with directories"""
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        
        # Create directories if they don't exist
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if templates exist, if not, create default templates
        if not os.listdir(templates_dir):
            logger.info("No templates found. Creating default templates.")
            self.initialize_default_templates()
    
    def initialize_default_templates(self):
        """Initialize default templates"""
        # Create news template
        news_template = """<!DOCTYPE html>
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
</html>"""
        
        # Create article snippet template
        article_snippet = """<div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">
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
</div>"""
        
        # Write templates to files
        with open(os.path.join(self.templates_dir, "news_template.html"), "w") as f:
            f.write(news_template)
        
        with open(os.path.join(self.templates_dir, "article_snippet.html"), "w") as f:
            f.write(article_snippet)
    
    def get_templates(self) -> List[str]:
        """Get list of available templates"""
        return [f for f in os.listdir(self.templates_dir) if f.endswith(".html")]
    
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get template content"""
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            return None
        
        with open(template_path, "r") as f:
            return f.read()
    
    def create_template(self, template_name: str, content: str) -> bool:
        """Create a new template"""
        template_path = os.path.join(self.templates_dir, template_name)
        
        with open(template_path, "w") as f:
            f.write(content)
        
        return True
    
    def update_template(self, template_name: str, content: str) -> bool:
        """Update an existing template"""
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            return False
        
        with open(template_path, "w") as f:
            f.write(content)
        
        return True
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template"""
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            return False
        
        os.remove(template_path)
        return True

class HtmlPageManager:
    """Class for managing HTML pages"""
    
    def __init__(self, pages_dir: str, db_path: str):
        """Initialize with directories and database path"""
        self.pages_dir = pages_dir
        self.db_path = db_path
        self.pages: List[HtmlPage] = []
        
        # Create directories if they don't exist
        os.makedirs(pages_dir, exist_ok=True)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Load database if it exists
        self.load_database()
    
    def load_database(self) -> None:
        """Load pages from database"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                
                self.pages = [HtmlPage.from_dict(page_data) for page_data in data]
            except Exception as e:
                logger.error(f"Error loading database: {e}")
                self.pages = []
    
    def save_database(self) -> None:
        """Save pages to database"""
        try:
            with open(self.db_path, "w") as f:
                json.dump([page.to_dict() for page in self.pages], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def get_page(self, page_id: int) -> Optional[HtmlPage]:
        """Get a page by ID"""
        for page in self.pages:
            if page.id == page_id:
                return page
        return None
    
    def get_page_by_filename(self, filename: str) -> Optional[HtmlPage]:
        """Get a page by filename"""
        for page in self.pages:
            if page.filename == filename:
                return page
        return None
    
    def create_page(self, filename: str, title: str, content: str) -> HtmlPage:
        """Create a new page"""
        # Find the next available ID
        next_id = max([p.id for p in self.pages]) + 1 if self.pages else 1
        
        # Create the page
        page = HtmlPage(
            id=next_id,
            filename=filename,
            title=title,
            content=content
        )
        
        # Add to the list
        self.pages.append(page)
        
        # Save to database
        self.save_database()
        
        # Write to file
        page_path = os.path.join(self.pages_dir, filename)
        with open(page_path, "w") as f:
            f.write(content)
        
        return page
    
    def update_page(self, page_id: int, title: str, content: str) -> Optional[HtmlPage]:
        """Update a page"""
        page = self.get_page(page_id)
        if not page:
            return None
        
        # Update the page
        page.title = title
        page.content = content
        page.updated_at = datetime.now().isoformat()
        
        # Save to database
        self.save_database()
        
        # Write to file
        page_path = os.path.join(self.pages_dir, page.filename)
        with open(page_path, "w") as f:
            f.write(content)
        
        return page
    
    def publish_page(self, page_id: int) -> Optional[HtmlPage]:
        """Publish a page"""
        page = self.get_page(page_id)
        if not page:
            return None
        
        # Update the page
        page.status = "published"
        page.updated_at = datetime.now().isoformat()
        
        # Save to database
        self.save_database()
        
        return page
    
    def delete_page(self, page_id: int) -> bool:
        """Delete a page"""
        page = self.get_page(page_id)
        if not page:
            return False
        
        # Remove from the list
        self.pages = [p for p in self.pages if p.id != page_id]
        
        # Save to database
        self.save_database()
        
        # Remove file
        page_path = os.path.join(self.pages_dir, page.filename)
        if os.path.exists(page_path):
            os.remove(page_path)
        
        return True

class NewsToHtmlConverter:
    """Class for converting news articles to HTML pages"""
    
    def __init__(self, template_manager: HtmlTemplateManager, page_manager: HtmlPageManager):
        """Initialize with template and page managers"""
        self.template_manager = template_manager
        self.page_manager = page_manager
    
    def create_news_page_from_articles(
        self,
        topic: str,
        articles: List[Dict[str, Any]],
        output_filename: str,
        header_text: str,
        subheader_text: str,
        header_image: str
    ) -> str:
        """Create a news page from articles"""
        # Get the template
        template_content = self.template_manager.get_template_content("news_template.html")
        if not template_content:
            raise ValueError("News template not found")
        
        # Prepare articles for template
        template_articles = []
        for article in articles:
            template_article = {
                "title": article["title"],
                "topic": article["topic"],
                "date": article["published_date"],
                "excerpt": article["content"][:150] + "..." if len(article["content"]) > 150 else article["content"],
                "url": article["url"],
                "image": article["local_image_path"] if article.get("local_image_path") else article.get("image_url", "/static/images/news/default.jpg")
            }
            template_articles.append(template_article)
        
        # Prepare featured article if available
        featured_article = None
        if template_articles:
            featured_article = template_articles[0]
            featured_article["tags"] = [featured_article["topic"]]
            template_articles = template_articles[1:]
        
        # Replace placeholders in template
        page_content = template_content
        page_content = page_content.replace("{{ page_title }}", header_text)
        page_content = page_content.replace("{{ page_description }}", subheader_text)
        page_content = page_content.replace("{{ header_text }}", header_text)
        page_content = page_content.replace("{{ subheader_text }}", subheader_text)
        page_content = page_content.replace("{{ header_image }}", header_image)
        
        # Replace featured article
        if featured_article:
            featured_html = f"""
            <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 mb-8">
                <div class="md:flex">
                    <div class="md:w-1/2">
                        <img src="{featured_article['image']}" alt="{featured_article['title']}" class="w-full h-full object-cover">
                    </div>
                    <div class="md:w-1/2 p-6">
                        <h2 class="text-2xl font-bold text-blue-400 mb-2">{featured_article['title']}</h2>
                        <p class="text-gray-400 mb-4">
                            <span><i class="fas fa-calendar-alt mr-1"></i> {featured_article['date']}</span>
                        </p>
                        <p class="text-gray-300 mb-6">{featured_article['excerpt']}</p>
                        <div class="flex flex-wrap gap-2 mb-6">
                            <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{featured_article['topic']}</span>
                        </div>
                        <a href="{featured_article['url']}" target="_blank" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition inline-block">
                            Read Full Article <i class="fas fa-external-link-alt ml-1"></i>
                        </a>
                    </div>
                </div>
            </div>
            """
            page_content = page_content.replace("{% if featured_article %}", "")
            page_content = page_content.replace("{% endif %}", "")
            page_content = page_content.replace("{{ featured_article.title }}", featured_article["title"])
            page_content = page_content.replace("{{ featured_article.date }}", featured_article["date"])
            page_content = page_content.replace("{{ featured_article.excerpt }}", featured_article["excerpt"])
            page_content = page_content.replace("{{ featured_article.image }}", featured_article["image"])
            page_content = page_content.replace("{{ featured_article.url }}", featured_article["url"])
            
            # Replace tags loop
            tags_html = ""
            for tag in featured_article["tags"]:
                tags_html += f'<span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{tag}</span>'
            page_content = page_content.replace("{% for tag in featured_article.tags %}", "")
            page_content = page_content.replace("{% endfor %}", "")
            page_content = page_content.replace('{{ tag }}', tags_html)
        else:
            # Remove featured article section
            page_content = page_content.replace("{% if featured_article %}", "{% if False %}")
        
        # Replace articles loop
        articles_html = ""
        for article in template_articles:
            article_html = f"""
            <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">
                <img src="{article['image']}" alt="{article['title']}" class="w-full h-48 object-cover">
                <div class="p-4">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-xl font-semibold text-blue-400">{article['title']}</h3>
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">{article['topic']}</span>
                    </div>
                    <p class="text-gray-400 text-sm mb-2">
                        <span><i class="fas fa-calendar-alt mr-1"></i> {article['date']}</span>
                    </p>
                    <p class="text-gray-300 mb-4">{article['excerpt']}</p>
                    <a href="{article['url']}" target="_blank" class="text-blue-400 hover:text-blue-300">
                        Read More <i class="fas fa-external-link-alt ml-1"></i>
                    </a>
                </div>
            </div>
            """
            articles_html += article_html
        
        page_content = page_content.replace("{% for article in articles %}", "")
        page_content = page_content.replace("{% endfor %}", "")
        
        # Replace article template with actual articles
        article_template_start = '<div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">'
        article_template_end = '</div>'
        article_template_full = page_content.split(article_template_start)[1].split(article_template_end)[0]
        article_template_full = article_template_start + article_template_full + article_template_end
        
        page_content = page_content.replace(article_template_full, articles_html)
        
        # Create or update the page
        existing_page = self.page_manager.get_page_by_filename(output_filename)
        if existing_page:
            page = self.page_manager.update_page(existing_page.id, header_text, page_content)
        else:
            page = self.page_manager.create_page(output_filename, header_text, page_content)
        
        # Publish the page
        if page:
            self.page_manager.publish_page(page.id)
        
        # Return the page path
        return os.path.join(self.page_manager.pages_dir, output_filename)
