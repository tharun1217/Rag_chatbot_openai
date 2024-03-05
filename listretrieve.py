import os
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from bs4 import BeautifulSoup
import json

def remove_html_tags(text):
    if isinstance(text, str):
        # Initialize BeautifulSoup
        soup = BeautifulSoup(text, "html.parser")
        # Extract text without HTML tags
        return soup.get_text()
    else:
        return str(text)

def fetch_and_save_data(site_url, list_title, username, password, fields):
    try:
        # Connect to SharePoint
        ctx_auth = AuthenticationContext(url=site_url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(site_url, ctx_auth)
            # Get the list
            web = ctx.web
            list_obj = web.lists.get_by_title(list_title)

            # Set up variables for paging
            position = None
            page_size = 5000  # Adjust page size as needed
            total_items = 0

            # Create folder if it doesn't exist
            folder_path = "input"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Create and open the text file
            file_path = os.path.join(folder_path, f"{list_title}_data.txt")
            with open(file_path, "w", encoding="utf-8") as txt_file:
                while True:
                    # Get list items with selected fields using paging
                    query = list_obj.items.select(fields).filter(f"Id gt {position}" if position else "").top(page_size)
                    items = query.get().execute_query()

                    # Break if no more items
                    if not items:
                        break

                    # Write each item data to the text file
                    for item in items:
                        data = [remove_html_tags(item.get_property(field)) for field in fields]
                        txt_file.write("\t".join(data) + "\n")

                    # Update total items
                    total_items += len(items)

                    # Get the position for the next page
                    position = items[-1].properties['Id']

            print(f"Successfully retrieved and wrote data to {file_path}")

            return total_items
        else:
            print("Failed to acquire token. Check credentials.")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    try:
        # Load configuration from config.json
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
 
        site_url = config["site_url"]
        username = config["username"]
        password = config["password"]

        # Fetch and save data for QandA list
        total_qanda_items = fetch_and_save_data(site_url, "QandA", username, password, ["Description", "Answer"])
        print(f"Total items in QandA list: {total_qanda_items}")

        # Fetch and save data for InquiryList
        total_inquiry_items = fetch_and_save_data(site_url, "InquiryList", username, password, ["Category", "SubCategory", "InquiryTitle", "InquiryDescription", "ID"])
        print(f"Total items in InquiryList: {total_inquiry_items}")

        # Fetch and save data for InquiryDiscussionsList
        total_discussions_items = fetch_and_save_data(site_url, "InquiryDiscussionsList", username, password, ["ID", "Title", "Comment", "Role"])
        print(f"Total items in InquiryDiscussionsList: {total_discussions_items}")

        # Fetch and save data for InquiryCheckList
        total_checklist_items = fetch_and_save_data(site_url, "InquiryCheckList", username, password, ["LongName", "Description", "DocLink"])
        print(f"Total items in InquiryCheckList: {total_checklist_items}")

        # Fetch and save data for InquiryHistoryList
        total_history_items = fetch_and_save_data(site_url, "InquiryHistoryList", username, password, ["Description", "Action", "Role", "InquiryID"])
        print(f"Total items in InquiryHistoryList: {total_history_items}")

        # Fetch and save data for CPTSKnowledgeBaseArticles
        total_articles_items = fetch_and_save_data(site_url, "CPTSKnowledgeBaseArticles", username, password, ["Description"])
        print(f"Total items in CPTSKnowledgeBaseArticles: {total_articles_items}")

    except FileNotFoundError:
        print("config.json file not found.")
    except KeyError as ke:
        print(f"KeyError: {ke}. Check if all necessary keys are present in config.json.")
    except Exception as e:
        print(f"Error: {e}")
