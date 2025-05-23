import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re
import argparse

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

def main(args):
    # MAX_ARTICLES_TO_DISPLAY is now args.max_articles
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
        'language': 'en', # Assuming this is always 'en'
        'limit': 30 # Still fetch more to filter
    }
    if args.api_locale: # Add if provided
        params['locale'] = args.api_locale
    if args.api_categories: # Add if provided
        params['categories'] = args.api_categories

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
            if articles_for_display_count >= args.max_articles:
                break
            regular_news_html_content += generate_news_card_html(filtered_articles[i])
            articles_for_display_count += 1
        
        if not regular_news_html_content: # If only one article was found, it's featured.
            regular_news_html_content = "<!-- No additional news articles available -->"


    # Read HTML file
    html_file_path = os.path.join(os.path.dirname(__file__), '..', args.html_file_name)
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: {html_file_path} not found.")
        return
    except Exception as e:
        print(f"Error reading {html_file_path}: {e}")
        return
        
    # Update recent-news.html content
    updated_html_content = html_content

    # Ensure featured_article_html and regular_news_html_content are defined
    # (they should be from the logic above, handling cases with/without filtered_articles)
    if 'featured_article_html' not in locals():
        featured_article_html = "<!-- Fallback: No featured article generated -->"
    if 'regular_news_html_content' not in locals():
        regular_news_html_content = "<!-- Fallback: No regular news generated -->"

    # Update featured news section
    print(f"DEBUG_FEATURED_HTML_CONTENT:\n{featured_article_html}\nEND_DEBUG_FEATURED_HTML_CONTENT")
    
    pattern_featured = ""
    if args.featured_div_identifier.startswith('#'):
        # ID based identifier
        div_id = args.featured_div_identifier[1:]
        # This regex looks for a div that has the class "featured-news" AND the specified ID.
        # It allows for other classes to be present as well.
        pattern_featured = rf'(<div\s+(?:[^>]*\s)?class="[^"]*featured-news[^"]*"\s+(?:[^>]*\s)?id="{div_id}"[^>]*>)(.*?)(</div>)'
    elif args.featured_div_identifier.startswith('.'):
        # Class based identifier
        div_class = args.featured_div_identifier[1:]
        # This regex looks for a div that has the specified class. 
        # It allows for other classes to be present.
        # It will target the first such div.
        pattern_featured = rf'(<div\s+(?:[^>]*\s)?class="[^"]*{div_class}[^"]*"[^>]*>)(.*?)(</div>)'
    else:
        print(f"ERROR: Invalid featured_div_identifier format: {args.featured_div_identifier}. Must start with # or .")
        # Potentially exit or use a default, but for now, let it fail finding the pattern.
        pattern_featured = None # This will cause re.search to fail if identifier is malformed

    if pattern_featured and re.search(pattern_featured, updated_html_content, re.DOTALL):
        replacement_featured = f'\\1{featured_article_html.strip()}\\3'
        updated_html_content = re.sub(pattern_featured, replacement_featured, updated_html_content, count=1, flags=re.DOTALL)
    else:
        print("ERROR: Did not find featured news div for update.")

    # Update regular news grid section
    print(f"DEBUG_REGULAR_NEWS_HTML_CONTENT_LENGTH: {len(regular_news_html_content)}")
    print(f"DEBUG_REGULAR_NEWS_HTML_CONTENT_SNIPPET:\n{regular_news_html_content[:500]}\nEND_DEBUG_REGULAR_NEWS_HTML_CONTENT_SNIPPET")
    print(f"DEBUG_REGULAR_NEWS_HTML_CONTENT:\n{regular_news_html_content}\nEND_DEBUG_REGULAR_NEWS_HTML_CONTENT")
    pattern_grid = r'(<div class="news-grid">)(.*?)(</div>)'
    replacement_grid = f'\\1{regular_news_html_content.strip()}\\3'
    if re.search(pattern_grid, updated_html_content, re.DOTALL):
        updated_html_content = re.sub(pattern_grid, replacement_grid, updated_html_content, count=1, flags=re.DOTALL)
    else:
        print("ERROR: Did not find news grid div for update.")

    # Write the updated HTML back to the file
    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html_content)
        print(f"Successfully updated {args.html_file_name} with the latest news.")
    except Exception as e:
        print(f"Error writing updated content to {html_file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update HTML file with the latest news articles.")
    parser.add_argument('--html_file_name', type=str, required=True, help='Name of the HTML file to update (e.g., "recent-news.html")')
    parser.add_argument('--api_locale', type=str, default="us", help='Locale for The News API (e.g., "us", "gb")')
    parser.add_argument('--api_categories', type=str, default="", help='Comma-separated categories for The News API (e.g., "politics,technology")')
    parser.add_argument('--featured_div_identifier', type=str, required=True, help='Identifier for the featured news div (e.g., "#smart-grid" or ".featured-news")')
    parser.add_argument('--max_articles', type=int, default=10, help='Maximum number of articles to display (including featured)')
    
    parsed_args = parser.parse_args()
    main(parsed_args)
