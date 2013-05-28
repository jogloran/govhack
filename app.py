import os
import abc

import tornado
import tornado.web
import tornado.ioloop

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
			'url': 'http://i2.kym-cdn.com/photos/images/original/000/236/809/956.png',
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

if __name__ == '__main__':
	app = tornado.web.Application([
		(r'/', App),
		(r'/endpoint', Endpoint),
		(r'/data', Data, { 'data_sources': [ MockImageDataSource() ] }),
		(r'/((?:font|css|js|stylesheets)/.+)', tornado.web.StaticFileHandler, { 'path': os.getcwd() }),
	], debug=True)

	app.listen(8008)
	tornado.ioloop.IOLoop().instance().start()
