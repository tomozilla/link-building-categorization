import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Move this function to the top, before it's used
def write_to_log(message, is_new_domain=False):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(f'semrush_processing_{datetime.now().strftime("%Y%m%d")}.log', 'a', encoding='utf-8') as f:
        if is_new_domain:
            f.write("\n" + "="*80 + "\n")  # Add separator line
            f.write(f"[{timestamp}] Starting new domain processing\n")
        f.write(f"[{timestamp}] {message}\n")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# SEMrush credentials
SEMRUSH_EMAIL = os.getenv('SEMRUSH_EMAIL')
SEMRUSH_PASSWORD = os.getenv('SEMRUSH_PASSWORD')
LINK_BUILDING_TOOL_URL = os.getenv('LINK_BUILDING_TOOL_URL')

# --------------------------------------------------
# 1. Setup: Define login credentials and project URL
# --------------------------------------------------

# --------------------------------------------------
# 2. Define classification logic
# --------------------------------------------------


def classify_strategy_with_gpt(domain, url, snippet_text, page_type_text):
    prompt = f"""
You are an expert link-building strategist.

Based on the following information, categorize this prospect into one of these EXACT outreach strategies (use exactly these names, no punctuation):
- Manual link
- Directory/Catalogue
- Add link to article
- Product review
- Link from mention
- Guest post
- Recover lost backlinks

Context:
- Domain: {domain}
- URL: {url}
- Snippet: {snippet_text}
- Page Type: {page_type_text}

Explain briefly why, then give ONLY the exact category name from the list above, with no punctuation or quotes.
"""

    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3)

        reply = response.choices[0].message.content
        print("GPT Response:", reply)
        write_to_log(f"GPT Response:\n{reply}")

        # Extract final category from response
        lines = [line.strip() for line in reply.splitlines() if line.strip()]
        if lines:
            return lines[-1]  # Return the last non-empty line
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Manual link"  # fallback

    return "Manual link"  # fallback


def classify_outreach_strategy(snippet_text, page_type_text):
    """
    Simple example classification function.
    Inspect snippet/page type to decide on outreach strategy.

    Return one of the categories:
    - "Manual link"
    - "Directory/Catalogue"
    - "Add link to article"
    - "Product review"
    - "Link from mention"
    - "Guest post"
    - "Recover lost backlinks"
    """

    snippet_lower = snippet_text.lower()
    page_type_lower = page_type_text.lower()

    # Example logic (very naive)
    if "blog" in page_type_lower or "blog" in snippet_lower:
        # If the page is clearly a blog, we might do a Guest post or Add link
        return "Guest post"
    elif "directory" in snippet_lower or "catalog" in snippet_lower:
        return "Directory/Catalogue"
    elif "review" in snippet_lower:
        return "Product review"
    elif "mention" in snippet_lower:
        return "Link from mention"
    else:
        # Fallback if nothing matches
        return "Add link to article"

# --------------------------------------------------
# 3. Initialize Selenium WebDriver
# --------------------------------------------------
def init_driver():
    # Adjust options as needed
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# --------------------------------------------------
# 4. Log in to Semrush
# --------------------------------------------------
def login_to_semrush(driver):
    driver.get("https://www.semrush.com/login/")

    # Wait for the login form to appear
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    # Fill out the email and password
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    email_field.send_keys(SEMRUSH_EMAIL)
    password_field.send_keys(SEMRUSH_PASSWORD)

    # Click the login button
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    # Wait until we are logged in (you may need to wait for a specific element)
    time.sleep(5)  # Simple sleep; ideally, wait for a post-login element

