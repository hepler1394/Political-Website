import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

def format_date(date_string):
    """Converts ISO date string to 'Month Day, Year' format."""
    try:
        dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ") # Handle cases without microseconds
        except ValueError:
            return "Date N/A" # Fallback if parsing fails
    return dt_object.strftime("%B %d, %Y")

def generate_news_card_html(article):
    """Generates HTML for a single news card."""
    title = article.get('title', 'No Title Available')
    description = article.get('description', article.get('snippet', 'No Description Available'))
    url = article.get('url') # Default '#' removed, as articles without URLs are skipped in main()
    image_url = article.get('image_url', 'https://via.placeholder.com/400x300/00a8ff/ffffff?text=News')
    published_at = format_date(article.get('published_at', ''))

    # Basic HTML escaping for title and description
    title = title.replace('<', '&lt;').replace('>', '&gt;')
    description = description.replace('<', '&lt;').replace('>', '&gt;')

    return f"""
            <div class="news-card">
                <div class="news-image">
                    <img src="{image_url}" alt="{title}">
                </div>
                <div class="news-info">
                    <div class="news-date">{published_at}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <a href="{url}" class="news-more" target="_blank">Read Full Article</a>
                </div>
            </div>
    """

def generate_featured_news_html(article):
    """Generates HTML for the featured news card."""
    title = article.get('title', 'No Title Available')
    description = article.get('description', article.get('snippet', 'No Description Available'))
    url = article.get('url') # Assumes URL is present due to pre-filtering
    image_url = article.get('image_url') # Assumes image_url is present
    published_at = format_date(article.get('published_at', ''))

    # Basic HTML escaping
    title = title.replace('<', '&lt;').replace('>', '&gt;')
    description = description.replace('<', '&lt;').replace('>', '&gt;')

    return f"""
            <div class="featured-news-card">
                <div class="featured-news-image">
                    <div class="news-tag">Featured</div>
                    <img src="{image_url}" alt="{title}">
                </div>
                <div class="featured-news-content">
                    <div class="news-date">{published_at}</div>
                    <h2>{title}</h2>
                    <p class="news-excerpt">{description}</p>
                    <a href="{url}" class="btn btn-primary news-more" target="_blank" rel="noopener noreferrer">Read Full Story</a>
                </div>
            </div>
    """

def main():
    MAX_ARTICLES_TO_DISPLAY = 20
    # Load environment variables
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
    api_token = os.getenv('NEWS_API_TOKEN')

    if not api_token:
        print("Error: NEWS_API_TOKEN not found in .env file.")
        return

    # Fetch news from The News API
    news_api_url = "https://api.thenewsapi.com/v1/news/top"
    params = {
        'api_token': api_token,
        'locale': 'us',
        'language': 'en',
        'limit': 30,
        'categories': 'politics'
    }

    try:
        response = requests.get(news_api_url, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from API: {e}")
        return

    news_data = response.json()
    articles = news_data.get('data')

    if not articles:
        print("No articles found in API response.")
        return

    # Stricter Article Filtering
    filtered_articles = []
    if articles:
        for article in articles:
            url = article.get('url')
            image_url = article.get('image_url')
            if url and image_url: # Must have both URL and image_url
                filtered_articles.append(article)
            else:
                title = article.get('title', 'N/A')
                print(f"Skipping article due to missing URL or image_url: {title}")
    
    if not filtered_articles:
        print("No suitable articles found after filtering.")
        # Prepare empty content to clear sections if needed
        featured_article_html = "<!-- No featured article available -->"
        regular_news_html_content = "<!-- No regular news articles available -->"
    else:
        featured_article_html = ""
        regular_news_html_content = ""
        articles_for_display_count = 0

        # Select featured article
        featured_article_html = generate_featured_news_html(filtered_articles[0])
        articles_for_display_count = 1

        # Select regular articles
        for i in range(1, len(filtered_articles)):
            if articles_for_display_count >= MAX_ARTICLES_TO_DISPLAY:
                break
            regular_news_html_content += generate_news_card_html(filtered_articles[i])
            articles_for_display_count += 1
        
        if not regular_news_html_content: # If only one article was found, it's featured.
            regular_news_html_content = "<!-- No additional news articles available -->"


    # Read recent-news.html
    recent_news_file_path = os.path.join(os.path.dirname(__file__), '..', 'recent-news.html')
    try:
        with open(recent_news_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: {recent_news_file_path} not found.")
        return
    except Exception as e:
        print(f"Error reading {recent_news_file_path}: {e}")
        return
        
    # Update recent-news.html content
    # Update featured news section
    pattern_featured = r'(<div class="featured-news" id="smart-grid">)(.*?)(</div>)'
    # Ensure featured_article_html is defined, even if it's the placeholder comment
    if 'featured_article_html' not in locals() and not filtered_articles:
        featured_article_html = "<!-- Debug: No featured article available (initial check) -->"
    elif 'featured_article_html' not in locals() and filtered_articles:
         # This case should ideally not happen if logic is correct
        featured_article_html = generate_featured_news_html(filtered_articles[0])


    print(f"DEBUG: About to search for featured pattern. featured_article_html is: {featured_article_html[:200]}...") # Print first 200 chars
    
    updated_html_content = html_content
    if re.search(pattern_featured, updated_html_content, re.DOTALL):
        print("DEBUG: Found pattern_featured in HTML.")
        # The existing re.sub line for pattern_featured follows
        replacement_featured_html = f'\\1{featured_article_html.strip()}\\3'
        updated_html_content = re.sub(pattern_featured, replacement_featured_html, updated_html_content, count=1, flags=re.DOTALL)
    else:
        print("DEBUG: Did NOT find pattern_featured in HTML.")
        # The existing print error message for pattern_featured follows
        print("Error: <div class=\"featured-news\" id=\"smart-grid\"> not found in recent-news.html.")
        # Continue to update the other section if this one is missing

    # Update regular news grid section
    pattern_grid = r'(<div class="news-grid">)(.*?)(</div>)'
    replacement_grid_html = f'\\1{regular_news_html_content.strip()}\\3'

    if re.search(pattern_grid, updated_html_content, re.DOTALL):
        updated_html_content = re.sub(pattern_grid, replacement_grid_html, updated_html_content, count=1, flags=re.DOTALL)
    else:
        print("Error: <div class=\"news-grid\"> not found in recent-news.html.")
        # If both are missing, it's a bigger issue, but we'll try to write what we have.

    # Write the updated HTML back to recent-news.html
    try:
        with open(recent_news_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html_content)
        print("Successfully updated recent-news.html with the latest news.")
    except Exception as e:
        print(f"Error writing updated content to {recent_news_file_path}: {e}")

if __name__ == "__main__":
    main()
