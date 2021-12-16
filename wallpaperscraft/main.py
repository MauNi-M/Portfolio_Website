from random import choice, randint
import requests
from bs4 import BeautifulSoup

wallpaperscraft_url = "https://wallpaperscraft.com"


def get_categories():
    r = requests.get(wallpaperscraft_url)
    soup = BeautifulSoup(r.text, "html5lib")
    categories = [tag.attrs["href"] for tag in soup.select('a[href^="/catalog/"]')]
    return categories


def get_categories_list():
    categories_list = [cat_link.split("/")[-1] for cat_link in get_categories()]
    return categories_list


def get_images_pages(category_url):
    end = 50
    random_page = randint(1, end)
    cat_url = wallpaperscraft_url + category_url + f"/page{random_page}"
    r = requests.get(cat_url)
    while r.status_code != 200:
        if end < 1:
            raise ValueError("End got less than one, check page number")
        end = end // 2
        random_page = randint(1,end)
        cat_url = wallpaperscraft_url + category_url + f"/page{random_page}"
        r = requests.get(cat_url)
    soup = BeautifulSoup(r.text, "html5lib")
    image_pages = [tag.attrs["href"] for tag in soup.select('a[href^="/wallpaper/"]')]
    return image_pages


def get_resolutions(image_page):
    res_url = wallpaperscraft_url + image_page
    r = requests.get(res_url)
    soup = BeautifulSoup(r.text, "html5lib")
    resolutions = [tag.attrs['href'] for tag in soup.select('a[href^="/download/"]')]
    return resolutions


def resolutions_list():
    r = requests.get(wallpaperscraft_url)
    soup = BeautifulSoup(r.text, "html5lib")
    resolutions = [tag.attrs["href"].split("/")[-1] for tag in soup.select('a[href^="/all"]') if tag.attrs["href"].split("/")[-1].split("x")[0].isnumeric()]
    return resolutions

def common_resolutions():
    with open("aspect_ratio.txt", "r", encoding="utf8") as r:
        return r.read()


# TODO: complete ratio dictionary
# def ratio_dict():
#     ratio = {}
#     for res in resolutions_list():
#

def get_image(img_res_page):
    img_url = wallpaperscraft_url + img_res_page
    r = requests.get(img_url)
    soup = BeautifulSoup(r.text, "html5lib")
    image = soup.select_one('a[href^="https://images.wallpaperscraft.com"]')
    return image.attrs["href"]


def get_random_image_url():
    rand_cat = choice(get_categories())
    print(f"Random category: {rand_cat}")
    print(f"Next Url: {wallpaperscraft_url}{rand_cat}")
    img_page = choice(get_images_pages(rand_cat))
    print(f"Random page: {img_page}")
    print(f"Next url: {wallpaperscraft_url}{img_page}")
    img_res = choice(get_resolutions(img_page))
    print(f"Random res: {img_res}")
    image = get_image(img_res)
    return image


def web_image(category: str, resolution: str) -> str:
    """

    :param category: try anything otherwise use categories_list for all categories available
    :param resolution: use any resolution you want(widthxheight),if it doesnt exist use get_resolution_list for all resolutions available
    :return: url of the image
    """
    cat_link = [cat for cat in get_categories() if category.lower() in cat][0]
    if cat_link:
        resolution = [res for res in get_resolutions(choice(get_images_pages(cat_link))) if resolution in res][0]
        if resolution:
            return get_image(resolution)
        else:
            raise ValueError(f"Try another resolution")
    else:
        raise ValueError(f"Try another category, |{category}| invalid.")


if __name__ == '__main__':
    pass
