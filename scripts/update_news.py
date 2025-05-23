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
    url = article.get('url', '#')
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

def main():
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
        'limit': 3
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

    # Generate HTML for news cards
    news_html_content = ""
    for article in articles:
        news_html_content += generate_news_card_html(article)

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
    # Using regex to find the div and replace its content.
    # This pattern captures the div tags and the content inside.
    # It's important to make the inner content capture non-greedy (.*?)
    pattern = r'(<div class="news-grid">)(.*?)(</div>)'
    
    # We want to replace the content *between* the tags
    # So the replacement string will be the opening tag, new content, and closing tag.
    replacement_html = f'\\1{news_html_content.strip()}\\3'

    if re.search(pattern, html_content, re.DOTALL):
        updated_html_content = re.sub(pattern, replacement_html, html_content, count=1, flags=re.DOTALL)
    else:
        print("Error: <div class=\"news-grid\"> not found in recent-news.html.")
        print("Please ensure the target div exists in the HTML file.")
        # For debugging, print the first 500 chars of what was read
        print("\nStart of recent-news.html content:")
        print(html_content[:500])
        print("------------------------------------")
        return

    # Write the updated HTML back to recent-news.html
    try:
        with open(recent_news_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html_content)
        print("Successfully updated recent-news.html with the latest news.")
    except Exception as e:
        print(f"Error writing updated content to {recent_news_file_path}: {e}")

if __name__ == "__main__":
    main()
