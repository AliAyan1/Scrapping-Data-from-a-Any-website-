from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import json
import logging

class WebScraper:
    def __init__(self, headless=True):
        """Initialize the web scraper with Chrome driver"""
        chrome_options = Options()
        
        # Suppress Chrome logs and warnings
        chrome_options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if headless:
            chrome_options.add_argument("--headless")  # Run in background
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Suppress webdriver manager logs
        logging.getLogger('WDM').setLevel(logging.NOTSET)
        
        # Auto-download and setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to hide automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set implicit wait
        self.driver.implicitly_wait(10)
    
    def scrape_basic_elements(self, url):
        """Basic example: scrape common elements"""
        try:
            print(f"🔍 Scraping: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            data = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'headings': [],
                'links': [],
                'paragraphs': []
            }
            
            # Get all headings (h1, h2, h3, etc.)
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            data['headings'] = [h.text.strip() for h in headings if h.text.strip()]
            
            # Get all links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            data['links'] = [{'text': link.text.strip(), 'href': link.get_attribute('href')} 
                           for link in links if link.text.strip() and link.get_attribute('href')]
            
            # Get all paragraphs
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            data['paragraphs'] = [p.text.strip() for p in paragraphs if p.text.strip()]
            
            print(f"✅ Found: {len(data['headings'])} headings, {len(data['links'])} links, {len(data['paragraphs'])} paragraphs")
            return data
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            return None
    
    def scrape_quotes_demo(self):
        """Demo: Scrape quotes.toscrape.com - guaranteed to work!"""
        try:
            url = "https://quotes.toscrape.com/"
            print(f"🔍 Scraping quotes from: {url}")
            self.driver.get(url)
            
            quotes_data = []
            quotes = self.driver.find_elements(By.CLASS_NAME, "quote")
            
            for quote in quotes:
                quote_text = quote.find_element(By.CLASS_NAME, "text").text
                author = quote.find_element(By.CLASS_NAME, "author").text
                tags = [tag.text for tag in quote.find_elements(By.CLASS_NAME, "tag")]
                
                quotes_data.append({
                    'text': quote_text,
                    'author': author,
                    'tags': tags
                })
            
            print(f"✅ Successfully scraped {len(quotes_data)} quotes!")
            return quotes_data
            
        except Exception as e:
            print(f"❌ Error scraping quotes: {str(e)}")
            return []
    
    def scrape_with_interaction(self, url):
        """Example with user interactions (clicking, scrolling, etc.)"""
        try:
            print(f"🔍 Scraping with interaction: {url}")
            self.driver.get(url)
            
            # Example: Click a button to load more content
            try:
                load_more_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "load-more"))
                )
                load_more_button.click()
                time.sleep(2)  # Wait for content to load
                print("✅ Clicked 'load more' button")
            except:
                print("ℹ️  No 'load more' button found")
            
            # Example: Scroll to bottom to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print("✅ Scrolled to bottom")
            
            # Example: Fill out a form
            try:
                search_box = self.driver.find_element(By.NAME, "search")
                search_box.clear()
                search_box.send_keys("your search term")
                
                search_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                search_button.click()
                
                # Wait for results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
                )
                print("✅ Filled and submitted search form")
            except:
                print("ℹ️  No search form found")
            
            # Scrape the results
            results = []
            result_elements = self.driver.find_elements(By.CLASS_NAME, "result-item")
            
            for element in result_elements:
                result = {
                    'text': element.text.strip(),
                    'link': element.find_element(By.TAG_NAME, "a").get_attribute('href') if element.find_elements(By.TAG_NAME, "a") else None
                }
                results.append(result)
            
            print(f"✅ Found {len(results)} result items")
            return results
            
        except Exception as e:
            print(f"❌ Error during interaction scraping: {str(e)}")
            return []
    
    def scrape_table_data(self, url):
        """Example: scrape data from HTML tables"""
        try:
            print(f"🔍 Scraping table data from: {url}")
            self.driver.get(url)
            
            tables_data = []
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            if not tables:
                print("ℹ️  No tables found on this page")
                return []
            
            for i, table in enumerate(tables):
                table_data = {
                    'table_index': i,
                    'headers': [],
                    'rows': []
                }
                
                # Get headers
                headers = table.find_elements(By.CSS_SELECTOR, "thead th, tr:first-child th")
                if headers:
                    table_data['headers'] = [header.text.strip() for header in headers]
                
                # Get rows
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
                for row in rows[1:]:  # Skip header row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        table_data['rows'].append(row_data)
                
                tables_data.append(table_data)
                print(f"✅ Table {i+1}: {len(table_data['rows'])} rows, {len(table_data['headers'])} columns")
            
            return tables_data
            
        except Exception as e:
            print(f"❌ Error scraping table data: {str(e)}")
            return []
    
    def scrape_dynamic_content(self, url):
        """Example: handle dynamically loaded content"""
        try:
            print(f"🔍 Scraping dynamic content from: {url}")
            self.driver.get(url)
            
            # Wait for specific elements to load
            items = []
            
            # Method 1: Wait for specific elements
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dynamic-item"))
                )
                print("✅ Dynamic content loaded")
            except:
                print("ℹ️  No dynamic content with class 'dynamic-item' found")
            
            # Method 2: Keep scrolling until no new content loads
            print("🔄 Scrolling to load all content...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            
            while scroll_count < 3:  # Limit scrolls to prevent infinite loops
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1
            
            # Now scrape all the loaded content
            elements = self.driver.find_elements(By.CLASS_NAME, "dynamic-item")
            
            if not elements:
                # Try alternative selectors if dynamic-item doesn't exist
                elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='item'], .content-item, .post")
            
            for element in elements:
                item_data = {
                    'text': element.text.strip(),
                    'attributes': {
                        'id': element.get_attribute('id'),
                        'class': element.get_attribute('class'),
                        'data-value': element.get_attribute('data-value')
                    }
                }
                items.append(item_data)
            
            print(f"✅ Found {len(items)} dynamic items")
            return items
            
        except Exception as e:
            print(f"❌ Error scraping dynamic content: {str(e)}")
            return []
    
    def save_to_csv(self, data, filename):
        """Save scraped data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                if data and isinstance(data, list) and isinstance(data[0], dict):
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")
    
    def save_to_json(self, data, filename):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("🔒 Browser closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    print("🚀 Starting Web Scraper...")
    
    # Using context manager (recommended)
    with WebScraper(headless=True) as scraper:
        
        # Demo 1: Scrape quotes (guaranteed to work)
        print("\n" + "="*50)
        print("DEMO 1: Scraping Quotes")
        print("="*50)
        quotes_data = scraper.scrape_quotes_demo()
        if quotes_data:
            scraper.save_to_json(quotes_data, "quotes_data.json")
            print(f"Sample quote: {quotes_data[0]['text']} - {quotes_data[0]['author']}")
        
        # Demo 2: Basic scraping
        print("\n" + "="*50)
        print("DEMO 2: Basic Element Scraping")
        print("="*50)
        basic_data = scraper.scrape_basic_elements("https://httpbin.org/html")
        if basic_data:
            scraper.save_to_json(basic_data, "basic_data.json")
        
        # Demo 3: Table scraping (using a page that actually has tables)
        print("\n" + "="*50)
        print("DEMO 3: Table Scraping")
        print("="*50)
        table_data = scraper.scrape_table_data("https://www.w3schools.com/html/html_tables.asp")
        if table_data:
            scraper.save_to_json(table_data, "table_data.json")
        
        # Demo 4: Your original URLs
        print("\n" + "="*50)
        print("DEMO 4: Your Original URLs")
        print("="*50)
        builtwith_data = scraper.scrape_basic_elements("https://builtwith.com/")
        if builtwith_data:
            scraper.save_to_json(builtwith_data, "builtwith_data.json")
    
    print("\n🎉 All scraping completed!")