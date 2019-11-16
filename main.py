from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import csv
import firebase_admin
from firebase_admin import credentials,db
import os
import pandas as pd
import difflib as diff
count = 0
'''
    def make_lines_set(txt):
        f = open(txt)
        lines = f.readlines()
        sets = set(lines)
        f.close()
        return sets
    results = bigs.difference(smalls)
    for result in results:
        print(result)
'''
cred = credentials.Certificate("mercari-price-firebase-adminsdk-hi90f-b7e0d246d7.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mercari-price.firebaseio.com/',
    'databaseAuthVariableOverride': {
        'uid': 'my-service-worker'
    }
    })
users_ref = db.reference('/data')
dbres = users_ref.get()
with open('./index.html', 'w') as f:
    print('<head><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"><script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script><script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script></head><div class="container"><div class="row">',file=f)
    f.close()
def main():
    driver = webdriver.Chrome('./chromedriver')
    
    set_search_conditions(driver)
    get_item(driver)

    driver.close()
    with open('index.html', 'a') as f:
        print('</div></div>',file=f)


def set_search_conditions(driver):
    driver.get('https://www.mercari.com/jp/')
    s = driver.find_elements_by_name('keyword')
    s[1].send_keys('Galaxy S8')
    s[1].send_keys(Keys.ENTER)
    category_root = Select(driver.find_element_by_name('category_root'))
    category_root.select_by_visible_text('家電・スマホ・カメラ')
    category_child = driver.find_element_by_xpath(
        '/html/body/div[1]/main/div[2]/form/div[2]/div[2]/div[2]/div[8]/select/option[2]')
    category_child.click()
    category_chkbox = driver.find_element_by_xpath(
        '/html/body/div[1]/main/div[2]/form/div[2]/div[2]/div[3]/div[91]/div[1]/label')
    category_chkbox.click()
    hanbaityu = driver.find_element_by_xpath(
        '/html/body/div/main/div[2]/form/div[2]/div[8]/div/div[2]/label')
    hanbaityu.click()
    submit = driver.find_element_by_tag_name('button')
    submit.click()
    
    lowprice = Select(driver.find_element_by_xpath('/html/body/div/main/div[2]/form/div[1]/div/div/select'))
    lowprice.select_by_visible_text('価格の安い順')

def get_item(driver):

    global count
    search_limit = 50

    items = driver.find_elements_by_class_name('items-box')
    for item in items:

        count += 1
        if count > search_limit:
            break
        with open('index.html', 'a') as f:
            title =  item.find_element_by_tag_name('h3').text 
            link = item.find_element_by_tag_name('a').get_attribute('href')
            price = item.find_element_by_class_name('items-box-price').text
            img = item.find_element_by_tag_name('img').get_attribute('data-src')
            print('<div class="col">',file=f)
            print('<a href="' + link + '">LINK</a>',file=f)
            print('<h3>' + title + '</h3>',file=f)
            print('<img src="' + img + '"></img>',file=f)
            print(price,file=f)
            print('</div>',file=f)
            if dbres[count]["title"] == title:
                print("match")
            else:
                print(dbres[count]["title"])
                print(title)
                print("dont match")
            f.close()
            with open('main.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([title,price,link,img])
                f.close()
        users_ref.child(str(count)).set({
        'title': title,
        'price': price,
        'link': link,
        'img': img
        })

    if count > search_limit:
        return

    # 次のページがあれば処理を繰り返す
    next_page = driver.find_element_by_class_name('pager-next')
    if next_page.is_displayed() is True:
        next_page.find_element_by_tag_name('a').click()
        get_item(driver)


if __name__ == '__main__':
    main()
    print(CSVDIFF())