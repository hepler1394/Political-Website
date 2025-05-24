import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import re
import argparse
import html # For escaping

# --- Helper Functions ---
def format_date(date_string):
    """Converts various ISO date string formats to 'Month Day, Year' format."""
    if not date_string:
        return "Date N/A"
    
    formats_to_try = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # With microseconds and Z UTC
        "%Y-%m-%dT%H:%M:%SZ",    # Without microseconds and Z UTC
        "%Y-%m-%dT%H:%M:%S%z",   # With timezone offset
        "%Y-%m-%dT%H:%M:%S",     # Without timezone (assume UTC)
    ]
    
    dt_object = None
    for fmt in formats_to_try:
        try:
            dt_object = datetime.strptime(date_string, fmt)
            if dt_object.tzinfo is None or dt_object.tzinfo.utcoffset(dt_object) is None:
                dt_object = dt_object.replace(tzinfo=timezone.utc)
            break 
        except ValueError:
            continue
            
    if dt_object is None:
        try:
            # More general ISO parsing, handling potential 'Z' for UTC
            dt_object = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            if dt_object.tzinfo is None or dt_object.tzinfo.utcoffset(dt_object) is None:
                 dt_object = dt_object.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Warning: Could not parse date string: {date_string}")
            return "Date N/A"
            
    return dt_object.strftime("%B %d, %Y")

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

    # Added news-meta div for better structure of date and source
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
    
    # Added news-meta div for better structure of date and source
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

