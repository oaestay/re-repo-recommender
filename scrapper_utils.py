import psycopg2
import psycopg2.extras
import requests
import csv
import unicodedata
import os.path

import models
from config import config, config_accounts
import constants as const
from tqdm import *
import time


# ============================================================================
#                                Fetch
# ============================================================================

def load_repositories():
    print("Adding repositories and users...")
    with open(const.REPOSITORIES_CSV) as file:
        reader = csv.DictReader(file)
        rows = [(row["Username"], row["Repository Name"]) for row in reader]

    with tqdm(total=len(rows)) as pbar:
        for i, (owner, repository) in tqdm(enumerate(rows)):
            owner_exists = does_user_exist(owner)
            repository_exists = does_repository_exist(owner, repository)
            if not owner_exists or not repository_exists:
                r = get(
                    get_repository_url(owner, repository),
                )
                if r is not None:
                    if not owner_exists:
                        user = models.User(r.json()["owner"])
                        user.save_to_db()
                    if not repository_exists:
                        repository = models.Repository(r.json())
                        repository.save_to_db()
            pbar.update()


def add_stars(entry):
    repo, url = entry
    r = get(
        url,
        headers={
            "Accept": "application/vnd.github.v3.star+json",
        },
    )
    if r is not None:
        for stargazer in r.json():
            try:
                user = models.User(stargazer["user"])
                user.save_to_db()
                star = models.Star(stargazer["user"]["id"], repo["id"], stargazer["starred_at"])
                star.save_to_db()
            except Exception as error:
                print("==============================")
                print(url)
                print(error)
                print(stargazer)


def add_watchers(entry):
    repo, url = entry
    r = get(
        url,
    )
    if r is not None:
        for watcher in r.json():
            try:
                user = models.User(watcher)
                user.save_to_db()
                watch = models.Watch(watcher["id"], repo["id"])
                watch.save_to_db()
            except Exception as error:
                print("==============================")
                print(url)
                print(error)
                print(watcher)


def add_forks(entry):
    repo, url = entry
    r = get(
        url,
    )
    if r is not None:
        for forker in r.json():
            try:
                user = models.User(forker["owner"])
                user.save_to_db()
                fork = models.Fork(repo["id"], forker)
                fork.save_to_db()
            except Exception as error:
                print("==============================")
                print(url)
                print(error)
                print(forker)


# ============================================================================
# ============================================================================

def does_user_exist(name):
    conn = None
    result = None
    try:
        params = config()
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        query = """SELECT * FROM users WHERE name = %s;"""
        cur.execute(query, (name, ))
        result = cur.fetchone() is not None
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    finally:
        if conn is not None:
            conn.close()
    return result


def does_repository_exist(owner, repository):
    conn = None
    result = None

    try:
        params = config()
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        query = """SELECT * FROM repositories WHERE name = %s AND owner_name = %s;"""
        cur.execute(query, (repository, owner))
        result =  cur.fetchone() is not None
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    finally:
        if conn is not None:
            conn.close()
    return result


def get_repositories():
    conn = None
    repositories = None

    try:
        params = config()
        conn = psycopg2.connect(**params)

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = """SELECT * FROM repositories ORDER BY id"""
        cur.execute(query)
        repositories = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    finally:
        if conn is not None:
            conn.close()
    return repositories


def get_repository_url(owner, repo):
    return const.API_BASE_URL + "/repos/{}/{}".format(owner, repo)


def get_stargazers_url(owner, repo):
    return const.API_BASE_URL + "/repos/{}/{}/stargazers".format(owner, repo)


def get_watchers_url(owner, repo):
    return const.API_BASE_URL + "/repos/{}/{}/subscribers".format(owner, repo)


def get_forks_url(owner, repo):
    return const.API_BASE_URL + "/repos/{}/{}/forks".format(owner, repo)


def get(url, headers={}):
    accounts = config_accounts()
    for i in range(5):
        for account in accounts:
            r = requests.get(
                url,
                auth=account,
                headers=headers,
            )
            if r.status_code == 200:
                return r
            elif "message" in r.json():
                print(r.json()["message"])
        time.sleep(900)

    with open(const.FAILED_URLS, "a+") as file:
        file.write(url + "\n")
