import os
import json
from dotenv import load_dotenv
from IPython.display import Markdown, display, update_display
from openai import OpenAI
from helpers.extractor import Website

class OpenApi:
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
    
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
            return "Cannot use openApi"
        elif not api_key.startswith("sk-proj-"):
            print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
            return "Cannot use openApi"
        elif api_key.strip() != api_key:
            print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
            return "Cannot use openApi"
        self.openai = OpenAI()
    
    def get_links_user_prompt(self, website):
        user_prompt = f"Here is the list of links on the website of {website.url} - "
        user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
        Do not include Terms of Service, Privacy, email links.\n"
        user_prompt += "Links (some might be relative links):\n"
        user_prompt += "\n".join(website.links)
        return user_prompt
    
    def get_links(self, website):
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.link_extraction_system_prompt},
                {"role": "user", "content": self.get_links_user_prompt(website)}
        ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        return json.loads(result)
    
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
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.brochre_system_prompt_fun if isFun else self.brochre_system_prompt_serious},
                {"role": "user", "content": self.get_brochure_user_prompt(company_name, website)}
            ],
        )
        result = response.choices[0].message.content
        # display(Markdown(result))
        return result
        
    def stream_brochure(self, company_name, website, isFun):
        stream = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.brochre_system_prompt_fun if isFun else self.brochre_system_prompt_serious},
                {"role": "user", "content": self.get_brochure_user_prompt(company_name, website)}
            ],
            stream=True
        )
        
        response = ""
        display_handle = display(Markdown(""), display_id=True)
        for chunk in stream:
            response += chunk.choices[0].delta.content or ''
            response = response.replace("```","").replace("markdown", "")
            update_display(Markdown(response), display_id=display_handle.display_id)