# --- API Fetching Functions ---
def fetch_thenewsapi_articles(api_token, locale, categories, limit=3):
    """Fetches and processes articles from The News API."""
    if not api_token:
        print("TheNewsAPI: Token not provided. Skipping fetch.")
        return []
        
    news_api_url = "https://api.thenewsapi.com/v1/news/top"
    params = {
        'api_token': api_token,
        'language': 'en',
        'limit': limit + 5, 
        'categories': categories if categories else None,
        'locale': locale if locale else None
    }
    params = {k: v for k, v in params.items() if v is not None}

    print(f"Fetching from TheNewsAPI with params: {params}")
    processed_articles = []
    try:
        response = requests.get(news_api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json().get('data', [])
        print(f"TheNewsAPI returned {len(data)} articles raw.")
        
        for article in data:
            if article.get('url') and (article.get('image_url') or article.get('image')):
                image = article.get('image_url') or article.get('image')
                source_domain = article.get('source', 'N/A')
                source_name = "News Source" # Default
                if source_domain and isinstance(source_domain, str):
                    source_name = source_domain.replace('www.', '').split('.')[0].capitalize()
                
                article_tags = article.get('categories', [])
                if isinstance(article_tags, list): # Ensure tags are a list
                    article_tags = [tag.strip().capitalize() for tag in article_tags if isinstance(tag, str)]
                else:
                    article_tags = []


                processed_articles.append({
                    'title': article.get('title'),
                    'description': article.get('description') or article.get('snippet'),
                    'url': article.get('url'),
                    'image_url': image,
                    'published_at': article.get('published_at'),
                    'source_name': source_name,
                    'tags': list(set(article_tags)) # Deduplicate
                })
        print(f"TheNewsAPI: {len(processed_articles)} articles after initial processing and filtering.")
        return processed_articles[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from TheNewsAPI: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred with TheNewsAPI: {e}")
        return []


def fetch_brave_news_articles(api_key, query_categories, country_locale, search_lang='en', limit=10):
    """Fetches and processes articles from Brave News API."""
    if not api_key:
        print("Brave News API: Key not provided. Skipping fetch.")
        return []

    brave_api_url = "https://api.search.brave.com/news/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    query = query_categories.replace(',', ' OR ') if query_categories else "latest news"
    country_code = country_locale.split(',')[0] if country_locale else 'us'

    params = {
        "q": query,
        "country": country_code,
        "search_lang": search_lang,
        "freshness": "pd", # Past day for more freshness
        "text_decorations": "false",
        "spellcheck": "true",
        "count": limit + 10 
    }
    print(f"Fetching from Brave News API with params: {params}")
    processed_articles = []
    try:
        response = requests.get(brave_api_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        results = response.json().get('results', [])
        print(f"Brave News API returned {len(results)} articles raw.")
        
        for article_data in results: # Renamed to avoid conflict with outer 'article'
            if article_data.get('url') and article_data.get('thumbnail', {}).get('src') and article_data.get('title'):
                source_meta = article_data.get('meta_url', {})
                source_name = source_meta.get('hostname') if source_meta else article_data.get('profile', {}).get('name')
                if not source_name or not isinstance(source_name, str):
                    source_name = "News Source"
                else:
                    source_name = source_name.replace('www.', '').split('.')[0].capitalize()

                article_tags = []
                if query_categories: # Prioritize tags from the original query
                    article_tags = [cat.strip().capitalize() for cat in query_categories.split(',') if cat.strip()]
                # Brave API sometimes has 'cluster.category' or similar, but it's not consistent.
                # For now, stick to query categories for Brave.
                
                processed_articles.append({
                    'title': article_data.get('title'),
                    'description': article_data.get('description'),
                    'url': article_data.get('url'),
                    'image_url': article_data.get('thumbnail', {}).get('src'),
                    'published_at': article_data.get('date_published'), 
                    'source_name': source_name,
                    'tags': list(set(article_tags)) # Deduplicate
                })
        print(f"Brave News API: {len(processed_articles)} articles after initial processing and filtering.")
        return processed_articles[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from Brave News API: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred with Brave News API: {e}")
        return []

# --- Main Logic ---
def main(args):
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
    thenewsapi_token = os.getenv('NEWS_API_TOKEN')
    brave_api_key = os.getenv('BRAVE_NEWS_API_KEY')

    if not brave_api_key and not thenewsapi_token: # Check if at least one key is present
        print("Error: No API tokens (BRAVE_NEWS_API_KEY or NEWS_API_TOKEN) found in .env file. Cannot fetch news.")
        return

    all_articles = []
    
    # Prioritize Brave News API
    if brave_api_key:
        brave_query = args.api_categories
        if not brave_query: # Default queries if no categories specified
            if args.html_file_name == "recent-news.html": brave_query = "US politics, breaking news"
            elif args.html_file_name == "international-news.html": brave_query = "world news, international relations"
            elif args.html_file_name == "ai-news.html": brave_query = "artificial intelligence, technology innovations"
            else: brave_query = "latest news"
        
        brave_articles = fetch_brave_news_articles(brave_api_key, brave_query, args.api_locale, limit=args.max_articles)
        all_articles.extend(brave_articles)
        print(f"Fetched {len(brave_articles)} articles from Brave News API.")

    # Supplement with TheNewsAPI if needed and token available (max 3 from here)
    remaining_needed = args.max_articles - len(all_articles)
    if thenewsapi_token and remaining_needed > 0:
        thenewsapi_articles = fetch_thenewsapi_articles(thenewsapi_token, args.api_locale, args.api_categories, limit=min(remaining_needed, 3))
        all_articles.extend(thenewsapi_articles)
        print(f"Fetched {len(thenewsapi_articles)} articles from TheNewsAPI to supplement.")
    
    # Remove duplicates based on URL (preferring earlier entries, e.g., from Brave if it was primary)
    seen_urls = set()
    unique_articles = []
    for article_item in all_articles: # Renamed to avoid conflict
        if article_item['url'] not in seen_urls:
            unique_articles.append(article_item)
            seen_urls.add(article_item['url'])
    all_articles = unique_articles[:args.max_articles] # Ensure we don't exceed max_articles
    print(f"Total unique articles after combining, deduplicating, and limiting: {len(all_articles)}")

    featured_article_html = ""
    regular_news_html_content = ""

    if all_articles:
        featured_article_html = generate_featured_news_html(all_articles[0])
        
        regular_articles_list = []
        if len(all_articles) > 1:
            for i in range(1, len(all_articles)): # Iterate through the rest for the grid
                regular_articles_list.append(generate_news_card_html(all_articles[i]))
        
        if regular_articles_list:
            regular_news_html_content = "".join(regular_articles_list)
        elif len(all_articles) == 1 : 
             regular_news_html_content = ""
    else:
        print("No articles found from any API after filtering to display.")

    html_file_path = os.path.join(os.path.dirname(__file__), '..', args.html_file_name)
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: HTML file {html_file_path} not found.")
        return
    except Exception as e:
        print(f"Error reading {html_file_path}: {e}")
        return
        
    updated_html_content = html_content

    # Update featured news section
    pattern_featured = ""
    if args.featured_div_identifier.startswith('#'):
        div_id = args.featured_div_identifier[1:]
        pattern_featured = rf'(<div\s+[^>]*id="{re.escape(div_id)}"[^>]*>)(.*?)(</div>)'
    elif args.featured_div_identifier.startswith('.'):
        div_class = args.featured_div_identifier[1:]
        # More specific: find the first div that *contains* the class, not just starts with it.
        pattern_featured = rf'(<div\s+[^>]*class="[^"]*\b{re.escape(div_class)}\b[^"]*"[^>]*>)(.*?)(</div>)'
    else:
        print(f"ERROR: Invalid featured_div_identifier: {args.featured_div_identifier}. Must start with # or .")
        pattern_featured = None

    if pattern_featured:
        match_featured = re.search(pattern_featured, updated_html_content, re.DOTALL)
        if match_featured:
            replacement_featured = f'{match_featured.group(1)}{featured_article_html.strip()}{match_featured.group(3)}'
            updated_html_content = re.sub(pattern_featured, replacement_featured, updated_html_content, count=1, flags=re.DOTALL)
            print(f"Successfully updated featured news section: {args.featured_div_identifier}")
        else:
            print(f"ERROR: Did not find featured news div matching identifier: {args.featured_div_identifier} in {args.html_file_name}")
    else:
         print(f"Skipping featured news update for {args.html_file_name} due to invalid identifier.")

    # Update regular news grid section
    pattern_grid = r'(<div\s+class="news-grid"\s*[^>]*>)(.*?)(</div>)' # Made class matching more flexible
    match_grid = re.search(pattern_grid, updated_html_content, re.DOTALL)
    if match_grid:
        replacement_grid = f'{match_grid.group(1)}{regular_news_html_content.strip()}{match_grid.group(3)}'
        updated_html_content = re.sub(pattern_grid, replacement_grid, updated_html_content, count=1, flags=re.DOTALL)
        print(f"Successfully updated news grid section in {args.html_file_name}.")
    else:
        print(f"ERROR: Did not find news grid div (<div class=\"news-grid\">) for update in {args.html_file_name}.")

    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html_content)
        print(f"Successfully wrote updates to {args.html_file_name}.")
    except Exception as e:
        print(f"Error writing updated content to {html_file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update HTML file with news from Brave News API and TheNewsAPI.")
    parser.add_argument('--html_file_name', type=str, required=True, help='Name of the HTML file to update.')
    parser.add_argument('--api_locale', type=str, default="us", help='Comma-separated primary locale(s) for news APIs (e.g., "us", "gb,ca"). Brave uses the first one.')
    parser.add_argument('--api_categories', type=str, default="", help='Comma-separated categories/query terms (e.g., "politics,technology"). Used as query for Brave.')
    parser.add_argument('--featured_div_identifier', type=str, required=True, help='CSS Selector for the featured news div (e.g., "#smart-grid" or ".featured-news").')
    parser.add_argument('--max_articles', type=int, default=10, help='Total number of articles to display (1 featured + N-1 grid).')
    
    parsed_args = parser.parse_args()
    main(parsed_args)
