from bs4 import Tag, BeautifulSoup
import requests


class ChanObject(object):

    base_url = 'http://boards.4chan.org'
    board_url = base_url + "/%s"
    page_url = board_url + "/%s"
    thread_url = board_url + "/res/%s"

    def __init__(self, html_or_soup=None):
        if html_or_soup:
            self._soup = html_or_soup if isinstance(html_or_soup, Tag) else \
                    BeautifulSoup(html_or_soup)


class Post(ChanObject):

    def __init__(self, thread, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self._thread = thread

    @property
    def thread(self):
        return self._thread

    @property
    def id(self):
        return self._soup['id'].split('pc')[1]

    @property
    def __info(self):
        return self._soup.find('div', 'postInfo')

    @property
    def subject(self):
        return self.__info.find('span', 'subject').text

    @property
    def timestamp(self):
        return self.__info.find('span', 'dateTime')['data-utc']

    @property
    def __file(self):
        return self._soup.find('div', 'file')

    @property
    def has_attachment(self):
        return bool(self.__file)

    @property
    def attachment(self):
        if self.has_attachment:
            return "http:%s" % self.__file.find('a', 'fileThumb')['href']
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'timestamp': self.timestamp,
            'has_attachment': self.has_attachment,
            'attachment': self.attachment,
        }


class Thread(ChanObject):

    def __init__(self, board, id, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self._board = board
        self._id = id
        if not self._soup:
            self.fetch()
        else:
            self._replies = self.__get_replies()
            self._original_post = self.__get_op()

    @property
    def board(self):
        return self._board

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return self.thread_url % (self.board.name, self.id)

    @property
    def replies(self):
        return self._replies

    @property
    def original_post(self):
        return self._original_post

    def __get_replies(self):
        reply_soups = self._soup.find_all('div', 'replyContainer')
        return [Post(self, reply_soup) for reply_soup in reply_soups]

    def __get_op(self):
        op_soup = self._soup.find('div', 'opContainer')
        return Post(self, op_soup)

    def fetch(self):
        response = requests.get(self.url)
        self._soup = BeautifulSoup(response.text)
        self._replies = self.__get_replies()
        self._original_post = self.__get_op()
        return self

    def to_dict(self):
        return {
            'id': self.id,
            'board': self.board.name,
            'url': self.url,
            'name': self.original_post.subject,
            'timestamp': self.original_post.timestamp,
            'replies': [reply.to_dict() for reply in self.replies],
        }


class Board(ChanObject):

    page_count = 11
    _threads = None

    def __init__(self, name, *args, **kwargs):
        super(Board, self).__init__(*args, **kwargs)
        self._name = name
        self.fetch()

    @property
    def name(self):
        return self._name

    @property
    def threads(self):
        return self._threads

    @property
    def url(self):
        return self.board_url % self._name

    def __get_thread_id(self, soup):
        return soup['id'].split('t')[1]

    def __create_thread_dict(self, thread_soups):
        # Create dict
        threads = {}
        for thread_soup in thread_soups:
            thread_id = self.__get_thread_id(thread_soup)
            thread = Thread(self, thread_id, thread_soup)
            threads.update({thread_id: thread})
        return threads

    def __get_page_threads(self, page_num):
        url = self.page_url % (self._name, page_num) if page_num != 0 else \
                self.board_url % (self._name)
        response = requests.get(url)
        self._soup = BeautifulSoup(response.text)
        thread_soups = self._soup.find_all('div', 'thread')
        return self.__create_thread_dict(thread_soups)

    def __get_threads(self):
        threads = {}
        for page_num in xrange(self.page_count):
            t = self.__get_page_threads(page_num)
            threads.update(t)
        return threads

    def fetch(self):
        self._threads = self.__get_threads()
        return self

    def to_dict(self):
        return {
            'name': self.name,
            'threads': [thread.to_dict() for id, thread in self.threads.iteritems()],
        }
