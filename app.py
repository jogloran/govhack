import os
import abc

from collections import defaultdict

import tornado
import tornado.web
import tornado.ioloop
import tornado.options

import json
import urllib2
import sqlite3

topic='captain+cook'

import flickrapi
import re

api_key = '7f7d7d3fbe64bb46e98a4d97a72fd563'
nswuser = '29454428@N08'

def getDataSourceById(id):
    lat = -33.86712312199998
    lon = 151.20428619999998
    lat, lon = map(str, (lat, lon))
    suburb = getSuburbFrom(lat, lon) 

    data_sources = {
        'family': {
                'name':'Present and past family life',
                'pos' :[1,1],
                'data':[MockImageDataSource(), NAAImageSource('Sydney', 'sydney1885.sqlite', 1900), NAAImageSource('Collection','sydney1955.sqlite',1900),ABSDataSource(1900,2000)]
            },
        'past':
            {
                'name':'Past in the Present',
                'pos':[1,2],
                'data':[MockImageDataSource(), NAAImageSource(suburb, 'sydney1885.sqlite', 1900), NAAImageSource(suburb,'sydney1955.sqlite', 1900),ABSDataSource(1900,2000)]
            },
        'community':
            {
                'name':'Community and Remembrance',
                'pos':[2,1],
                'data':[MockImageDataSource(), NAAImageSource('Christmas OR Easter OR Hanukkah', 'sydney1885.sqlite',1900), NAAImageSource('Christmas OR Easter OR Hanukkah OR "Australia Day" OR ANZAC OR "bastille day" OR "chinese new year" OR diwali OR Ramadan OR "moon festival"','sydney1955.sqlite', 1900),ABSDataSource(1900,2000)]
            },
        'contact':
            {
                'name':'First Contact',
                'pos':[2,2],
                'data':[MockImageDataSource(), NAAImageSource('Sydney OR aboriginal OR contact OR "zheng he" OR "torres" OR "willem janszoon" OR "Abel Tasman" OR "captain cook" OR "la perouse" OR "Vasco de gama" OR "christopher columbus" OR "james stirling"', 'sydney1885.sqlite', 1788),ABSDataSource(1900,2000)]
            },
        'colonies':
            {
                'name':'The Australian Colonies',
                'pos':[3,1],
                'data':[MockImageDataSource(), NAAImageSource('Sydney OR colony OR queensland OR victoria OR "new south wales"', 'sydney1885.sqlite', 1785), NAAImageSource('Collection','sydney1955.sqlite', 1785),ABSDataSource(1900,2000)]
            },
        'nation':
            {
                'name':'Australia as a Nation',
                'pos':[3,2],
                'data':[MockImageDataSource(), NAAImageSource('nation OR australia OR federation','sydney1955.sqlite', 1890),ABSDataSource(1900,2000)]
            }
        }

    return data_sources[id]

