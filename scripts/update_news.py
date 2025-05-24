import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import re
import argparse
import html

# --- Helper Functions ---
def format_date(date_string):
    """Converts various ISO date string formats to 'Month Day, Year' format."""
    if not date_string:
        return "Date N/A"
    
    try:
        dt_object = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        if dt_object.tzinfo is None:
            dt_object = dt_object.replace(tzinfo=timezone.utc)
        return dt_object.strftime("%B %d, %Y")
    except ValueError:
        print(f"Warning: Could not parse date string: {date_string}")
        return "Date N/A"

def generate_news_card_html(article):
    """Generates HTML for a single news card."""
    title = html.escape(article.get('title', 'No Title Available'))
    description = html.escape(article.get('description', 'No Description Available'))
    url = article.get('url', '#')
    image_url = article.get('image_url', 'https://placehold.co/400x300/0a1128/00a8ff?text=News')
    published_at = format_date(article.get('published_at', ''))
    source_name = html.escape(article.get('source_name', 'Source N/A'))
    tags = article.get('tags', [])

    tags_html = ""
    if tags:
        tags_html = '<div class="news-tags">' + ''.join(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags if tag) + '</div>'

    return f"""
            <div class="news-card">
                <div class="news-image">
                    <img src="{html.escape(image_url)}" alt="{title}" onerror="this.onerror=null;this.src='https://placehold.co/400x300/0a1128/FFFFFF?text=Image+Error';">
                </div>
                <div class="news-info">
                    <div class="news-meta">
                        <div class="news-date">{published_at}</div>
                        <div class="news-source">Source: {source_name}</div>
                    </div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    {tags_html}
                    <a href="{html.escape(url)}" class="news-more" target="_blank" rel="noopener noreferrer">Read Full Article</a>
                </div>
            </div>
    """

def generate_featured_news_html(article):
    """Generates HTML for the featured news card."""
    title = html.escape(article.get('title', 'No Title Available'))
    description = html.escape(article.get('description', 'No Description Available'))
    url = article.get('url', '#')
    image_url = article.get('image_url', 'https://placehold.co/800x500/0a1128/00a8ff?text=Featured+News')
    published_at = format_date(article.get('published_at', ''))
    source_name = html.escape(article.get('source_name', 'Source N/A'))
    tags = article.get('tags', [])

    tags_html = ""
    if tags:
        tags_html = '<div class="news-tags">' + ''.join(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags if tag) + '</div>'
    
    return f"""
            <div class="featured-news-card">
                <div class="featured-news-image">
                    <div class="news-tag">Featured</div>
                    <img src="{html.escape(image_url)}" alt="{title}" onerror="this.onerror=null;this.src='https://placehold.co/800x500/0a1128/FFFFFF?text=Image+Error';">
                </div>
                <div class="featured-news-content">
                    <div class="news-meta">
                        <div class="news-date">{published_at}</div>
                        <div class="news-source">Source: {source_name}</div>
                    </div>
                    <h2>{title}</h2>
                    <p class="news-excerpt">{description}</p>
                    {tags_html}
                    <a href="{html.escape(url)}" class="btn btn-primary news-more" target="_blank" rel="noopener noreferrer">Read Full Story</a>
                </div>
            </div>
    """

