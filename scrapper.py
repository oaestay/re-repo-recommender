import re
import math
from tqdm import *


import constants as const
import scrapper_utils as utils
from config import config
from multiprocessing import Pool
pattern = re.compile(r'\s+')


def main():
    # Read csv, then save owners and repos
    # utils.load_repositories()

    repositories = utils.get_repositories()

    # stars_urls = [
    #     (repo, utils.get_stargazers_url(repo["owner_name"], repo["name"]) + "?per_page=100&page={}".format(current_page))
    #     for repo in repositories
    #     for current_page in range(1, min(399, int(math.ceil(repo["stargazers_count"] / 100))) + 1)
    # ]

    watches_urls = [
        (repo, utils.get_watchers_url(repo["owner_name"], repo["name"]) + "?per_page=100&page={}".format(current_page))
        for repo in repositories
        for current_page in range(1, min(399, int(math.ceil(repo["subscribers_count"] / 100))) + 1)
    ]

    forks_urls = [
        (repo, utils.get_forks_url(repo["owner_name"], repo["name"]) + "?per_page=100&page={}".format(current_page))
        for repo in repositories
        for current_page in range(1, int(math.ceil(repo["forks_count"] / 100)) + 1)
    ]

    failed_urls = []

    # print("Adding Stars...")
    # with open(const.FAILED_URLS, "a+") as file:
    #     file.write("Stars failed to fetch:\n")
    # with Pool(4) as p:
    #     with tqdm(total=len(stars_urls)) as pbar:
    #         for i, _ in tqdm(enumerate(p.imap_unordered(utils.add_stars, stars_urls))):
    #             pbar.update()

    print("Adding Watches...")
    with open(const.FAILED_URLS, "a+") as file:
        file.write("Watches failed to fetch:\n")
    with Pool(4) as p:
        with tqdm(total=len(watches_urls)) as pbar:
            for i, _ in tqdm(enumerate(p.imap_unordered(utils.add_watchers, watches_urls))):
                pbar.update()

    print("Adding Forks...")
    with open(const.FAILED_URLS, "a+") as file:
        file.write("Forks failed to fetch:\n")
    with Pool(4) as p:
         with tqdm(total=len(forks_urls)) as pbar:
            for i, _ in tqdm(enumerate(p.imap_unordered(utils.add_forks, forks_urls))):
                pbar.update()


if __name__ == '__main__':
    main()

