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
    message = ""


class UrlExplorer:

    # Links to explore
    links_to_explore = []

    # Links which has been visited
    links_visited = []

    start_url = ""
    other_url = ""
    n = 0

    def process_page(self, url, grablinks = True):
        """
        Processes the given url

        :param url:       string
        :param grablinks: boolean FALSE to disable link add to the pending links

        :return:    PageInfo instance
        """
        info = PageInfo()
        info.url = url
        print(url)

        try:
            with urllib.request.urlopen(url) as response:
                soup = BeautifulSoup(response, "html5lib")

                if grablinks:
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
        """
        Checks if the given link is foreign link

        :param link: string

        :return:     True if the given link doesn't belongs to the initial URL domain
        """
        if (link.find(self.start_url) == -1) and ((link.find("http:") != -1) or (link.find("https:") != -1)):
            return True
        else:
            return False

    def add_link_to_explore(self, url):
        """
        Adds the given URL into the urls to explore list.
        Skips mailto:, javascript: and # urls.

        :param url: url to add

        :return:    void
        """
        # skips mailto: and javascript: references
        if url.startswith("mailto:") or url.startswith("javascript:") or url.startswith("#"):
            return

        if url.find("http://") == -1 or url.find("https://") == -1:
            url = self.start_url + url

        self.links_to_explore.append(url)

    def grab_links(self, soup):
        """
        Gets the links on the soup

        :param soup: The soup the get links from

        :return: void
        """
        for link in soup.find_all('a', attrs={'href':re.compile("[a-zA-Z0-9\-\/]*")}):
            url = link.attrs["href"]
            if (not any(url in s for s in self.links_to_explore)) and not self.is_foreign_link(url):
                self.add_link_to_explore(url)

    def explore(self):
        """
        Starts the exploration of the given URLs

        :return: void
        """
        for url in self.links_to_explore:
            info = self.process_page(url)
            self.n = self.n + 1

            other_url = url.replace(self.start_url, self.other_url)
            other_info = self.process_page(other_url, False)

            if info.title != other_info.title:
                info.message = "Title doesn't match: found '" + other_info.title + "' instead of '" + info.title + "'"

            if self.n % 20 == 0:
                print("Urls processed: " + str(self.n))

            if self.n > 100:
                break

        print("Urls processed: " + str(self.n))

    def __init__(self, argv):
        """
        Constructor

        :param argv: Command line arguments
        """
        if len(argv) < 2:
            print("Usage: UrlDiff <url-a> <url-b>")
            exit(1)

        self.links_to_explore.append(argv[1])
        self.start_url = argv[1]
        self.other_url = argv[2]

        self.explore()

        for info in self.links_visited:
            print(info.url + "\t" + str(info.result))


# -------------------------------------- ENTRY POINT ------------------------------------------------------------------


if __name__ == "__main__":
    explorer = UrlExplorer(sys.argv)