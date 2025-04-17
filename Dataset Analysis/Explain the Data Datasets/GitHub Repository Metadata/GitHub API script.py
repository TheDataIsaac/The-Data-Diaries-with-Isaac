# --- Required Libraries ---
import requests
import time
import json
import os
import logging
import random # For jitter
import gzip   # For compression
import argparse # For command-line arguments
from datetime import datetime

# --- Default Configuration (can be overridden by command-line args) ---
DEFAULT_OUTPUT_DIR = "github_data_compressed"
DEFAULT_LOG_FILE = "github_scraper.log"
DEFAULT_FAILED_REPOS_FILE = "failed_repos.log"
DEFAULT_SUMMARY_FILE = "run_summary.json"

# Default date ranges if not specified via command line
DEFAULT_DATE_RANGES = [
    ("2024-07-01", "2024-09-30"),
    ("2024-04-01", "2024-06-30"),
    ("2024-01-01", "2024-03-31"),
    ("2023-10-01", "2023-12-31"),
    ("2023-07-01", "2023-09-30"),
    ("2023-04-01", "2023-06-30"),
    ("2023-01-01", "2023-03-31"),
    ("2022-10-01", "2022-12-31"),
    ("2022-07-01", "2022-09-30"),
    ("2022-04-01", "2022-06-30"),
    ("2022-01-01", "2022-03-31"),
    ("2021-10-01", "2021-12-31"),
    ("2021-07-01", "2021-09-30"),
    ("2021-04-01", "2021-06-30"),
    ("2021-01-01", "2021-03-31"),
]

# Search Parameters (Base query remains constant)
BASE_SEARCH_QUERY = '"data analysis" OR "data analytics" OR EDA OR "exploratory data analysis" language:Python'
SORT_BY = "updated"
ORDER = "desc"
RESULTS_PER_PAGE = 100
MAX_SEARCH_PAGES = 10

# Rate Limiting & Delays
DELAY_BETWEEN_REPOS = 1.5
DELAY_BETWEEN_SEARCH_PAGES = 10
MAX_RETRIES = 5
INITIAL_BACKOFF = 60
MAX_BACKOFF = 700 # ~11.6 minutes

# --- End Configuration ---

# --- Argument Parser Setup ---
parser = argparse.ArgumentParser(description="GitHub Repository Scraper")
parser.add_argument('--start_date', help='Start date for a single range (YYYY-MM-DD)', required=False)
parser.add_argument('--end_date', help='End date for a single range (YYYY-MM-DD)', required=False)
parser.add_argument('--output_dir', default=DEFAULT_OUTPUT_DIR, help='Directory to save output files')
parser.add_argument('--log_file', default=DEFAULT_LOG_FILE, help='Path to the log file')
parser.add_argument('--failed_log', default=DEFAULT_FAILED_REPOS_FILE, help='File to log repositories that failed processing')
parser.add_argument('--summary_file', default=DEFAULT_SUMMARY_FILE, help='File to save the run summary')

args = parser.parse_args()

# Determine date ranges to use
if args.start_date and args.end_date:
    DATE_RANGES_TO_PROCESS = [(args.start_date, args.end_date)]
    print(f"Processing single specified date range: {args.start_date} to {args.end_date}")
elif args.start_date or args.end_date:
    parser.error("--start_date and --end_date must be specified together.")
else:
    DATE_RANGES_TO_PROCESS = DEFAULT_DATE_RANGES
    print(f"Processing default date ranges defined in script.")

# Update config based on args
OUTPUT_DIR = args.output_dir
LOG_FILE = args.log_file
FAILED_REPOS_FILE = args.failed_log
SUMMARY_FILE = args.summary_file
OUTPUT_FILE_TEMPLATE = os.path.join(OUTPUT_DIR, "repos_{start_date}_to_{end_date}.jsonl.gz") # Added .gz

# --- Logging Setup ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('github_scraper')
logger.setLevel(logging.INFO)
logger.handlers.clear() # Clear existing handlers if re-running in same session

