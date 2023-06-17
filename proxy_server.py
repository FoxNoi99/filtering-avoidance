# ©filtering-avoidance FoxNoi99 クリエイティブ・コモンズ・ライセンス（表示 - 非営利 - 継承 4.0 国際）https://creativecommons.org/licenses/by-nc-sa/4.0/

from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

def rewrite_resource_urls(soup, tag_name, attr_name, base_url, target_url):
    for tag in soup.find_all(tag_name):
        original_url = tag.get(attr_name)
        if original_url:
            absolute_url = urljoin(target_url, original_url)
            new_url = f"{base_url}?url={absolute_url}"
            tag[attr_name] = new_url

def rewrite_links(content, base_url, target_url):
    soup = BeautifulSoup(content, 'html.parser')
    rewrite_resource_urls(soup, 'a', 'href', base_url, target_url)
    rewrite_resource_urls(soup, 'img', 'src', base_url, target_url)
    rewrite_resource_urls(soup, 'link', 'href', base_url, target_url)
    rewrite_resource_urls(soup, 'script', 'src', base_url, target_url)
    return str(soup)

@app.route('/')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Error: 'url' parameter is required."

    try:
        response = requests.get(target_url)
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to fetch the content from the URL: {e}"

    content_type = response.headers['Content-Type']
    if 'text/html' in content_type:
        content = rewrite_links(response.content, request.base_url, target_url)
    else:
        content = response.content

    return Response(content, content_type=content_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)