import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_data_for_product(classification, category, sub_category, prod):
    product_name = prod.find_element(By.TAG_NAME, "h4").text
                    
    product_format = ""
    product_container = prod.find_element(By.CLASS_NAME, "product-format")
    product_container_spans = product_container.find_elements(By.TAG_NAME, "span")
    for span in product_container_spans:
        product_format += " " + span.text
    
    product_price = prod.find_element(By.CLASS_NAME, "product-price__unit-price").text
    product_unit = prod.find_element(By.CLASS_NAME, "product-price__extra-price").text

    return {"classification": classification,
            "category": category,
            "sub_category": sub_category,
            "product_name" : product_name,
            "product_format": product_format,
            "product_price": product_price,
            "product_unit": product_unit
            }


def get_product_prices():

    data = []
    URL = "https://tienda.mercadona.es/categories"

    s = Service("D://selenium-geckodriver//geckodriver.exe")
    driver = webdriver.Firefox(service=s)
    
    agent= driver.execute_script("return navigator.userAgent")
    print("User Agent: ", agent)

    driver.get(URL)

    # introudce postal code as shown in this post
    # https://stackoverflow.com/questions/18557275/how-to-locate-and-insert-a-value-in-a-text-box-input-using-python-selenium
    # postal_code_form = driver.find_element(By.CLASS_NAME, "postal-code-checker")

    # sleep to make sure that the postal code form is loaded and can be accessed
    time.sleep(1)
    
    # create function wait till 10s to load all elements needed
    def wait_and_find_elements(locate_by, selector):
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((locate_by, selector))
            )
    # create function wait till 10s to load element
    def wait_and_find_element(locate_by, selector):
        return WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((locate_by, selector))
            )

    input_postal_code = wait_and_find_element(By.NAME, 'postalCode')
    input_postal_code.send_keys("08009")
    input_postal_code.send_keys(Keys.ENTER)

    # click all classification buttons in the menu   
    section_classification = wait_and_find_elements(By.CLASS_NAME, "category-menu__item")
    for i in range(len(section_classification)):
        time.sleep(1)
        
        classification_to_click = wait_and_find_elements(By.CLASS_NAME, "category-menu__item")[i]
        classification_button_to_click = classification_to_click.find_element(By.TAG_NAME, "button")
        driver.execute_script("arguments[0].click();", classification_button_to_click)
        classification = classification_to_click.find_element(By.TAG_NAME, "label").text
        
        # click all category buttons in the menu
        time.sleep(1)
        category_button = wait_and_find_elements(By.CLASS_NAME, "category-menu__item")[i].find_elements(By.CLASS_NAME, "category-item__link")
        for j in range(len(category_button)):
            time.sleep(1)
            category_button_to_click = wait_and_find_elements(By.CLASS_NAME, "category-item__link")[j]
            driver.execute_script("arguments[0].click();", category_button_to_click)

            ### SCRAPPING OF ONE PAGE TO GET ALL THE PRODUCTS

            # wait out of respect
            time.sleep(1)

            # h1 contains the category
            category = wait_and_find_element(By.TAG_NAME, "h1").text
            
            # h2/h3 contains the subcategories
            sections = wait_and_find_elements(By.CLASS_NAME, "section")

            for sect in sections:
                # check if h2 exists - some page structures, sub categories are in h2
                if len(sect.find_elements(By.TAG_NAME, "h2"))>0:
                    sub_category = sect.find_element(By.TAG_NAME, "h2").text
                # check if h3 exists - some page structures, sub categories are in h3
                elif len(sect.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "h3"))>0:
                    parent = sect.find_element(By.XPATH, "..")
                    sub_category = parent.find_element(By.TAG_NAME, "h3").text


                products = sect.find_elements(By.CLASS_NAME, "product-cell")
                
                for prod in products:
                    prod_data = get_data_for_product(classification, category, sub_category, prod)
                    data.append(prod_data)

                    # print(classification, "-", category, " - ", sub_category, " - ", prod_data['product_name'], " - ", prod_data['product_format'], " - ", 
                    #       prod_data['product_price'], " - ", prod_data['product_unit'])

    driver.close()
    driver.quit()

    return data