# File Handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# --- Helper Functions (handle_rate_limit_or_error, make_api_request - unchanged from previous version) ---
def handle_rate_limit_or_error(response, attempt):
    """Handles rate limits (403, 429) and server errors (5xx). Returns sleep time."""
    status_code = response.status_code
    headers = response.headers

    if status_code == 403 or status_code == 429:
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                sleep_time = int(retry_after) + 5
                logger.warning(f"Rate limit hit (Retry-After: {retry_after}s). Sleeping for {sleep_time} seconds.")
                return sleep_time
            except ValueError: pass

        backoff_time = min(INITIAL_BACKOFF * (2 ** attempt), MAX_BACKOFF)
        logger.warning(f"Rate limit hit (Status {status_code}). Attempt {attempt + 1}. Sleeping for {backoff_time} seconds (exponential backoff).")
        remaining = headers.get("X-RateLimit-Remaining")
        reset_time = headers.get("X-RateLimit-Reset")
        if remaining == '0' and reset_time:
            try:
                reset_timestamp = int(reset_time)
                sleep_duration = max(0, reset_timestamp - time.time()) + 5
                sleep_duration = min(sleep_duration, MAX_BACKOFF)
                logger.warning(f"Rate limit explicitly 0. Reset time: {datetime.fromtimestamp(reset_timestamp)}. Sleeping for {sleep_duration:.2f} seconds.")
                return sleep_duration
            except ValueError: pass
        return backoff_time
    elif 500 <= status_code < 600:
        backoff_time = min(INITIAL_BACKOFF * (2 ** attempt), MAX_BACKOFF)
        logger.warning(f"Server error (Status {status_code}). Attempt {attempt + 1}. Sleeping for {backoff_time} seconds.")
        return backoff_time
    return 0

