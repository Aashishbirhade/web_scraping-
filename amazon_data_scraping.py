from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Function: Initialize WebDriver
# Function: Initialize WebDriver
def initialize_driver():
    from selenium.webdriver.chrome.service import Service

    # Use Service object with ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.maximize_window()
    return driver


# Function: Log in to Amazon
# 

# Function: Log in to Amazon with OTP Handling
def login_to_amazon(driver, email, password):
    driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
    
    try:
        # Enter email
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(email)
        driver.find_element(By.ID, "continue").click()

        # Enter password
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()

        # Check for OTP input
        try:
            otp_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "auth-mfa-otpcode"))
            )
            otp_code = input("Enter the OTP sent to your registered mobile number: ")
            otp_element.send_keys(otp_code)
            driver.find_element(By.ID, "auth-signin-button").click()
            print("OTP submitted.")
        except:
            print("No OTP prompt detected, continuing...")

        # Verify login by checking for a specific element after login
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nav-orders")))
        print("Login successful!")
    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        exit()



# Function: Scrape Categories
def get_category_links(driver):
    driver.get("https://www.amazon.com/Best-Sellers/zgbs")
    categories = driver.find_elements(By.CSS_SELECTOR, ".zg_homeWidget a")
    print(categories)
    return [category.get_attribute("href") for category in categories[:10]]  # Get top 10 categories

# Function: Scrape Products in a Category
def scrape_category(driver, link):
    driver.get(link)
    category_name = driver.title
    data = []

    print(f"Scraping category: {category_name}")
    for _ in range(50):  # Adjust for the number of pages
        products = driver.find_elements(By.CSS_SELECTOR, ".zg-grid-general-faceout")
        print(len(products))
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                
                discount = (
                    product.find_element(By.CSS_SELECTOR, ".a-text-price").text
                    if product.find_elements(By.CSS_SELECTOR, ".a-text-price")
                    else "No discount"
                )
                rating = (
                    product.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                    if product.find_elements(By.CSS_SELECTOR, ".a-icon-alt")
                    else "No rating"
                )
                data.append({
                    "Category Name": category_name,
                    "Product Name": name,
                    "Price": price,
                    "Discount": discount,
                    "Rating": rating,
                })
            except Exception as e:
                print("Error scraping product:", e)

        # Pagination
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
            next_button.click()
            time.sleep(2)
        except:
            break

    return data
# Function: Save Data to File
def save_data_to_file(data, filename):
    
    df = pd.DataFrame(data)
    df.to_csv(f"{filename}.csv", index=False)
    df.to_json(f"{filename}.json", orient="records", indent=4)
    print(f"Data saved to {filename}.csv and {filename}.json")

# Main Function
if __name__ == "__main__":
    # Initialize
    driver = initialize_driver()

    # Credentials
    email = input("Enter your Amazon email: ")
    password = input("Enter your Amazon password: ")

    # Log in
    login_to_amazon(driver, email, password)

    # Get category links
    category_links = get_category_links(driver)

    # Scrape data for each category
    all_data = []
    for category_link in category_links:
        category_data = scrape_category(driver, category_link)
        all_data.extend(category_data)

    # Save data
    save_data_to_file(all_data, "amazon_best_sellers")

    # Quit browser
    driver.quit()
    print("Scraping complete!")

