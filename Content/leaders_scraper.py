import requests
from bs4 import BeautifulSoup
import re
class Scrapper:
 # A class was created in order to be imported in the main.py latter on   
        
    def get_first_paragraphs(self, wikipedia_url):   
        '''The goal of this function was to get the information of the first paragraph of a link
        provided by the user as a parameter and return it, after sanitised with regular expression,
        a clean and formated paragraph.'''   
        wiki = requests.get(wikipedia_url)
        soup = BeautifulSoup(wiki.text, "html.parser")
        # Getting the request to access the link.
        first_paragraph = ""
        for p in soup.find_all("p"):
            if p.find_parent(class_="bandeau-cell"):
                continue
            if p.find_parent(class_="plainlist"):
                continue   
            p = p.text.strip()
            if p != "":
                first_paragraph = p
                break
        # In this section, if statements were used to filter the information and get the correct paragraph.
        cleaned_paragraph = re.sub(r"(?:(?<=\/)[^\/]+\/)|(?:\[.*?\])|(?:\xa0)|(?:[\w\s-]+;)|(?:(?<=\[)[^]]+(?=]))|(?:«[^»]+»)|(?:\d+(?=\]))|(?:[^;\n]+;)|(?:CD&V\/N-VA)", "", p)
        #Sanitization with regex.
        return cleaned_paragraph

    def get_leaders(self):
        '''With this function, the dictionary with all the information of the leaders per country is created.
        Calling the function get_first_paragraphs() using the url of each leader,
        the first paragraph is added to the dictionary with the key value 'Summary'.
        It returns the dictionary when called.'''
        # Defining the urls
        countries_url = "https://country-leaders.onrender.com/countries"
        cookie_url = "https://country-leaders.onrender.com/cookie"
        leaders_url = "https://country-leaders.onrender.com/leaders"

        with requests.Session() as session:
            # Getting the cookies
            r = session.get(cookie_url)
            cookies = r.cookies.get_dict()
            leaders_per_country = {}
            # Getting the countries
            countries_req = session.get(countries_url, cookies=cookies)
            countries = countries_req.json()
            # Looping over the countries and saving the leaders in a dictionary
            leaders_per_country = {}    
            for country in countries:
                leaders_per_country[country] = session.get(leaders_url, cookies=cookies, params={"country": country}).json()
            # Looping again over the countries to modify the information adding the first paragraph as 'summary' for each leader
            for country in countries:
                for i in range(len(leaders_per_country[country])):
                    leaders_per_country[country][i]['Summary'] = self.get_first_paragraphs(leaders_per_country[country][i]["wikipedia_url"])
        return leaders_per_country

    def save(self, leaders_country):
        '''This function saves the information acquired from the previous functions and store them in a json file in the disk.'''
        import json
        content_leaders_dict = leaders_country
        new_filename = "./leaders.json"
        with open(new_filename, "w+", encoding='utf8') as file_leader:
            json.dump(content_leaders_dict, file_leader, indent=4, ensure_ascii=False)
    
    def main(self):
        '''This function calls the function save() using the function get_leaders() as parameter
        in order to be imported in the main.py'''
        self.save(self.get_leaders())