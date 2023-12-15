import os
import requests
import html
import re
import xml.etree.ElementTree as ET

# Hardcoded RSS Feed URL
RSS_FEED_URL = "https://rss.app/feeds/ZtrEb8ER0SDfjyIm.xml"

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "fetch_news_summary",
        "description":
        "Fetch and summarize the latest three articles from a news feed.",
        "parameters": {
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "string",
                    "description": "A string containing 'yes'"
                },
            },
            "required": ["confirm"]
        }
    }
}


# Function to strip HTML and URLs from simple context
def strip_html(content):
  # Decode HTML entities
  content = html.unescape(content)

  # Remove HTML tags
  text_only = re.sub('<[^<]+?>', '', content)

  # Remove URLs
  no_urls = re.sub(r'http\S+', '', text_only)

  return no_urls.strip()


# The callback function (Fetches news summaries)
def fetch_news_summary(arguments):
  """
  Fetch and summarize the latest three articles from the specified RSS feed.

  :param rss_feed_url: URL of the RSS feed.
  :return: list of dicts, Each dict contains title, short description, and link of an article.
  """
  try:
    response = requests.get(RSS_FEED_URL)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    articles = [{
        "title":
        item.find('title').text if item.find('title') is not None else "",
        "description":
        ' '.join((strip_html(item.find('description').text)
                  or "").split()[:50]),
        "link":
        item.find('link').text if item.find('link') is not None else ""
    } for item in root.findall('.//item')[:3]]

    return articles

  except requests.RequestException as e:
    return f"Failed to fetch news feed: {str(e)}"
  except ET.ParseError:
    return "Failed to parse the RSS feed."
