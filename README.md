# Project Repository

This repository contains the files for the project website.

## Automated News Updates

The `recent-news.html` (US Political News) and `international-news.html` (General International News) pages are automatically updated daily with the latest news stories. This process is handled by a Python script and a GitHub Actions workflow.

### How it Works
1.  **News Fetching Script**: A Python script located at `scripts/update_news.py` is now configurable using command-line arguments. Its core responsibilities include:
    *   Fetching the latest top news articles from The News API (`https://www.thenewsapi.com`) based on configured parameters (locale, categories).
    *   Parsing the API response.
    *   Filtering articles to ensure they have necessary content (URL, image).
    *   Generating HTML content for a single featured article and a grid of subsequent regular news articles (up to a configurable maximum, e.g., 10 total).
    *   Updating the specified HTML file by replacing content within a designated featured news div (identified by a CSS ID or class) and a designated news grid div (`<div class="news-grid">`).

2.  **GitHub Actions Workflow**: A GitHub Actions workflow defined in `.github/workflows/update-news.yml`:
    *   Runs automatically every day at 00:00 UTC.
    *   Can also be triggered manually.
    *   Sets up a Python environment and installs necessary dependencies (`requests`, `python-dotenv`).
    *   Executes the `scripts/update_news.py` script twice:
        *   Once with parameters to update `recent-news.html` with US political news.
        *   Once with parameters to update `international-news.html` with general international news.
    *   Commits and pushes any changes made to `recent-news.html` and `international-news.html` back to the repository if they are modified.

### Local Setup for Manual Script Execution

If you wish to run the news update script manually locally:

1.  **Create an Environment File**:
    *   In the root directory of the project, create a file named `.env`.
2.  **Add API Token**:
    *   Open the `.env` file and add your API token from The News API in the following format:
        ```
        NEWS_API_TOKEN=YOUR_ACTUAL_API_TOKEN_HERE
        ```
    *   The `.env` file is included in `.gitignore` and should not be committed to the repository.
3.  **Run the Script**:
    *   Ensure you have Python 3 and the `requests` and `python-dotenv` libraries installed (`pip install requests python-dotenv`).
    *   The script is now configurable via command-line arguments. Here's how to run it manually:

        **Arguments:**
        *   `--html_file_name`: (Required) Name of the HTML file (e.g., "recent-news.html").
        *   `--api_locale`: (Optional) API `locale` parameter. Defaults to "us". For multiple, use comma-separated (e.g., "gb,ca,au").
        *   `--api_categories`: (Optional) API `categories` parameter. Defaults to no category. For multiple, use comma-separated (e.g., "politics,technology").
        *   `--featured_div_identifier`: (Required) CSS selector for the featured news div (ID prefixed with '#' e.g., "#smart-grid", or class prefixed with '.' e.g., ".featured-news").
        *   `--max_articles`: (Optional) Total number of articles to display (1 featured + rest in grid). Defaults to 10.

        **Example for Recent News (US Political):**
        ```bash
        python scripts/update_news.py --html_file_name "recent-news.html" --api_locale "us" --api_categories "politics" --featured_div_identifier "#smart-grid" --max_articles 10
        ```

        **Example for International News (General):**
        ```bash
        python scripts/update_news.py --html_file_name "international-news.html" --api_locale "gb,ca,au,de,fr,jp" --featured_div_identifier ".featured-news" --max_articles 10
        ```

### GitHub Actions Configuration

For the automated workflow to function correctly in your own fork or version of this repository, you need to configure a GitHub Secret:

1.  **Navigate to Repository Settings**: Go to your repository on GitHub, then click on "Settings".
2.  **Secrets and Variables**: In the left sidebar, under "Security", click on "Secrets and variables", then "Actions".
3.  **New Repository Secret**:
    *   Click the "New repository secret" button.
    *   Name the secret: `NEWS_API_TOKEN`
    *   Value: Paste your actual API token from The News API.
    *   Click "Add secret".

This will allow the GitHub Action to securely access the API token when it runs.

## Note on HTML File Cleanliness
If these HTML files (`recent-news.html`, `international-news.html`) have been processed by many developmental versions of the update script, they might have accumulated duplicated content *outside* the main sections managed by the script. For the cleanest possible display, a one-time manual review and cleanup of these HTML files in the repository to remove any such orphaned duplicated blocks is recommended. The script itself is designed to cleanly replace content *within* the designated featured and grid divs.
