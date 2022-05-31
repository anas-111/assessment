from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import psycopg2


connection = psycopg2.connect(host="host.docker.internal", port=49153, database="postgres", user="postgres", password="postgrespw")
cursor = connection.cursor()
print(connection)
def create_table():
    sql = '''CREATE TABLE IF NOT EXISTS public.details(
        ean TEXT,
        product_title TEXT,
        img_link TEXT,
        reviews_count TEXT,
        stars TEXT,
        variants TEXT,
        old_price TEXT,
        current_price TEXT,
        label TEXT,
        art_nr TEXT,
        alter TEXT,
        konsistenz TEXT,
        hauttyp TEXT,
        eigenschaft TEXT,
        produktauszeichnung TEXT,
        produkttyp TEXT,
        anwendungsbereich TEXT,
        description TEXT
    )'''
    cursor.execute(sql)
    cursor.execute('commit;')
    connection.commit()
    print("Table Created")

def insert_data(ean, product_title, img_link, reviews_count, stars, variants, old_price, current_price, label, art_nr, alter, konsistenz, hauttyp, eigenschaft, produktauszeichnung, produkttyp, anwendungsbereich, description):
    cursor = connection.cursor()
    row = (ean, product_title, img_link, reviews_count, stars, variants, old_price, current_price, label, art_nr, alter, konsistenz, hauttyp, eigenschaft, produktauszeichnung, produkttyp, anwendungsbereich, description)
    sql = '''INSERT INTO public.details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    cursor.execute(sql, row)
    cursor.execute('commit;')
    connection.commit()
    print('row inserted')

def create_driver_handler(driver_path=ChromeDriverManager().install()):
    '''
    creates a browser instance for selenium, 
    it adds some functionalities into the browser instance
    '''
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("log-level=3")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={user_agent}')
    # chrome_options.add_argument("--remote-debugging-port=9222");
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--proxy-server='direct://'")
    # chrome_options.add_argument("--proxy-bypass-list=*")
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True 
    capabilities['acceptInsecureCerts'] = True
    # the following two options are used to take out the chrome browser infobar
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    # chrome_options.add_experimental_option(
    #     "excludeSwitches", ["enable-automation"])
    driver_instance = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options, desired_capabilities=capabilities)
    driver_instance.implicitly_wait(10)
    return driver_instance

def product_details(drv):
    try:
    # sleep(600)
        sleep(1)

        ## Will find the name of the product
        title = drv.find_element(By.CLASS_NAME, 'header-name').text

        ## Extracting EAN numbers from the api request made
        ean = ''
        ele = drv.find_element(By.ID, 'state-body')
        list = (ele.get_attribute('innerHTML').split(','))
        j = 0
        for i in list:
            if(title in i):
                break
            j+=1
        if((j+1) < len(list)):
            ean = (list[j+1])[1::][:-1]

        ## Extracting link of main image
        images = drv.find_elements(by=By.TAG_NAME, value='img')
        img_link = images[0].get_attribute('src')

        ## Number of reviews
        count_reviews = ((drv.find_element(By.CLASS_NAME, 'product-detail-header__feedback--review-count').text)[1::])[:-1]

        star_block = driver.find_element(By.CLASS_NAME, 'rating-stars')
        lst = star_block.find_elements(By.ID, 'Ebene_1')

        stars = str(5 - len(lst))

        variants_row = drv.find_elements(By.CLASS_NAME, 'product-detail__variant-row--spread-content')
        variant = ''
        old_price =''
        current_price = ''
        if(len(variants_row) > 0):
            for i in variants_row:
                variant += (' ' + i.find_element(By.CLASS_NAME, 'product-detail__variant-name').text)
                if(len(i.find_elements(By.CLASS_NAME, 'product-price__strikethrough')) > 0):
                    old_price += ' ' + i.find_element(By.CLASS_NAME, 'product-price__strikethrough').text
                else:
                    old_price += ' nil'
                if(len(i.find_elements(By.CLASS_NAME, 'product-price__discount')) > 0):
                    current_price += ' ' + i.find_element(By.CLASS_NAME, 'product-price__discount').text
                else:
                    current_price += ' ' + i.find_element(By.CLASS_NAME, 'product-price__base').text
            variant = variant[1::]
            old_price = old_price[1::]
            current_price = current_price[1::]

        ## label information
        labels = drv.find_elements(By.CLASS_NAME, 'product-label__name')
        label = ''
        for i in labels:
            label += ' ' + i.text
        label = label[1::]
        
        ## Getting all specific product details
        items = drv.find_elements(By.CLASS_NAME, 'classification__item')

        art_nr, alter, konsistenz, hauttyp, eigenschaft, produktauszeichnung, produkttyp, anwendungsbereich = '', '','','','','','',''
        for i in range(0, len(items)):
            if(items[i].text == 'Art-Nr.'):
                art_nr = items[i+1].text
            elif(items[i].text == 'Alter'):
                alter = items[i+1].text
            elif(items[i].text == 'Konsistenz'):
                konsistenz = items[i+1].text
            elif(items[i].text == 'Hauttyp'):
                hauttyp = items[i+1].text
            elif(items[i].text == 'Eigenschaft'):
                eigenschaft = items[i+1].text
            elif(items[i].text == 'Produktauszeichnung'):
                produktauszeichnung = items[i+1].text
            elif(items[i].text == 'Produkttyp'):
                produkttyp = items[i+1].text
            elif(items[i].text == 'Anwendungsbereich'):
                anwendungsbereich = items[i+1].text
        
        ## Handling the pop up
        button = False
        button = drv.find_element(By.XPATH, "//button[contains(text(), 'Alle erlauben')]")
        if(button):
            button.click()
    
        
        sleep(0.5)
        extend = drv.find_elements(By.CLASS_NAME, 'truncate__toggle')
        if(len(extend) > 0):
            try:
                actions = ActionChains(drv)
                actions.move_to_element(extend[0]).perform()
                extend[0].click()
                div = drv.find_element(By.CLASS_NAME, 'truncate__html-container')
                description = div.text
            except: 
                div = drv.find_element(By.CLASS_NAME, 'product-details__description')
                description = div.text
        else:
            div = drv.find_element(By.CLASS_NAME, 'product-details__description')
            # driver.execute_script("arguments[0].scrollIntoView();", div)
            description = div.text
        
        ## Inserting the extracted data into database
        insert_data(ean, title, img_link, count_reviews, stars, variant, old_price, current_price, label, art_nr, alter, konsistenz, hauttyp, eigenschaft, produktauszeichnung, produkttyp, anwendungsbereich, description)
        print("Row Inserted")
        ## Printing all the values extracted
        print(stars)
        print(ean)
        print(img_link)
        print(count_reviews)
        print(title)
        print(variant)
        print(old_price)
        print(current_price)
        print(label)
        print(description)

    except Exception as e:
        print(e)
        

def page_traverse(driver):
    ## Handling the pop - up
    button = False
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Alle erlauben')]")
    if(button):
        button.click()
    j = 0
    while(True):
        ## Searching for products on the category page
        elements = driver.find_elements(by=By.CLASS_NAME, value='product-grid-column')
        i = 0
        while(i < len(elements)):
            driver.execute_script("arguments[0].scrollIntoView();", elements[i])
            link = elements[i].find_element(by = By.CLASS_NAME, value = 'link')
            drv = create_driver_handler()

            ## Opening the product page
            drv.get(link.get_attribute('href'))
            product_details(drv)
            drv.close()
            i+=1
            elements = driver.find_elements(by=By.CLASS_NAME, value='product-grid-column')
        driver.execute_script("arguments[0].scrollIntoView();", elements[-1])
        # arrows = driver.find_elements(By.CLASS_NAME, 'pagination__arrow')
        arrows = driver.find_elements_by_xpath('//a[@class="link link--text pagination__arrow active"]')
        print(len(arrows))
        if((j!=0 and len(arrows)==2) or (j==0 and len(arrows)==1)):
            link = arrows[-1].get_attribute('href')
            driver.get(link)
            j+=1
        else:
            print("END OF PAGES")
            break
        


driver = create_driver_handler()
driver.get('https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308')
create_table()
page_traverse(driver)