def fetch_brave_news_articles(api_key, query, country_locale, limit=10, search_lang='en'):
    """Fetches and processes articles from Brave News API."""
    if not api_key:
        print("Brave News API: Key not provided. Cannot fetch news.")
        return []

    brave_api_url = "https://api.search.brave.com/news/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
    country_code = country_locale.split(',')[0].strip() if country_locale else 'us'

    params = {
        "q": query,
        "country": country_code,
        "search_lang": search_lang,
        "freshness": "pw",  # Past Week for more results
        "text_decorations": "false",
        "spellcheck": "true",
        "count": limit + 5 # Fetch more to allow for filtering
    }
    print(f"Fetching from Brave News API with query: '{query}', country: '{country_code}', limit: {limit}")
    
    processed_articles = []
    try:
        response = requests.get(brave_api_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        results = response.json().get('results', [])
        print(f"Brave News API returned {len(results)} articles raw.")
        
        for article_data in results:
            if article_data.get('url') and article_data.get('thumbnail', {}).get('src') and article_data.get('title'):
                source_meta = article_data.get('meta_url', {})
                source_name = source_meta.get('hostname') if source_meta else article_data.get('profile', {}).get('name')
                source_name = source_name.replace('www.', '').split('.')[0].capitalize() if source_name else "News Source"

                tags = [t.strip().capitalize() for t in query.replace('OR', ' ').replace('AND', ' ').split() if t.strip()]
                
                processed_articles.append({
                    'title': article_data.get('title'),
                    'description': article_data.get('description'),
                    'url': article_data.get('url'),
                    'image_url': article_data.get('thumbnail', {}).get('src'),
                    'published_at': article_data.get('date_published'), 
                    'source_name': source_name,
                    'tags': list(set(tags))
                })
        print(f"Brave News API: {len(processed_articles)} articles passed filtering.")
        return processed_articles[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from Brave News API: {e}")
        return []

# --- Main Logic ---
def main(args):
    print(f"--- Starting news update for {args.html_file_name} ---")
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
    brave_api_key = os.getenv('BRAVE_NEWS_API_KEY')

    if not brave_api_key:
        print("CRITICAL ERROR: BRAVE_NEWS_API_KEY not found. Cannot fetch news.")
        all_articles = []
    else:
        all_articles = fetch_brave_news_articles(
            brave_api_key,
            args.query,
            args.api_locale,
            limit=args.max_articles
        )
    
    print(f"Total articles to display: {len(all_articles)}")

    if all_articles:
        featured_article_html = generate_featured_news_html(all_articles[0])
        regular_news_html_content = ""
        if len(all_articles) > 1:
            regular_articles_list = [generate_news_card_html(all_articles[i]) for i in range(1, len(all_articles))]
            regular_news_html_content = "".join(regular_articles_list)
    else:
        print("No articles found to display. Page sections will be cleared.")
        featured_article_html = ""
        regular_news_html_content = ""

    html_file_path = os.path.join(os.path.dirname(__file__), '..', args.html_file_name)
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"CRITICAL ERROR: HTML file {html_file_path} not found.")
        return

    updated_html_content = html_content

    # Update featured news section
    pattern_featured = ""
    if args.featured_div_identifier.startswith('#'):
        div_id = args.featured_div_identifier[1:]
        pattern_featured = rf'(<div\s+[^>]*id="{re.escape(div_id)}"[^>]*>)(.*?)(</div>)'
    elif args.featured_div_identifier.startswith('.'):
        div_class = args.featured_div_identifier[1:]
        pattern_featured = rf'(<div\s+[^>]*class="[^"]*\b{re.escape(div_class)}\b[^"]*"[^>]*>)(.*?)(</div>)'

    if pattern_featured:
        if re.search(pattern_featured, updated_html_content, re.DOTALL):
            updated_html_content = re.sub(pattern_featured, f'\\1{featured_article_html.strip()}\\3', updated_html_content, count=1, flags=re.DOTALL)
            print(f"Successfully updated featured news section: {args.featured_div_identifier}")
        else:
            print(f"ERROR: Did not find featured news div matching: {args.featured_div_identifier}")
    
    # Update regular news grid section
    pattern_grid = r'(<div\s+class="news-grid"\s*[^>]*>)(.*?)(</div>)'
    if re.search(pattern_grid, updated_html_content, re.DOTALL):
        updated_html_content = re.sub(pattern_grid, f'\\1{regular_news_html_content.strip()}\\3', updated_html_content, count=1, flags=re.DOTALL)
        print("Successfully updated news grid section.")
    else:
        print("ERROR: Did not find news grid div.")

    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html_content)
        print(f"Successfully wrote updates to {args.html_file_name}.")
    except Exception as e:
        print(f"CRITICAL ERROR writing to {html_file_path}: {e}")
    print(f"--- Finished news update for {args.html_file_name} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update HTML file with news from the Brave News API.")
    parser.add_argument('--html_file_name', required=True, help='Name of the HTML file to update.')
    parser.add_argument('--query', required=True, help='Search query for the Brave News API.')
    parser.add_argument('--api_locale', default="us", help='Primary locale for Brave News API (e.g., "us", "gb").')
    parser.add_argument('--featured_div_identifier', required=True, help='CSS Selector for the featured news div (e.g., "#smart-grid" or ".featured-news").')
    parser.add_argument('--max_articles', type=int, default=10, help='Total number of articles to fetch and display.')
    
    parsed_args = parser.parse_args()
    main(parsed_args)
