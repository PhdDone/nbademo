from selenium import webdriver
import argparse
import logging
import time

month_map = ['0', 'OCT', 'NOV', 'DEC', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP']

def run(url, filename):
    driver = webdriver.Chrome()
    driver.get(url)
    #driver.get("http://stats.nba.com/schedule/#!?PD=N&Month=4")
    f = open("./data/"+filename, 'w')
    results = driver.find_elements_by_xpath('/html/body/main/div[2]/div/div[2]/div/div/section')

    for i in range(1, len(results)):
        result = results[i]
        games = result.find_elements_by_class_name("schedule-game")
        
        for game in games:
            article = game.find_element_by_tag_name('article')
            game_id = article.get_attribute('id')
            date = article.get_attribute('data-game-date')
            f.write(game_id + "\n")
            f.write(date + "\n")
            f.write(article.text + "\n")
            f.write("######\n")

    driver.quit()
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('m', metavar='Month', type=int, nargs='+',
                        help='Jan is 4, Oct is 1, Sep is 12')
    args = parser.parse_args()
    logging.basicConfig(filename='selenium.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info(args.m)
    baseurl = "http://stats.nba.com/schedule/#!?PD=N&Month="
    for month in args.m:
        file_name = month_map[month] + ".txt"
        url = baseurl + str(month)
        logging.info(url)
        run(url, file_name)
        time.sleep(1)
        logging.info("finish")
