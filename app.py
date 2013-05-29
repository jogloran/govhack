import os
import abc

import tornado
import tornado.web
import tornado.ioloop
import tornado.options

class Endpoint(tornado.web.RequestHandler):
    def get(self):
        self.write({ 'test': 1 })
        self.finish()

class DataSource(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def make_json(self):
		pass

class MockImageDataSource(DataSource):
	def make_json(self):
		return [{
			'type': 'image',
			'title': 'A mock image',
			'subtitle': 'Subtitle',
			'url': 'http://farm8.staticflickr.com/7284/8736071763_e4a5f89764_o.jpg',
			'timestamp': '2013-05-28T13:29Z',
		},
		{
			'type': 'image',
			'title': 'A mock image',
			'subtitle': 'Subtitle',
			'url': 'http://farm6.staticflickr.com/5341/8778803810_a743321a0f_o.jpg',
			'timestamp': '2013-05-28T13:29Z',
		}]

class MockMediaDataSource(DataSource):
	def make_json(self):
		return [{
			'type': 'media',
			'title': 'An audio item',
			'subtitle': 'Listen to it',
			'timestamp': '2013-05-28T13:29Z',
			'url': 'test.mp3'
		}]

class MockTextDataSource(DataSource):
	def make_json(self):
		return [{
			'type': 'text',
			'title': 'A mock item',
			'subtitle': 'Subtitle',
			'html': '<strong>test</strong>',
			'timestamp': '2013-05-28T13:29Z',
		},
		{
			'type': 'text',
			'title': 'Another mock text item',
			'subtitle': 'Subtitle',
			'html': '<u>another</u>',
			'timestamp': '2013-05-28T13:29Z',
		}]

class MockGraphDataSource(DataSource):
	def make_json(self):
		return [{
			'type': 'graph',
			'title': 'A mock graph',
			'subtitle': 'Subtitle',
			'datapoints': [[1983, 3], [1984, 4], [1985, 3], [1986, 2]],
			'timestamp': '2013-05-28T13:29Z',
		}]

class Data(tornado.web.RequestHandler):
	def initialize(self, data_sources):
		self.data_sources = data_sources

	def get(self):
		response = { 'items': [] }
		for ds in self.data_sources:
			response['items'].extend( ds.make_json() )

		self.write(response)
		self.finish()

class App(tornado.web.RequestHandler):
    def get(self):
        self.write(file('index.html').read())
        self.finish()

class StaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

if __name__ == '__main__':
	tornado.options.parse_command_line()
	app = tornado.web.Application([
		(r'/', App),
		(r'/endpoint', Endpoint),
		(r'/data', Data, { 'data_sources': [ MockImageDataSource(), MockTextDataSource(), MockGraphDataSource(), MockMediaDataSource() ] }),
		(r'/((?:fonts|css|js|stylesheets)/.+)', tornado.web.StaticFileHandler, { 'path': os.getcwd() }),
		(r'/(_.+)', StaticFileHandler, dict(path=os.getcwd())),
		(r'/(.+\.mp3)', StaticFileHandler, dict(path=os.getcwd())),		
	], debug=True)

	app.listen(8008)
	tornado.ioloop.IOLoop().instance().start()
