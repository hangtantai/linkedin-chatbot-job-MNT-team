# import library if not import
from bs4 import BeautifulSoup
def extract_link(file_name: str, data: dict = None) -> dict:
    """
    Extracts link to detailed job

    Args:
        content (str): the HTML content as string
        data (dict): the dictionary to update link of job

    Returns:
        dict: the update dictionary with extracted information
    """
    # read content from file
    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()

    # check if dataFrame is None
    if data is None:
        data = {}

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Main container
    main_container = soup.find('div', class_="scaffold-layout__list")
    
    # Find all div tags within the main container
    div_tags = main_container.find_all('div')

    list_elements = {}
    a_tags = []

    # Iterate through each div tag to find ul tags and their li children
    for div in div_tags:
        ul_tag = div.find('ul')
        if ul_tag:
            li_tags = ul_tag.find_all('li')
            for li in li_tags:
                div = li.select_one("div > div > div.job-card-list__entity-lockup.artdeco-entity-lockup.artdeco-entity-lockup--size-4.ember-view > div > div > a")
                if div is not None:
                    a_tags.append(div)

    # extract link
    for a in a_tags:
        key = a.get("aria-label")
        value = a.get("href")
        if key and value:
            list_elements[key] = value

    # print infor of the process
    print("Successfully: extracted link")
    return list_elements