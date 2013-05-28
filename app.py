import os

import tornado
import tornado.web
import tornado.ioloop

class Endpoint(tornado.web.RequestHandler):
    def get(self):
        self.write({ 'test': 1 })
        self.finish()

class App(tornado.web.RequestHandler):
    def get(self):
        self.write(file('index.html').read())
        self.finish()

if __name__ == '__main__':
	app = tornado.web.Application([
		(r'/', App),
		(r'/endpoint', Endpoint),
		(r'/((?:font|css|js|stylesheets)/.+)', tornado.web.StaticFileHandler, { 'path': os.getcwd() }),
	], debug=True)

	app.listen(8008)
	tornado.ioloop.IOLoop().instance().start()
