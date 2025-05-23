# Project Repository

This repository contains the files for the project website.

## Automated News Updates

The `recent-news.html` page is automatically updated daily with the latest news stories related to US news. This process is handled by a Python script and a GitHub Actions workflow.

### How it Works
1.  **News Fetching Script**: A Python script located at `scripts/update_news.py` is responsible for:
    *   Fetching the latest top news articles from The News API (`https://www.thenewsapi.com`).
    *   Parsing the API response.
    *   Generating HTML content for each news article (title, description, image, link).
    *   Updating the `<div class="news-grid">` section in the `recent-news.html` file with these new articles.

2.  **GitHub Actions Workflow**: A GitHub Actions workflow defined in `.github/workflows/update-news.yml`:
    *   Runs automatically every day at 00:00 UTC.
    *   Can also be triggered manually.
    *   Sets up a Python environment and installs necessary dependencies (`requests`, `python-dotenv`).
    *   Executes the `scripts/update_news.py` script.
    *   Commits and pushes any changes made to `recent-news.html` back to the repository.

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
    *   Navigate to the project root in your terminal and run the script using:
        ```bash
        python scripts/update_news.py
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
