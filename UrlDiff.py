#!/usr/bin/python3
import sys
import urllib.request
import hashlib
from bs4 import BeautifulSoup
import re


class PageInfo:
    title = ""
    digest = ""
    result = 0
    url = ""


class UrlExplorer:

    # Links to explore
    links_to_explore = []

    # Links which has been visited
    links_visited = []

    start_url = ""
    other_url = ""
    n = 0

    def process_page(self, url):
        info = PageInfo()
        info.url = url

        try:
            with urllib.request.urlopen(url) as response:
                soup = BeautifulSoup(response, "html5lib")
                self.grab_links(soup)

                html = response.read()
                md5 = hashlib.md5()
                md5.update(html)

                info.digest = md5.digest()
                info.title = soup.title.string
                info.result = 200
        except urllib.request.HTTPError as e:
            info.result = e.getcode()

        self.links_visited.append(info)

        return info

    def is_foreign_link(self, link):
        if (link.find(self.start_url) == -1) and (link.find("http:") != -1):
            return True
        else:
            return False

    def add_link_to_explore(self, url):
        # skips mailto: and javascript: references
        if url.startswith("mailto:") or url.startswith("javascript:") or url.startswith("#"):
            return

        if url.find("http://") == -1 or url.find("https://") == -1:
            url = self.start_url + url

        self.links_to_explore.append(url)

    def grab_links(self, soup):
        for link in soup.find_all('a', attrs={'href':re.compile("[a-zA-Z0-9\-\/]*")}):
            url = link.attrs["href"]
            if (not any(url in s for s in self.links_to_explore)) and not self.is_foreign_link(url):
                self.add_link_to_explore(url)

    def explore(self):
        for url in self.links_to_explore:
            info = self.process_page(url)
            self.n = self.n + 1

            if self.n > 10:
                break

    def __init__(self, argv):
        if len(argv) < 2:
            print("Usage: UrlDiff <url-a> <url-b>")
            exit(1)

        self.links_to_explore.append(argv[1])
        self.start_url = argv[1]
        self.other_url = argv[2]

        self.explore()

        for info in self.links_visited:
            print(info.url + "\t\t\t\t" + str(info.result) + "\n")


# -------------------------------------- ENTRY POINT ------------------------------------------------------------------


if __name__ == "__main__":
    explorer = UrlExplorer(sys.argv)