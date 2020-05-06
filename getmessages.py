import requests
from bs4 import BeautifulSoup, NavigableString

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

def strip(s):
    return s.strip().lstrip()

def filter_contents(el):
    return list(filter(lambda _: _ != '\n', el.contents))

def convert_contents(el):
    pairs = [html_to_discord(i) for i in el.contents]
    txts, imgs = list(zip(*pairs))

    final_imgs = []
    for img in imgs:
        final_imgs.extend(img)

    return ''.join(txts), final_imgs

def html_to_discord(el):
    # Convert to markdown, eg images and p tags = paragraph
    
    if type(el) == str or type(el) == NavigableString:
        return strip(el), []

    if el.name == 'p':
        txt, imgs = convert_contents(el)
        return strip(txt) + '\n', imgs
    
    if el.name == 'b':
        txt, imgs = convert_contents(el)
        return '**' + strip(txt) + '**', imgs

    if el.name == 'img':
        return '<IMAGE>', [el['src']]

    return convert_contents(el)

def parse_msgs(msgs_container):
    notices = filter_contents(msgs_container)

    messages = []

    for notice in notices:
        author = strip(''.join(notice.find_all('small', class_='small-caps')[0].strong.contents))

        heading, _ = html_to_discord(notice.find_all('h4')[0])
        body, images = html_to_discord(notice.find_all('div', class_='notice-content')[0])

        messages.append([heading, body, images, author])
    
    return messages

def get_messages():
    session = requests.Session()

    with open('./.creds', 'r') as f:
        username = f.readline().strip()
        password = f.readline().strip()
    
    session.post("https://web3.girraween-h.schools.nsw.edu.au/portal2/user", json={
        "action": "login",
        "username": username,
        "password": password
    })

    resp_text = session.get("https://web3.girraween-h.schools.nsw.edu.au/portal/dashboard").text

    soup = BeautifulSoup(resp_text, 'html.parser')

    span_9s = soup.find_all('div', class_="span9")

    for possible_content in span_9s:
        children = filter_contents(possible_content)

        for i in range(len(children)):
            if children[i].contents[0] == 'Daily Notices':
                # This element is the header, the next one will contain the notices.
                return parse_msgs(children[i+1])

if __name__ == '__main__':
    print(get_messages())