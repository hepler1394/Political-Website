"""
USA AI News Tool - News Fetcher Module
This module handles fetching news from various APIs and managing news articles.
"""

import os
import json
import logging
import requests
import time
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Topic:
    """Class representing a news topic"""
    
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        keywords: List[str],
        priority: str = "medium"
    ):
        """Initialize a topic"""
        self.id = id
        self.name = name
        self.description = description
        self.keywords = keywords
        self.priority = priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "priority": self.priority
        }

class NewsArticle:
    """Class representing a news article"""
    
    def __init__(
        self,
        title: str,
        source: str,
        url: str,
        published_date: str,
        content: str,
        topic: str,
        image_url: Optional[str] = None,
        local_image_path: Optional[str] = None,
        status: str = "new",
        id: Optional[int] = None
    ):
        """Initialize a news article"""
        self.id = id
        self.title = title
        self.source = source
        self.url = url
        self.published_date = published_date
        self.content = content
        self.topic = topic
        self.image_url = image_url
        self.local_image_path = local_image_path
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "published_date": self.published_date,
            "content": self.content,
            "topic": self.topic,
            "image_url": self.image_url,
            "local_image_path": self.local_image_path,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsArticle':
        """Create from dictionary"""
        return cls(
            id=data.get("id"),
            title=data["title"],
            source=data["source"],
            url=data["url"],
            published_date=data["published_date"],
            content=data["content"],
            topic=data["topic"],
            image_url=data.get("image_url"),
            local_image_path=data.get("local_image_path"),
            status=data.get("status", "new")
        )

# Define default topics
PROJECT_TOPICS = [
    Topic(
        id=1,
        name="Climate Action",
        description="News and updates on climate policy, renewable energy, and environmental initiatives.",
        keywords=["climate change", "renewable energy", "carbon emissions", "green policy", "environmental"]
    ),
    Topic(
        id=2,
        name="Healthcare",
        description="News and updates on healthcare policy, universal coverage, and medical advances.",
        keywords=["healthcare", "medicare", "medicaid", "universal healthcare", "medical research"]
    ),
    Topic(
        id=3,
        name="Economic Justice",
        description="News and updates on economic inequality, labor rights, and progressive economic policies.",
        keywords=["economic inequality", "labor rights", "minimum wage", "wealth tax", "worker protections"]
    ),
    Topic(
        id=4,
        name="Voting Rights",
        description="News and updates on voting access, election security, and democratic reforms.",
        keywords=["voting rights", "election security", "voter suppression", "electoral reform", "democracy"]
    ),
    Topic(
        id=5,
        name="International News",
        description="Global news with a focus on progressive policies and international cooperation.",
        keywords=["international relations", "global cooperation", "united nations", "diplomacy", "global policy"]
    ),
    Topic(
        id=6,
        name="AI News",
        description="News and updates on artificial intelligence, its impacts, and ethical considerations.",
        keywords=["artificial intelligence", "AI ethics", "machine learning", "AI regulation", "AI research"]
    )
]