# --------------------------------------------------
# 5. Process each prospect
# --------------------------------------------------
def process_prospects(driver):
    # Navigate to the Link Building Tool page
    driver.get(LINK_BUILDING_TOOL_URL)

    # Wait for the prospects table to load
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='prospects-table_row']"))
        )
    except TimeoutException:
        print("Timeout waiting for the prospects table. Check your project URL or network.")
        return

    while True:
        try:
            from selenium.common.exceptions import NoSuchElementException

            # Always get the first row since rows shift up after processing
            rows = driver.find_elements(By.CSS_SELECTOR, "[data-test='prospects-table_row']")
            if not rows:  # No more rows to process
                print("No more prospects to process")
                break

            row = rows[0]  # Always process the first row

            # 1) Extract the domain text
            try:
                domain_element = row.find_element(By.CSS_SELECTOR, "[data-lbt-test='domain_url-domain']")
                domain_text = domain_element.text.strip()
            except NoSuchElementException:
                print("Domain element not found.")
                domain_text = ""

            # 2) Extract snippet text
            try:
                snippet_element = row.find_element(By.CSS_SELECTOR, "[data-lbt-test='domain_url-snippet']")
                snippet_text = snippet_element.text.strip()
            except NoSuchElementException:
                print("Snippet element not found.")
                snippet_text = ""

            # 3) Extract page type text
            try:
                page_type_element = row.find_element(By.CSS_SELECTOR, "[name='urlType']")
                page_type_text = page_type_element.text.strip()
            except NoSuchElementException:
                print("Page type element not found.")
                page_type_text = ""

            # 3.5) Extract URL text
            try:
                url_element = row.find_element(By.CSS_SELECTOR, "[data-lbt-test='url-text']")
                url_text = url_element.text.strip() if url_element else ""
            except NoSuchElementException:
                print("URL element not found.")
                url_text = ""

            # Continue with your processing or classification...


            # Use OpenAI to classify
            write_to_log(f"Domain: {domain_text} | URL: {url_text} | Snippet: {snippet_text} | Page Type: {page_type_text}", is_new_domain=True)
            strategy = classify_strategy_with_gpt(domain_text, url_text, snippet_text, page_type_text)

            # Clean up the strategy string
            strategy = strategy.strip().strip('"').strip("'").rstrip('.')  # Remove quotes and trailing period

            print(f"Domain: {domain_text} | Clean Strategy: {strategy}")
            write_to_log(f"Domain: {domain_text} | Clean Strategy: {strategy}")

            # 4) Select the outreach strategy from the dropdown
            strategy_button = row.find_element(
                By.CSS_SELECTOR, "button[data-lbt-test='move-to-button']"
            )
            strategy_button.click()

            # Wait for dropdown and verify it's visible
            dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-lbt-test='move-to-dropdown']"))
            )

            # Update the selector to match the actual structure
            dropdown_items = driver.find_elements(
                By.CSS_SELECTOR,
                "div[data-lbt-test='move-to-strategies_item'] div.___SFlex_1rng6_gg_ span[data-ui-name='Tooltip.Trigger']"
            )

            # Click the item that matches our chosen strategy
            strategy_found = False
            for item in dropdown_items:
                item_text = item.text.strip()
                print(f"Comparing '{item_text}' with '{strategy}'")
                write_to_log(f"Comparing '{item_text}' with '{strategy}'")
                if item_text.lower() == strategy.lower():
                    driver.execute_script("arguments[0].click();", item)
                    strategy_found = True
                    time.sleep(2)  # Wait for row to be removed
                    break

            if not strategy_found:
                print(f"Could not find strategy '{strategy}' in dropdown for {domain_text}")
                write_to_log(f"Could not find strategy '{strategy}' in dropdown for {domain_text}")
                # Click outside to close dropdown before continuing
                driver.find_element(By.TAG_NAME, "body").click()
                time.sleep(1)
                continue

        except Exception as e:
            print(f"Error processing row: {e}")
            # If there's an error, we'll try the next iteration
            time.sleep(1)
            continue

# --------------------------------------------------
# 6. Main routine
# --------------------------------------------------
def main():
    driver = init_driver()
    try:
        login_to_semrush(driver)
        process_prospects(driver)
    finally:
        print("Done processing prospects. Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()