def make_api_request(url, headers, params=None, is_optional_endpoint=False):
    """Makes a GitHub API request with retries and rate limit handling."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=45)
            if is_optional_endpoint and response.status_code == 404:
                logger.info(f"Optional endpoint {url} returned 404. Skipping.")
                return None
            sleep_duration = handle_rate_limit_or_error(response, attempt)
            if sleep_duration > 0:
                time.sleep(sleep_duration)
                continue
            response.raise_for_status()
            if response.status_code == 200:
                try: return response.json()
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from {url}. Response text: {response.text[:200]}...")
                    return None
            elif response.status_code == 204: return None
            logger.error(f"Unexpected status code {response.status_code} for {url}. Response: {response.text[:200]}...")
            return None
        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out for {url}. Attempt {attempt + 1}/{MAX_RETRIES}.")
            if attempt == MAX_RETRIES - 1: logger.error(f"Request failed after {MAX_RETRIES} timeouts: {url}"); return None
            time.sleep(min(INITIAL_BACKOFF * (2 ** attempt), MAX_BACKOFF))
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}. Attempt {attempt + 1}/{MAX_RETRIES}.")
            if attempt == MAX_RETRIES - 1: logger.error(f"Request failed permanently after {MAX_RETRIES} attempts: {url}"); return None
            time.sleep(min(INITIAL_BACKOFF * (2 ** attempt), MAX_BACKOFF))
    return None

# --- fetch_repo_details (unchanged from previous version, still uses make_api_request) ---
def fetch_repo_details(owner, repo, headers):
    """Fetches detailed data for a single repository using make_api_request."""
    logger.info(f"Fetching details for {owner}/{repo}...")
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    endpoints = {
        "metadata": (base_url, False), "languages": (f"{base_url}/languages", False),
        "topics": (f"{base_url}/topics", False), "contributors": (f"{base_url}/contributors?per_page=100&anon=1", False),
        "readme": (f"{base_url}/readme", True), "releases": (f"{base_url}/releases?per_page=100", False),
        "commits": (f"{base_url}/commits?per_page=100", False), "open_pulls": (f"{base_url}/pulls?state=open&per_page=1", False),
        "community_profile": (f"{base_url}/community/profile", True), "branches": (f"{base_url}/branches?per_page=100", False),
        "tags": (f"{base_url}/tags?per_page=100", False), "latest_release": (f"{base_url}/releases/latest", True),
        "workflows": (f"{base_url}/actions/workflows", False)
    }
    repo_data = {}
    for key, (url, is_optional) in endpoints.items():
        data = make_api_request(url, headers, is_optional_endpoint=is_optional)
        repo_data[key] = data
        if data is None and not is_optional:
            logger.warning(f"    Failed to fetch mandatory data for {key} ({owner}/{repo}). Some details might be missing.")
        time.sleep(0.2) # Small delay between detail fetches

    # --- Parsing Logic (Same as before, ensure safety against None) ---
    parsed_data = { "repo_name": None, "owner": owner, "repo": repo, "description": None, "github_url": f"https://github.com/{owner}/{repo}", "homepage": None,"topics": [], "license": None, "language": None, "languages_breakdown": None,"stars": 0, "forks": 0, "watchers": 0, "open_issues_count": 0,"contributors_count_page1": 0, "default_branch": None, "created_at": None, "updated_at": None,"pushed_at": None, "size_kb": 0, "visibility": None, "is_template": False, "archived": False,"disabled": False, "has_issues": False, "has_projects": False, "has_wiki": False,"has_pages": False, "has_downloads": False, "has_discussions": False,"recent_commits_count_page1": 0, "release_count_page1": 0, "has_readme": False,"readme_size_bytes": None, "open_pulls_count_page1": 0, "community_health_percentage": None,"community_has_description": None, "community_has_readme": None, "community_has_code_of_conduct": None,"community_has_contributing": None, "community_has_issue_template": None,"community_has_pull_request_template": None, "community_has_license": None,"branch_count_page1": 0, "tag_count_page1": 0, "latest_release_name": None,"latest_release_published_at": None, "workflow_count": 0, "fetch_timestamp": datetime.utcnow().isoformat() }
    meta = repo_data.get("metadata");
    if meta: parsed_data.update({ "repo_name": meta.get("name"), "github_url": meta.get("html_url"), "description": meta.get("description"), "homepage": meta.get("homepage"), "license": meta.get("license", {}).get("name") if meta.get("license") else None, "language": meta.get("language"), "stars": meta.get("stargazers_count", 0), "forks": meta.get("forks_count", 0), "watchers": meta.get("subscribers_count", 0), "open_issues_count": meta.get("open_issues_count", 0), "default_branch": meta.get("default_branch"), "created_at": meta.get("created_at"), "updated_at": meta.get("updated_at"), "pushed_at": meta.get("pushed_at"), "size_kb": meta.get("size", 0), "visibility": meta.get("visibility"), "is_template": meta.get("is_template", False), "archived": meta.get("archived", False), "disabled": meta.get("disabled", False), "has_issues": meta.get("has_issues", False), "has_projects": meta.get("has_projects", False), "has_wiki": meta.get("has_wiki", False), "has_pages": meta.get("has_pages", False), "has_downloads": meta.get("has_downloads", False), "has_discussions": meta.get("has_discussions", False) })
    else: logger.error(f"Metadata fetch failed for {owner}/{repo}. Skipping detail parsing."); return None # Crucial check

    languages = repo_data.get("languages");
    if languages: parsed_data["languages_breakdown"] = languages
    topics_data = repo_data.get("topics");
    if topics_data: parsed_data["topics"] = topics_data.get("names", [])
    contributors = repo_data.get("contributors");
    if contributors: parsed_data["contributors_count_page1"] = len(contributors)
    readme = repo_data.get("readme");
    if readme: parsed_data["has_readme"] = True; parsed_data["readme_size_bytes"] = readme.get("size")
    releases = repo_data.get("releases");
    if releases: parsed_data["release_count_page1"] = len(releases)
    commits = repo_data.get("commits");
    if commits: parsed_data["recent_commits_count_page1"] = len(commits)
    open_pulls = repo_data.get("open_pulls");
    if open_pulls: parsed_data["open_pulls_count_page1"] = len(open_pulls)
    community = repo_data.get("community_profile");
    if community: files = community.get("files", {}); parsed_data.update({"community_health_percentage": community.get("health_percentage"),"community_has_description": files.get("description") is not None, "community_has_readme": files.get("readme") is not None,"community_has_code_of_conduct": files.get("code_of_conduct") is not None, "community_has_contributing": files.get("contributing") is not None,"community_has_issue_template": files.get("issue_template") is not None, "community_has_pull_request_template": files.get("pull_request_template") is not None,"community_has_license": files.get("license") is not None})
    branches = repo_data.get("branches");
    if branches: parsed_data["branch_count_page1"] = len(branches)
    tags = repo_data.get("tags");
    if tags: parsed_data["tag_count_page1"] = len(tags)
    latest_release = repo_data.get("latest_release");
    if latest_release: parsed_data.update({"latest_release_name": latest_release.get("name") or latest_release.get("tag_name"),"latest_release_published_at": latest_release.get("published_at")})
    workflows = repo_data.get("workflows");
    if workflows: parsed_data["workflow_count"] = workflows.get("total_count", 0)

    logger.info(f"Finished processing details for {owner}/{repo}.")
    return parsed_data

# --- Updated Save Function with Compression ---
def save_record(record, filename):
    """Appends a JSON record to a compressed JSON Lines file (.jsonl.gz)."""
    try:
        # Use gzip.open with 'at' mode (append text)
        with gzip.open(filename, 'at', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False)
            f.write('\n') # Write newline character explicitly
        return True
    except IOError as e:
        logger.error(f"Error saving record to compressed file {filename}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving record to {filename}: {e}")
        return False

# --- Main Execution ---
def main():
    start_time = time.time()
    logger.info("Starting GitHub repository scraper with enhanced features.")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Failed repos log: {FAILED_REPOS_FILE}")
    logger.info(f"Summary file: {SUMMARY_FILE}")

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable not set. Exiting.")
        return

    HEADERS = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    processed_repo_urls = set() # Avoid duplicates within this run
    failed_repos = []           # Track repos that failed completely
    summary_records = []        # Track summary per date range
    total_repos_saved_overall = 0

    for start_date, end_date in DATE_RANGES_TO_PROCESS:
        range_start_time = time.time()
        logger.info(f"--- Processing date range: {start_date} to {end_date} ---")
        date_query = f"pushed:{start_date}..{end_date}"
        full_search_query = f"{BASE_SEARCH_QUERY} {date_query}"
        output_filename = OUTPUT_FILE_TEMPLATE.format(start_date=start_date, end_date=end_date)
        logger.info(f"Search Query: {full_search_query}")
        logger.info(f"Output File: {output_filename}")

        repos_found_in_range = 0
        repos_processed_in_range = 0
        repos_saved_in_range = 0

        for page in range(1, MAX_SEARCH_PAGES + 1):
            logger.info(f"Fetching search results page {page}/{MAX_SEARCH_PAGES} for range {start_date}-{end_date}...")
            search_params = { "q": full_search_query, "sort": SORT_BY, "order": ORDER, "per_page": RESULTS_PER_PAGE, "page": page }
            search_url = "https://api.github.com/search/repositories"

            results = make_api_request(search_url, HEADERS, params=search_params)

            if results is None:
                logger.error(f"Failed to fetch search results page {page} for range {start_date}-{end_date}. Skipping rest of this range.")
                break

            items = results.get("items", [])
            if not items:
                logger.info(f"No more items found on page {page}. Moving to next date range or finishing.")
                break

            current_page_found_count = len(items)
            repos_found_in_range += current_page_found_count
            logger.info(f"Found {current_page_found_count} repositories on page {page}. Total in range so far: {repos_found_in_range}.")
            if page == 1:
                 total_items_available = results.get("total_count", 0)
                 logger.info(f"Total matching repositories reported by GitHub for this query: {total_items_available} (will fetch max 1000).")

            for item in items:
                repos_processed_in_range += 1
                html_url = item.get("html_url")
                if not html_url: logger.warning("Search item missing 'html_url'. Skipping."); continue
                if html_url in processed_repo_urls: logger.info(f"Skipping already processed repository: {html_url}"); continue

                full_name = item.get("full_name")
                if full_name and '/' in full_name:
                    owner, repo_name = full_name.split('/', 1)
                    repo_identifier = f"{owner}/{repo_name}" # For logging failures

                    # Fetch detailed data
                    details = fetch_repo_details(owner, repo_name, HEADERS)

                    # Save data incrementally
                    if details:
                        details["query_date_range"] = f"{start_date}..{end_date}"
                        if save_record(details, output_filename):
                            repos_saved_in_range += 1
                            total_repos_saved_overall += 1
                            processed_repo_urls.add(html_url) # Mark as processed only if saved
                        else:
                             # If saving failed, log it as a failed repo for review
                             logger.error(f"Failed to save data for {repo_identifier} to {output_filename}. Adding to failed list.")
                             failed_repos.append(f"{repo_identifier} (Save Error)")
                    else:
                        # If fetch_repo_details returned None (critical failure)
                        logger.error(f"Failed to fetch critical details for {repo_identifier}. Adding to failed list.")
                        failed_repos.append(f"{repo_identifier} (Fetch Error)")


                    # Respect delay between processing repos, add jitter
                    sleep_time = DELAY_BETWEEN_REPOS + random.uniform(0, 0.5)
                    # logger.debug(f"Sleeping for {sleep_time:.2f} seconds...") # Verbose logging
                    time.sleep(sleep_time)

                else:
                    logger.warning(f"Could not parse owner/repo from full_name: {full_name}")

            # Delay before fetching the next search page
            if page < MAX_SEARCH_PAGES and current_page_found_count == RESULTS_PER_PAGE:
                 logger.info(f"Sleeping for {DELAY_BETWEEN_SEARCH_PAGES} seconds before fetching next search page...")
                 time.sleep(DELAY_BETWEEN_SEARCH_PAGES)
            else:
                 logger.info("Reached last page or end of results for this query.")
                 break # Exit page loop

        range_end_time = time.time()
        range_duration = range_end_time - range_start_time
        logger.info(f"--- Finished processing date range: {start_date} to {end_date}. Found: {repos_found_in_range}, Processed: {repos_processed_in_range}, Saved: {repos_saved_in_range}. Duration: {range_duration:.2f}s ---")

        # Add to summary record
        summary_records.append({
            "start_date": start_date,
            "end_date": end_date,
            "output_file": output_filename,
            "repos_found_github": results.get("total_count", 0) if 'results' in locals() and results else 'N/A', # Total github reported
            "repos_processed_script": repos_processed_in_range, # How many script attempted to process
            "repos_saved_successfully": repos_saved_in_range,
            "duration_seconds": round(range_duration, 2)
        })
        # Save summary incrementally too? Or just at the end is fine. Let's do it at the end.

    # --- Final Summary and Cleanup ---
    end_time = time.time()
    total_duration = end_time - start_time
    logger.info(f"--- Scraper finished overall run ---")
    logger.info(f"Total repositories saved across all ranges: {total_repos_saved_overall}")
    logger.info(f"Total unique URLs processed in this run: {len(processed_repo_urls)}")
    logger.info(f"Total execution time: {total_duration:.2f} seconds ({total_duration/3600:.2f} hours)")
    logger.info(f"Log file saved to: {LOG_FILE}")
    logger.info(f"Data saved to compressed files (.jsonl.gz) in directory: {OUTPUT_DIR}")

    # Save summary file
    try:
        with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(summary_records, f, indent=2, ensure_ascii=False)
        logger.info(f"Run summary saved to: {SUMMARY_FILE}")
    except IOError as e:
        logger.error(f"Error saving summary file {SUMMARY_FILE}: {e}")

    # Save failed repos file
    if failed_repos:
        logger.warning(f"Found {len(failed_repos)} repositories that failed processing. Saving list to: {FAILED_REPOS_FILE}")
        try:
            with open(FAILED_REPOS_FILE, 'w', encoding='utf-8') as f:
                for repo_id in failed_repos:
                    f.write(f"{repo_id}\n")
        except IOError as e:
            logger.error(f"Error saving failed repositories list to {FAILED_REPOS_FILE}: {e}")
    else:
        logger.info("No repositories failed permanently during processing.")

    logger.info("Reminder: Use 'tmux' or 'screen' for unattended execution.")
    logger.info("Note: Duplicates might exist across different date range files. Consider post-processing deduplication based on 'github_url'.")

if __name__ == "__main__":
    main()