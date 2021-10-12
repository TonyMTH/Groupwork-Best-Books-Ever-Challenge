#Imports
from selenium import webdriver
import pandas as pd
import re
import time

from helpers import *


#open chrome
my_driver = "chromedriver.exe"
op = webdriver.ChromeOptions()
op.add_argument('headless')

csv_name = 'best-books.csv'

# main_url = 'https://www.goodreads.com/list/show/1.Best_Books_Ever'
page_url_csv = 'page_url.txt'

#collect in dictionary
content_dict = {'url':[],'title':[],'author':[],'num_reviews':[],'num_ratings':[],'avg_rating':[],'num_pages':[],\
    'original_publish_year':[],'series':[],'genres':[],'awards':[],'places':[]}

#if csv doesn't exist, create new one
try:
    df = pd.read_csv(csv_name)
    next_row = df.shape[0]
    with open(page_url_csv,'r') as file:
        main_url = file.readlines()[0]
except:
    next_row = 0
    with open(csv_name,'w') as file:
        file.write(','.join(content_dict.keys()))
        file.write('\n')
        
#print(main_url)
k=0
page_number=next_row//100
save_freq = 3
no_items_needed = 5000
wait_time = 1


#move through the pages
while True:
    print("="*20+"page("+str(page_number)+")"+"="*20)
    main_driver = webdriver.Chrome(my_driver,options=op)
    main_driver.implicitly_wait(wait_time)
    main_driver.get(main_url)

    books = main_driver.find_elements_by_xpath('.//a[@class="bookTitle"]')
    author = main_driver.find_elements_by_xpath('.//a[@class="authorName"]')
    ratings = main_driver.find_elements_by_xpath('.//span[@class="minirating"]')

    den_divisor = len(books)
    it = next_row%den_divisor
    

    while it+1 != len(books):
        
        #back to base url
        main_driver = webdriver.Chrome(my_driver,options=op)
        main_driver.implicitly_wait(wait_time)
        main_driver.get(main_url)
        time.sleep(wait_time)

        content_dict['title'].append(books[it].text)
        #print(books[it].text)
        content_dict['url'].append(books[it].get_attribute("href"))
        content_dict['series'].append(check_Series(books[it].text))
        content_dict['author'].append(author[it].text)

        avg_rating, num_ratings = getRatings(ratings[it].text)
        content_dict['avg_rating'].append(avg_rating)
        content_dict['num_ratings'].append(num_ratings)

        #Follow the link of book i (redirection to book i page)
        #update movie_i_driver url
        book_i_driver_url = books[it].get_attribute("href")
        main_driver = webdriver.Chrome(my_driver,options=op)
        main_driver.implicitly_wait(wait_time)
        main_driver.get(book_i_driver_url)

        rightContainer = main_driver.find_element_by_xpath("//div[@class='rightContainer']")
        genres = rightContainer.find_elements_by_xpath('.//div[@class="elementList "]')
        genres = [g.find_element_by_xpath('.//div[@class="left"]').text for g in genres]

        bookMeta = main_driver.find_element_by_xpath('.//div[@id="bookMeta"]')
        hyperlink = bookMeta.find_elements_by_xpath('.//a[@class="gr-hyperlink"]')
        numberOfPages = main_driver.find_element_by_xpath('.//span[@itemprop="numberOfPages"]')

        details = main_driver.find_element_by_xpath('.//div[@id="details"]')
        original_publish_year = details.find_elements_by_xpath('.//div[@class="row"]')[1]
        main_driver.find_element_by_xpath('.//a[@id="bookDataBoxShow"]').click()

        bookDataBox = main_driver.find_element_by_xpath('.//div[@id="bookDataBox"]')

        try:
            setting_div = bookDataBox.find_element_by_xpath("//div[text()='Setting']")
            settings = setting_div.find_element_by_xpath("./following-sibling::div")
            places = settings.find_elements_by_tag_name("a")
            places = [ p.text for p in places if p.text != '…more' and p.text.strip() != '']
        except:
            places = None

        try:
            literary_awards_div = bookDataBox.find_element_by_xpath("//div[text()='Literary Awards']")
            literary_awards = literary_awards_div.find_element_by_xpath("./following-sibling::div")
            awards = literary_awards.find_elements_by_tag_name("a")
            awards = [ a.text for a in awards if a.text != '...more' and a.text.strip() != '']
        except:
            awards = None

        # #genres_div = main_driver.find_element_by_xpath("//div[text()='Genres']")
        # right_container = main_driver.find_element_by_xpath('.//div[@class="rightContainer"]')
        # bigBoxBody = right_container.find_element_by_xpath('//div[@class="bigBoxContent containerWithHeaderContent"]')
        # #class="h2Container gradientHeaderContainer"
        # print('the')
        # #print(genres_div.text)
        # #genres = genres_div.find_element_by_xpath("./following-sibling::div")
        # genres = bigBoxBody.find_elements_by_xpath('.//a[@class="actionLinkLite bookPageGenreLink"]')
        # print(genres)
        # #genres = [g.find_elements_by_xpath('.//div[@class="left"]').text for g in genres]

        content_dict['num_reviews'].append( get_no_review_pages(hyperlink[-1].text) )
        content_dict['num_pages'].append( get_no_review_pages(numberOfPages.text) )
        content_dict['original_publish_year'].append( get_original_publish_year(original_publish_year.text) )
        content_dict['places'].append(places)
        content_dict['awards'].append(awards)
        content_dict['genres'].append(genres)

        #save data to csv after save_freq iterations
        if k%save_freq == 0 and k != 0:
            
            df = pd.DataFrame(content_dict)
            df.to_csv(csv_name, mode='a', header=False, index=False)
            print("writen now: "+str(save_freq)+", tottal written:"+str(next_row))
            content_dict = {'url':[],'title':[],'author':[],'num_reviews':[],'num_ratings':[],'avg_rating':[],'num_pages':[],\
                'original_publish_year':[],'series':[],'genres':[],'awards':[],'places':[]}
        k += 1
        next_row += 1
        it = next_row%den_divisor
    next_row += 1

    #save data to csv after
    df = pd.DataFrame(content_dict)
    df.to_csv(csv_name, mode='a', header=False, index=False)
    print("writen now: "+str(k%save_freq)+", tottal written:"+str(next_row))
    content_dict = {'url':[],'title':[],'author':[],'num_reviews':[],'num_ratings':[],'avg_rating':[],'num_pages':[],\
        'original_publish_year':[],'series':[],'genres':[],'awards':[],'places':[]}  
        
    #move to next page
    try:
        if k != 0:
            #back to base url
            main_driver = webdriver.Chrome(my_driver,options=op)
            main_driver.implicitly_wait(wait_time)
            main_driver.get(main_url)
            
            
            #next_page = main_driver.find_element_by_xpath('//body[@id="styleguide-v2"]')
            
            next_page = main_driver.find_element_by_xpath('//a[@class="next_page"]')

            #update main_url for next movie page
            main_url = next_page.get_attribute("href")
            
            
            with open(page_url_csv,'w') as file:
                file.write(main_url)
                file.write('\n')

        #Stop after no_items_needed
        if k >= no_items_needed:
            break
        
        
    except:
        #stop loop when there is no next page
        break

    page_number += 1

    
#write remaining items to csv
if k%save_freq != 0:
    df = pd.DataFrame(content_dict)
    df.to_csv(csv_name, mode='a', header=False, index=False)
    print("writen now: "+str(k%save_freq)+", tottal written:"+str(next_row))



print("Done")