class NewsFetcher:
    """Class for fetching news from various APIs"""
    
    def __init__(self, brave_api_key: str = None, google_api_key: str = None):
        """Initialize with API keys"""
        self.brave_api_key = brave_api_key
        self.google_api_key = google_api_key
        
        if not brave_api_key:
            logger.warning("Brave API key not provided. Brave search will not be available.")
        
        if not google_api_key:
            logger.warning("Google API key not provided. Google News search will not be available.")
    
    def fetch_news_for_topic(self, topic: Topic, limit: int = 10) -> List[NewsArticle]:
        """Fetch news for a specific topic"""
        articles = []
        
        # Try Brave API first
        if self.brave_api_key:
            brave_articles = self._fetch_from_brave(topic, limit)
            articles.extend(brave_articles)
        
        # If we don't have enough articles, try Google News API
        if len(articles) < limit and self.google_api_key:
            remaining = limit - len(articles)
            google_articles = self._fetch_from_google(topic, remaining)
            articles.extend(google_articles)
        
        # If we still don't have enough articles, use mock data
        if len(articles) < limit:
            remaining = limit - len(articles)
            mock_articles = self._get_mock_articles(topic, remaining)
            articles.extend(mock_articles)
        
        return articles[:limit]
    
    def _fetch_from_brave(self, topic: Topic, limit: int) -> List[NewsArticle]:
        """Fetch news from Brave Search API"""
        articles = []
        
        try:
            # Construct query from topic keywords
            query = " OR ".join(topic.keywords)
            
            # Make API request
            headers = {
                "X-Subscription-Token": self.brave_api_key,
                "Accept": "application/json"
            }
            
            params = {
                "q": query,
                "count": limit,
                "freshness": "week"
            }
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/news/search",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse results
                for item in data.get("results", []):
                    article = NewsArticle(
                        title=item.get("title", ""),
                        source=item.get("source", "Brave Search"),
                        url=item.get("url", ""),
                        published_date=item.get("published_date", datetime.now().isoformat()),
                        content=item.get("description", ""),
                        topic=topic.name,
                        image_url=item.get("image", {}).get("url")
                    )
                    articles.append(article)
            else:
                logger.error(f"Brave API error: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Error fetching from Brave: {e}")
        
        return articles
    
    def _fetch_from_google(self, topic: Topic, limit: int) -> List[NewsArticle]:
        """Fetch news from Google News API"""
        articles = []
        
        try:
            # Construct query from topic keywords
            query = " OR ".join(topic.keywords)
            
            # Make API request
            params = {
                "q": query,
                "apiKey": self.google_api_key,
                "pageSize": limit,
                "language": "en"
            }
            
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse results
                for item in data.get("articles", []):
                    article = NewsArticle(
                        title=item.get("title", ""),
                        source=item.get("source", {}).get("name", "Google News"),
                        url=item.get("url", ""),
                        published_date=item.get("publishedAt", datetime.now().isoformat()),
                        content=item.get("description", ""),
                        topic=topic.name,
                        image_url=item.get("urlToImage")
                    )
                    articles.append(article)
            else:
                logger.error(f"Google News API error: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Error fetching from Google: {e}")
        
        return articles
    
    def _get_mock_articles(self, topic: Topic, limit: int) -> List[NewsArticle]:
        """Get mock articles for a topic"""
        articles = []
        
        # Mock data for each topic
        mock_data = {
            "Climate Action": [
                {
                    "title": "New Climate Bill Gains Bipartisan Support",
                    "source": "Climate News Network",
                    "url": "https://example.com/climate-bill",
                    "published_date": "2025-05-20T10:30:00",
                    "content": "A groundbreaking climate bill has gained surprising bipartisan support in Congress. The legislation aims to reduce carbon emissions by 50% by 2030 through investments in renewable energy infrastructure and carbon capture technology.",
                    "image_url": "/static/images/news/climate_action_1.jpg"
                },
                {
                    "title": "Renewable Energy Surpasses Coal for First Time",
                    "source": "Energy Today",
                    "url": "https://example.com/renewable-energy",
                    "published_date": "2025-05-19T14:45:00",
                    "content": "In a historic milestone, renewable energy sources have surpassed coal in total electricity generation for the first time in U.S. history. Solar and wind power now account for over 25% of the nation's electricity production.",
                    "image_url": "/static/images/news/climate_action_2.jpg"
                }
            ],
            "Healthcare": [
                {
                    "title": "Universal Healthcare Plan Unveiled",
                    "source": "Health Policy Journal",
                    "url": "https://example.com/universal-healthcare",
                    "published_date": "2025-05-20T09:15:00",
                    "content": "A comprehensive universal healthcare plan has been unveiled by a coalition of lawmakers. The plan would provide coverage to all Americans while reducing overall healthcare costs through negotiated pricing and administrative efficiency.",
                    "image_url": "/static/images/news/healthcare_1.jpg"
                },
                {
                    "title": "Breakthrough in Cancer Treatment Shows Promise",
                    "source": "Medical Research Today",
                    "url": "https://example.com/cancer-treatment",
                    "published_date": "2025-05-18T11:30:00",
                    "content": "A new immunotherapy approach has shown remarkable results in clinical trials, with over 70% of patients experiencing complete remission of advanced-stage cancers. Researchers are calling it a potential paradigm shift in cancer treatment.",
                    "image_url": "/static/images/news/healthcare_2.jpg"
                }
            ],
            "Economic Justice": [
                {
                    "title": "Minimum Wage Increase Boosts Economy",
                    "source": "Economic Times",
                    "url": "https://example.com/minimum-wage",
                    "published_date": "2025-05-20T08:45:00",
                    "content": "A recent study has found that states that increased their minimum wage saw significant economic growth and reduced poverty rates. Consumer spending increased by 12% in areas with higher minimum wages, driving local business growth.",
                    "image_url": "/static/images/news/economic_justice_1.jpg"
                },
                {
                    "title": "Wealth Tax Proposal Gains Momentum",
                    "source": "Financial Policy Review",
                    "url": "https://example.com/wealth-tax",
                    "published_date": "2025-05-17T16:20:00",
                    "content": "A proposed wealth tax on ultra-high net worth individuals is gaining momentum in Congress. The tax would apply to households with over $50 million in assets and could generate an estimated $3 trillion in revenue over ten years.",
                    "image_url": "/static/images/news/economic_justice_2.jpg"
                }
            ],
            "Voting Rights": [
                {
                    "title": "Automatic Voter Registration Bill Passes",
                    "source": "Democracy Now",
                    "url": "https://example.com/voter-registration",
                    "published_date": "2025-05-20T13:10:00",
                    "content": "A bill establishing automatic voter registration has passed with strong support. The legislation will automatically register eligible citizens to vote when they interact with government agencies, potentially adding millions of new voters to the rolls.",
                    "image_url": "/static/images/news/voting_rights_1.jpg"
                },
                {
                    "title": "Election Security Measures Enhanced",
                    "source": "Electoral Integrity Watch",
                    "url": "https://example.com/election-security",
                    "published_date": "2025-05-16T10:45:00",
                    "content": "New election security measures have been implemented nationwide, including paper ballot backups, risk-limiting audits, and enhanced cybersecurity protocols. Experts say these changes will make the 2028 election the most secure in history.",
                    "image_url": "/static/images/news/voting_rights_2.jpg"
                }
            ],
            "International News": [
                {
                    "title": "Global Climate Accord Reaches Milestone",
                    "source": "International Herald",
                    "url": "https://example.com/climate-accord",
                    "published_date": "2025-05-20T07:30:00",
                    "content": "The global climate accord has reached a significant milestone with 150 countries now having submitted enhanced emissions reduction targets. The collective commitments put the world on track to limit warming to 1.8°C above pre-industrial levels.",
                    "image_url": "/static/images/news/international_news_1.jpg"
                },
                {
                    "title": "Diplomatic Breakthrough in Middle East",
                    "source": "Global Affairs",
                    "url": "https://example.com/middle-east-diplomacy",
                    "published_date": "2025-05-15T14:20:00",
                    "content": "A major diplomatic breakthrough has been achieved in the Middle East with the signing of a comprehensive peace agreement. The accord includes provisions for economic cooperation, security arrangements, and cultural exchanges.",
                    "image_url": "/static/images/news/international_news_2.jpg"
                }
            ],
            "AI News": [
                {
                    "title": "AI Ethics Framework Adopted Globally",
                    "source": "Tech Policy Today",
                    "url": "https://example.com/ai-ethics",
                    "published_date": "2025-05-20T11:45:00",
                    "content": "A comprehensive AI ethics framework has been adopted by major technology companies and governments worldwide. The framework establishes principles for transparency, accountability, and fairness in AI systems development and deployment.",
                    "image_url": "/static/images/news/ai_news_1.jpg"
                },
                {
                    "title": "Breakthrough in General AI Research",
                    "source": "AI Research Journal",
                    "url": "https://example.com/general-ai",
                    "published_date": "2025-05-14T09:30:00",
                    "content": "Researchers have announced a significant breakthrough in general artificial intelligence, demonstrating a system capable of transferring learning across multiple domains without specific training. The advance could accelerate progress toward more capable AI systems.",
                    "image_url": "/static/images/news/ai_news_2.jpg"
                }
            ]
        }
        
        # Get mock data for the topic
        topic_data = mock_data.get(topic.name, [])
        
        # Create articles
        for i in range(min(limit, len(topic_data))):
            data = topic_data[i]
            article = NewsArticle(
                title=data["title"],
                source=data["source"],
                url=data["url"],
                published_date=data["published_date"],
                content=data["content"],
                topic=topic.name,
                image_url=data["image_url"]
            )
            articles.append(article)
        
        return articles

