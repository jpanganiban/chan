from bs4 import BeautifulSoup
import requests


class ChanParser(object):

    base_url = 'http://boards.4chan.org'
    board_url = base_url + "/%s"
    page_url = board_url + "/%s"

    def __init__(self, board):
        self._board = board
        self._url = self.board_url % board
        self._page_count = 11
        self._threads = None

    @property
    def url(self):
        return self._url

    @property
    def board(self):
        return self._board

    @property
    def threads(self):
        return self._threads

    def _get_threads_ids(self, data):
        soup = BeautifulSoup(data, 'lxml')
        threads = soup.find_all('div', 'thread')
        return [thread['id'].split('t')[1] for thread in threads]

    def _get_page_threads(self, page_num):
        url = self.page_url % (self._board, page_num) if page_num != 0 else \
                self.board_url % self._board

        resp = requests.get(url)
        return self._get_threads_ids(resp.text)

    def get_threads(self):
        threads = set()
        for page in range(self._page_count):
            _threads = self._get_page_threads(page)
            for thread in _threads:
                threads.add(thread)
        self._threads = [thread for thread in threads]
        return self._threads