def getSuburbFrom(lat, lon):
    data = json.load(urllib2.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng='+lat+','+lon+'&sensor=true'))
#print data

    results = data['results']
    for r in results:
        if isinstance(r, dict):
            address = r['address_components']
            for comp in address:
                if 'types' in comp:
                    if 'locality' in comp['types']:
                        return comp['long_name']

class DataSource(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def make_json(self):
        pass

CAPITALS = ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane', 'Hobart'] 
class ABSDataSource(DataSource):
    def __init__(self, startyear, endyear):
        from pymongo import MongoClient
        self.c = MongoClient()
        self.startyear, self.endyear = startyear, endyear

    def make_json(self):
        data = list(self.c.test.pop_capital.find({'capital': { '$in': CAPITALS }, 'year': { '$gt': self.startyear, '$lt': self.endyear } }))

        row = data[0]
        result = {
            'title': row['capital'],
            'subtitle': row['year'],
            'timestamp': row['year'],
            'type': 'graph'
        }

        data_per_year = defaultdict(dict)
        for e in data:
            data_per_year[str(e['year'])][e['capital']] = e['population']

        # [ { year: y, melb: 19, syd: 20, adel: 21 ... } ]
        items = []
        for year, populations in data_per_year.items():
            item = { 'year': year }
            for capital, population in populations.items():
                item[capital] = population
            items.append(item)

        result['datapoints'] = items

        return [result]

def get_year(s):
    results = re.findall(r'\d{4}', s)
    if results: return results[-1]
    return None

def troveNews():
    work = queryTroveUrl('newspaper', query)
    results = []
    for item in work:
        current = {}
        current['type'] = 'image'
        current['title'] = item['title']
        current['subtitle'] = ''
        current['timestamp'] = ''
        if "identifier" in item:
            dict = item["identifier"]
            for id in dict:
                #these only have 1 url, so we only add them if they actually have a url
                current['url'] = id['value']
            if 'linktype' in id:
                if id['linktype'] == 'thumbnail':
                    results.append(current)

    return results


def queryFlickr():
    flickr = flickrapi.FlickrAPI(api_key)
    photos = flickr.photos_search(user_id=nswuser, per_page='10', format='json')
    #print photos
    fixedPhotos = photos[14:-1]
    print fixedPhotos
    parsedPhotos = json.loads(fixedPhotos)
    dict = parsedPhotos['photos']
    photoList = dict['photo']
    results = []
    for p in photoList:
        current = {}
        title = p['title']

        current['title'] = title
        current['timestamp'] = get_year(title)
	current['start'] = current['timestamp']
	if current['timestamp'] == None:
		continue
		#print 'year is none: ' + title
	else:
		print 'year is: ' + current['timestamp']
	current['type'] = 'image'
        rawSizes = flickr.photos_getSizes(photo_id=p['id'], format='json')
	#print rawSizes
        with file('out', 'w') as f: print >>f, rawSizes[14:-1]
	sizes = json.loads(rawSizes[14:-1])
        subSizes = sizes['sizes']
        subList = subSizes['size']
        for size in subList:
                if 'label' in size:
                        if size['label'] == "Square":
                                current['thumbnail'] = size['source']
                        elif size['label'] == 'Original':
                                current['url'] = size['source']
        results.append(current)

    print 'results size:' + str(len(results))
    return results

def queryTroveUrl(zone, searchTerms):
    results = []
    for i in range(5):
        data = json.load(urllib2.urlopen('http://api.trove.nla.gov.au/result?key=5gj3f7pp9b5c0ath&zone='+zone+'&q='+searchTerms+'&encoding=json&s='+str(i*20)))
        response = data['response']
        z = response['zone']
        for rec in z:
            records = rec['records']
            if 'next' not in records:
                i = 6
            if 'work' in records:
            	work = records['work']
            	for item in work:
                	results.append(item)

    return results

def queryTroveImages(query):
    work = queryTroveUrl('picture', query)
    results = []
    for item in work:
        current = {}
        current['type'] = 'image'
        current['title'] = item['title']
        current['subtitle'] = ''
        current['timestamp'] = ''
        if "identifier" in item:
            dict = item["identifier"]
            for id in dict:
                #these only have 1 url, so we only add them if they actually have a url
                current['url'] = id['value']
            if 'linktype' in id:
                if id['linktype'] == 'thumbnail':
                    results.append(current)

    return results

def queryTroveBooks(query):
    work = queryTroveUrl('book', query) 
    results = []
    for item in work:
        current = {}
        current['type'] = 'text'
        current['title'] = item['title']
        if 'contributor' in item:
            current['subtitle'] = item['contributor']
        if 'issued' in item:
            current['start'] = str(item['issued'])
            if '-' in current['start']:
                current['start'], current['end'] = current['start'].split('-')
        if 'snippet' in item:
            current['snippet'] = item['snippet']
        if 'type' in item:
            type = item['type'] #type is an list
            for t in type:
                if t == 'Book':
                    results.append(current)

    return results

def queryTroveMedia(query):
    work = queryTroveUrl('music', query)
    results = []
    for item in work:
        current = {}
        current['type'] = 'media'
        current['title'] = item['title']
        if 'contributor' in item:
            current['subtitle'] = item['contributor']
    return results

class Endpoint(tornado.web.RequestHandler):
    def get(self):
        self.write({ 'test': 1 })
        self.finish()

class FlickrImageDataSource(DataSource):
   def make_json(self):
      return queryFlickr()

class NAAImageSource(DataSource):
    def __init__(self, query, path, startYear):
        self.query = query
        self.c = sqlite3.connect(os.path.expanduser(path))
        self.startYear = startYear
        def convert_string(s):
            try:
                u = s.decode("utf-8")
            except UnicodeDecodeError:
                u = s.decode("cp1252")
            return u

        self.c.text_factory = convert_string

        self.cursor = self.c.cursor()

    def make_json_item_from_row(self, row):
        return {
            'type': 'image',
            'title': row[1],
            'subtitle': 'Image',
            'start': row[2],
            'url': row[4],
        }

    def make_json(self):
        c = self.cursor
        print self.query
        print self.startYear
        q = "select * from links where title match '"+self.query+"' and start_date > '" + str(self.startYear) + "'"
        print q
        c.execute(q)
        #c.execute("select * from links where title match ? and start_date <= ?", (self.query, self.startYear))
        result = []
        for row in c.fetchall():
            result.append(self.make_json_item_from_row(row))
        return result

class MockImageDataSource(DataSource):
    def make_json(self):
	c= queryFlickr()
        return c
        #return queryTroveImages(topic)
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
        return queryTroveBooks(topic)

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
    def get(self):
        module_name = self.get_argument('module')

        data_sources = getDataSourceById(module_name)['data']

        response = { 'items': [] }
        for ds in data_sources:
            response['items'].extend( ds.make_json() )

        self.write(response)
        self.finish()

class App(tornado.web.RequestHandler):
    def get(self):
        self.write(file('index.html').read())
        self.finish()

class Suburb(tornado.web.RequestHandler):
    def get(self):
        lat, lon = self.get_argument('lat'), self.get_argument('lon')
        suburb = getSuburbFrom(lat, lon) 
        d = {}
        d['suburb'] = suburb
        self.write(d)
        self.finish()

class StaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r'/', App),
        (r'/endpoint', Endpoint),
        (r'/suburb', Suburb),
        (r'/data', Data),
        (r'/((?:fonts|css|js|stylesheets|images)/.+)', tornado.web.StaticFileHandler, { 'path': os.getcwd() }),
        (r'/(_.+)', StaticFileHandler, dict(path=os.getcwd())),
        (r'/(.+\.mp3)', StaticFileHandler, dict(path=os.getcwd())),     
    ], debug=True)

    app.listen(8008)
    tornado.ioloop.IOLoop().instance().start()