class ImageDownloader:
    """Class for downloading images from news articles"""
    
    def __init__(self, save_dir: str):
        """Initialize with save directory"""
        self.save_dir = save_dir
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
    
    def download_image(self, article: NewsArticle) -> Optional[str]:
        """Download image for an article"""
        if not article.image_url:
            return None
        
        try:
            # Generate filename
            timestamp = int(time.time())
            topic_slug = article.topic.lower().replace(" ", "_")
            extension = os.path.splitext(article.image_url)[1]
            if not extension:
                extension = ".jpg"  # Default to jpg
            
            filename = f"{topic_slug}_{timestamp}{extension}"
            save_path = os.path.join(self.save_dir, filename)
            
            # Download image
            response = requests.get(article.image_url, stream=True)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                # Return relative path
                return f"/static/images/news/{filename}"
            else:
                logger.error(f"Error downloading image: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None

class NewsManager:
    """Class for managing news articles"""
    
    def __init__(self, db_path: str):
        """Initialize with database path"""
        self.db_path = db_path
        self.articles: List[NewsArticle] = []
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Load database if it exists
        self.load_database()
    
    def load_database(self) -> None:
        """Load articles from database"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                
                self.articles = [NewsArticle.from_dict(article_data) for article_data in data]
            except Exception as e:
                logger.error(f"Error loading database: {e}")
                self.articles = []
    
    def save_database(self) -> None:
        """Save articles to database"""
        try:
            with open(self.db_path, "w") as f:
                json.dump([article.to_dict() for article in self.articles], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def add_article(self, article: NewsArticle) -> bool:
        """Add a single article"""
        # Check if article already exists
        for existing in self.articles:
            if existing.url == article.url:
                return False
        
        # Find the next available ID
        next_id = max([a.id for a in self.articles]) + 1 if self.articles else 1
        
        # Set the ID
        article.id = next_id
        
        # Add to the list
        self.articles.append(article)
        
        # Save to database
        self.save_database()
        
        return True
    
    def add_articles(self, articles: List[NewsArticle]) -> int:
        """Add multiple articles"""
        count = 0
        for article in articles:
            if self.add_article(article):
                count += 1
        
        return count
    
    def get_article(self, article_id: int) -> Optional[NewsArticle]:
        """Get an article by ID"""
        for article in self.articles:
            if article.id == article_id:
                return article
        return None
    
    def get_articles_by_topic(self, topic: str) -> List[NewsArticle]:
        """Get articles by topic"""
        return [article for article in self.articles if article.topic == topic]
    
    def update_article_status(self, article_id: int, status: str) -> bool:
        """Update article status"""
        article = self.get_article(article_id)
        if not article:
            return False
        
        # Update the status
        article.status = status
        
        # Save to database
        self.save_database()
        
        return True
    
    def delete_article(self, article_id: int) -> bool:
        """Delete an article"""
        article = self.get_article(article_id)
        if not article:
            return False
        
        # Remove from the list
        self.articles = [a for a in self.articles if a.id != article_id]
        
        # Save to database
        self.save_database()
        
        return True
