from bs4 import BeautifulSoup
import requests
import re 
import os 
from dataclasses import dataclass
import sys

from src.logger import logging
from src.exception import CustomException


@dataclass
class DataIngestionConfig:
    scraping_url: str = "https://onepiece.fandom.com/wiki/Special:AllPages"
    base_url: str = "https://onepiece.fandom.com"
    raw_data_path: str = os.path.join('artifacts', 'raw_data')
    clean_data_path: str = os.path.join('artifacts', 'clean_data')    
    nav_tag: str = "mw-allpages-nav"
    body_tag: str = "mw-allpages-body"
    output_tag: str = "mw-allpages-output"


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
        
    def initiate_data_ingestion(self):
        '''
        Do the data ingestion by scraping the data from OnePiece Wiki Website (https://onepiece.fandom.com) 
        and cleaning it.
        Params:
            None
        Returns:
            Path to scraped data: str
            Path to clean data: str
        '''
        logging.info("Initialized Data Ingestion")
        try:
            self.initiate_data_scraping()
            self.initiate_data_cleaning()
            
            logging.info("Data Ingestion Completed")
            
            return (
                self.ingestion_config.raw_data_path,
                self.ingestion_config.clean_data_path
            )
        except Exception as e:
            raise CustomException(e, sys)
        
        
        
    def initiate_data_scraping(self):
        '''
        Scrapes the data from the OnePiece Wiki Website (https://onepiece.fandom.com) and store it in the artifacts folder.
        Params:
            None
        Returns:
            Path to scraped data: str
            Path to clean data: str
        '''
        logging.info('Entered the Data Scraping method or component.')
        try:
            response = requests.get(self.ingestion_config.scraping_url)
            if response.status_code != 200:
                logging.info("Could not connect to the SCRAPING URL: {}".format(self.ingestion_config.scraping_url))
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                count = 0
                while True:
                    navs = soup.find('div', class_=self.ingestion_config.nav_tag).find_all('a')[-1]
                    if 'Previous page' in navs.text:
                        break 
                    
                    response = requests.get(self.ingestion_config.base_url + navs['href'])
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for tag in soup.find('div', class_=self.ingestion_config.body_tag).find_all('a'):
                        title = re.sub(r"[^A-Za-z0-9]", "", tag['title'])
                        link = tag['href']
                        
                        with open(os.path.join(self.ingestion_config.raw_data_path, f'{title}.txt'), 'w') as file:
                            soup = BeautifulSoup(requests.get(self.ingestion_config.base_url + link).text, 'html.parser')
                            for el in soup.find('div', class_=self.ingestion_config.output_tag).children:
                                if el.name == 'p' or el.name == 'ul':
                                    file.write(el.get_text())
                    count += 1
                    
                    if count%500 == 0:
                        logging.info("Scraped {} Data Articles".format(count))
                
                logging.info(f'Total {count} data articles are scraped')
                logging.info('Scraping of data is completed')
                
                return (
                    self.ingestion_config.raw_data_path,
                    self.ingestion_config.clean_data_path
                )
                    
        except Exception as e:
            raise CustomException(e, sys)
                                
    def initiate_data_cleaning(self):
        '''
        Clean the scraped data in the raw data folder in the artifacts location
        Params:
            None
        Returns:
            Path to scraped data: str
            Path to cleaned data: str
        '''
        logging.info('Entered the data cleaning method or component.')
        
        try:
            count = 0
            for filename in os.listdir(self.ingestion_config.raw_data_path):
                filepath = os.path.join(self.ingestion_config.raw_data_path, filename)
                with open(filepath, 'r') as raw_file:
                    raw_data = raw_file.readlines()
                    
                data = [re.sub(r"\s+", " ", i) for i in raw_data if i != '\n']
                
                with open(os.path.join(self.ingestion_config.clean_data_path, filename), 'w') as clean_file:
                    clean_file.writelines(data)
                    
                count += 1
                if count%500 == 0:
                    logging.info("Cleaned {} Data Articles".format(count))
            
            logging.info(f"Total {count} data articles are cleaned")
            logging.info("Data Cleaning is completed")
            
            return (
                self.ingestion_config.raw_data_path,
                self.ingestion_config.clean_data_path
            )
                    
        except Exception as e:
            raise CustomException(e, sys)
        