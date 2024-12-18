import requests
from helpers.extractor import Website
import json

class Ollama:
    OLLAMA_API = "http://localhost:11434/api/chat"
    HEADERS = {"Content-Type": "application/json"}
    MODEL = "llama3.2"
    
    link_extraction_system_prompt = "You are provided with a list of links found on a webpage. \
    You are able to decide which of the links would be most relevant to include in a brochure about the company, \
    such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    link_extraction_system_prompt += "You should respond in JSON as in this example:"
    link_extraction_system_prompt += """
    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page": "url": "https://another.full.url/careers"}
        ]
    }
    """
    
    brochre_system_prompt_serious ="You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information."
    
    brochre_system_prompt_fun ="You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information."
    
    def get_links_user_prompt(self, website):
        user_prompt = f"Here is the list of links on the website of {website.url} - "
        user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
        Do not include Terms of Service, Privacy, email links.\n"
        user_prompt += "Links (some might be relative links):\n"
        user_prompt += "\n".join(website.links)
        return user_prompt
    
    def get_links(self, website):
          
        response = requests.post(
            self.OLLAMA_API, 
            json = {
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": self.link_extraction_system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.get_links_user_prompt(website)
                    }
                ],
                "stream": False,
                "format" : {
                    "type": "object"
                }
            },
            headers=self.HEADERS
        )
        return json.loads(response.json()['message']['content'])
        
    
    def get_all_details(self, website):
        result = "Landing page:\n"
        result += website.get_contents()
        links = self.get_links(website)
        for link in links["links"]:
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
        return result
    
    def get_brochure_user_prompt(self, company_name, website):
        user_prompt = f"You are looking at a company called: {company_name}\n"
        user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
        user_prompt += self.get_all_details(website)
        user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
        return user_prompt
    
    def create_brochure(self, company_name, website, isFun):
        system_prompt = self.brochre_system_prompt_fun if isFun else self.brochre_system_prompt_serious
        user_prompt = self.get_brochure_user_prompt(company_name, website)
        response = requests.post(
            self.OLLAMA_API, 
            json = {
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "stream": False
            },
            headers=self.HEADERS
        )
        result = response.json()['message']['content']
        # display(Markdown(result))
        return result