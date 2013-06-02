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

def getDataSourceById(id, lat=-33.86712312199998, lon=151.20428619999998):
    if not lat: lat = -33.86712312199998
    if not lon: lon = 151.20428619999998
    lat, lon = map(str, (lat, lon))
    suburb = getSuburbFrom(lat, lon) 
    print 'Suburb: %s' % suburb

    familyQuery = 'family OR brother OR sister OR daughter OR son OR mother OR father OR child OR uncle OR aunt'
    australiaAsANation = 'democracy OR nation OR Immigrants OR westminster OR "white australia" OR "trade union" OR "World War" OR sufferage OR Gallipoli OR kokoda OR menzies OR Parkes OR darwin OR "boer war"'
    colony = 'Sydney OR colony OR queensland OR "new south whales" OR victoria'
    firstContact = 'aboriginal OR contact OR convict OR explore OR "zheng he" OR torres OR "William Janszoon" OR "Captain Cook" OR "James Stirling" OR "First fleet"'
    community = 'Anzac OR flag OR easter OR christmas OR "Moon Festival" OR "Australia day"'
    data_sources = {
        'family': {
                'name':'Present and past family life',
                'pos' :[1,1],
                'data':[FlickrImageDataSource(["family", "brother", "sister"]), NAAImageSource(familyQuery, 'sydney1885.sqlite'), NAAImageSource(familyQuery,'sydney1955.sqlite'),NAAImageSource(familyQuery, "fts.sqlite"),ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010)]
            },
        'past':
            {
                'name':'Past in the Present',
                'pos':[1,2],
                'data':[NAAImageSource(suburb, 'sydney1885.sqlite'), NAAImageSource(suburb,'sydney1955.sqlite'),NAAImageSource(suburb, "fts.sqlite"), ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010)]
            },
        'community':
            {
                'name':'Community and Remembrance',
                'pos':[2,1],
                'data':[NAAImageSource(community, 'sydney1885.sqlite'), NAAImageSource(community,'sydney1955.sqlite'), NAAImageSource(community, 'fts.sqlite'),ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010)]
            },
        'contact':
            {
                'name':'First Contact',
                'pos':[2,2],
                'data':[ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010),
                ABSDataSource({
                    'colname' : 'pop_total_indigenous',
                    'title' : 'Indigenous Population',
                    #'subtitle' : 'Population in Australian Capitals'
                    'filter' : { 'state' : { '$in': STATES }},
                    'x-item' : 'state',
                    'y-item' : 'population',
                    'ykeys' : STATES, # ykey for AppController.js
                },1836, 2001),
                NAAImageSource(firstContact, 'sydney1885.sqlite'),NAAImageSource(firstContact, "fts.sqlite"), 
            ]
            },
        'colonies':
            {
                'name':'The Australian Colonies',
                'pos':[3,1],
                'data':[NAAImageSource(colony, 'sydney1885.sqlite'), NAAImageSource(colony, 'fts.sqlite'), ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010),
                ABSDataSource({
                   'colname' : 'sex_ratio',
                   'title' : 'Ratio of Males-to-Females by State',
                   #'subtitle' : 'Population in Australian Capitals'
                   'filter' : { 'state' : { '$in': STATES }},
                   'x-item' : 'state',
                   'y-item' : 'mf_ratio',
                   'ykeys' : STATES, # ykey for AppController.js
               }, 1796, 2004),
                ABSDataSource({
                  'colname' : 'pop_growth_pcnt',
                  'title' : 'Population Growth (%)',
                   'subtitle' : 'Population in Australian Capitals',
                  'filter' : { 'state' : { '$in': STATES }},
                  'x-item' : 'state',
                  'y-item' : 'percent_change',
                  'ykeys' : STATES, # ykey for AppController.js
               },1840, 2004)]
            },
        'nation':
            {
                'name':'Australia as a Nation',
                'pos':[3,2],
                'data':[NAAImageSource(australiaAsANation,'sydney1955.sqlite'),ABSDataSource({
                   'colname' : 'pop_capital',
                   'title' : 'Population in Australian Capitals',
                   'filter' : { 'capital' : { '$in': CAPITALS }},
                   'x-item' : 'capital',
                   'y-item' : 'population',
                   'ykeys' : CAPITALS, # ykey for AppController.js
                   #'subtitle' : 'Population in Australian Capitals'
               }, 1900, 2010)]
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


def queryFlickr(*terms):
    flickr = flickrapi.FlickrAPI(api_key)
    photos = flickr.photos_search(user_id=nswuser, per_page='100', format='json')
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
        if not any (term in title for term in terms):
            continue

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
    def __init__(self, terms):
        self.terms = terms

    def make_json(self):
        return queryFlickr(*self.terms)

class NAAImageSource(DataSource):
    def __init__(self, query, path):
        self.query = query
        self.c = sqlite3.connect(os.path.expanduser(path))
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
        c.execute('select * from links where title match ? limit 100', (self.query,))
        result = []
        for row in c.fetchall():
            result.append(self.make_json_item_from_row(row))
        return result

class MockImageDataSource(DataSource):
    def __init__(self, query):
        self.query = query

    def make_json(self):
        return queryTroveImages(self.query)
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
        lat = self.get_argument('lat', None)
        lng = self.get_argument('lng', None)

        data_sources = getDataSourceById(module_name, lat, lng)['data']

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

CAPITALS = ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane', 'Hobart']
STATES = ['ACT', 'Australia', 'NSW', 'NT', 'Qld', 'SA', 'Tas.', 'Vic.', 'WA']

class ABSDataSource(DataSource):

    def __init__(self, params, startyear, endyear):
        from pymongo import MongoClient
        self.c = MongoClient()
        self.col = self.c.test[params['colname']]
        self.startyear, self.endyear = startyear, endyear
        self.params = params
        self.filter = { 'year': { '$gt': self.startyear, '$lt': self.endyear } }
        self.filter.update(self.params.get('filter', {}))

    def make_json(self):
        #data = list(self.c.test.pop_capital.find({'capital': { '$in': CAPITALS }, 'year': { '$gt': self.startyear, '$lt': self.endyear } }))
        #data = list(self.col.find({'capital': { '$in': CAPITALS }, }))
        data = list(self.col.find(self.filter))

        row = data[0]
        result = {
            'title': self.params.get('title', self.params['colname']),  # row['capital'],
            'subtitle': self.params.get('subtitle', unicode(self.startyear) + ' - ' + unicode(self.endyear)),
            'timestamp': unicode(self.startyear) + ' - ' + unicode(self.endyear), # row['year'],
            'type': 'graph'
        }

        data_per_year = defaultdict(dict)
        x_item = self.params['x-item']
        y_item = self.params['y-item']
        year_field = self.params.get('year_field', 'year')

        for e in data:
            #data_per_year[str(e['year'])][e['capital']] = e['population']
            data_per_year[str(e[year_field])][e[x_item]] = e[y_item]

        # [ { year: y, melb: 19, syd: 20, adel: 21 ... } ]
        #items = []
        #for year, populations in data_per_year.items():
            #item = { 'year': year }
            #for capital, population in populations.items():
                #item[capital] = population
            #items.append(item)

        items = []
        for year, ys in data_per_year.items():
            item = { 'year': year }
            for x, y in ys.items():
                #x = x.replace('.', '')
                item[x] = y
            items.append(item)

        result['datapoints'] = items
        result['xkey'] = self.params.get('xkey', 'year')
        result['ykeys'] = self.params.get('ykeys', [])
        result['labels'] = self.params.get('labels', result['ykeys'])
        return [result]

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r'/', App),
        (r'/endpoint', Endpoint),
        (r'/suburb', Suburb),
        (r'/data', Data), 

        # FIXME: uncomment for ABS data sources
        # (r'/data', Data, { 'data_sources': [
        #    ABSDataSource({
        #        'colname' : 'pop_capital',
        #        'title' : 'Population in Australian Capitals',
        #        'filter' : { 'capital' : { '$in': CAPITALS }},
        #        'x-item' : 'capital',
        #        'y-item' : 'population',
        #        'ykeys' : CAPITALS, # ykey for AppController.js
        #        #'subtitle' : 'Population in Australian Capitals'
        #    }, 1900, 2010),

        #    ABSDataSource({
        #        'colname' : 'sex_ratio',
        #        'title' : 'Ratio of Males-to-Females by State',
        #        #'subtitle' : 'Population in Australian Capitals'
        #        'filter' : { 'state' : { '$in': STATES }},
        #        'x-item' : 'state',
        #        'y-item' : 'mf_ratio',
        #        'ykeys' : STATES, # ykey for AppController.js
        #    }, 1796, 2004),

        #    MockImageDataSource(),
        # ] }),

        #(r'/data', Data, { 'data_sources': [ MockImageDataSource(), MockTextDataSource(), NAAImageSource('Sydney','sydney1885.sqlite'), NAAImageSource('Collection','sydney1955.sqlite'), ABSDataSource(1900, 2000) ] }),
                                                                                                   #(r'/data', Data, { 'data_sources': [
                                                                                                       #ABSDataSource({
                                                                                                           #'colname' : 'pop_capital',
                                                                                                           #'title' : 'Population in Australian Capitals',
                                                                                                           #'filter' : { 'capital' : { '$in': CAPITALS }},
                                                                                                           #'x-item' : 'capital',
                                                                                                           #'y-item' : 'population',
                                                                                                           #'ykeys' : CAPITALS, # ykey for AppController.js
                                                                                                           ##'subtitle' : 'Population in Australian Capitals'
                                                                                                       #},1900, 2010),

                                                                                                       #ABSDataSource({
                                                                                                           #'colname' : 'sex_ratio',
                                                                                                           #'title' : 'Ratio of Males-to-Females by State',
                                                                                                           ##'subtitle' : 'Population in Australian Capitals'
                                                                                                           #'filter' : { 'state' : { '$in': STATES }},
                                                                                                           #'x-item' : 'state',
                                                                                                           #'y-item' : 'mf_ratio',
                                                                                                           #'ykeys' : STATES, # ykey for AppController.js
                                                                                                       #},1796, 2004),

                                                                                                       #ABSDataSource({
                                                                                                           #'colname' : 'pop_total_indigenous',
                                                                                                           #'title' : 'Indigenous Population',
                                                                                                           ##'subtitle' : 'Population in Australian Capitals'
                                                                                                           #'filter' : { 'state' : { '$in': STATES }},
                                                                                                           #'x-item' : 'state',
                                                                                                           #'y-item' : 'population',
                                                                                                           #'ykeys' : STATES, # ykey for AppController.js
                                                                                                       #},1836, 2001),

                                                                                                       #ABSDataSource({
                                                                                                           #'colname' : 'pop_growth',
                                                                                                           #'title' : 'Population Growth',
                                                                                                           ##'subtitle' : 'Population in Australian Capitals'
                                                                                                           #'filter' : { 'state' : { '$in': STATES }},
                                                                                                           #'x-item' : 'state',
                                                                                                           #'y-item' : 'change',
                                                                                                           #'ykeys' : STATES, # ykey for AppController.js
                                                                                                       #},1789, 2004),

                                                                                                       #ABSDataSource({
                                                                                                       #    'colname' : 'pop_growth_pcnt',
                                                                                                       #    'title' : 'Population Growth (%)',
                                                                                                           #'subtitle' : 'Population in Australian Capitals'
                                                                                                       #    'filter' : { 'state' : { '$in': STATES }},
                                                                                                       #    'x-item' : 'state',
                                                                                                       #    'y-item' : 'percent_change',
                                                                                                       #    'ykeys' : STATES, # ykey for AppController.js
                                                                                                       #},1840, 2004),
                                                                                                       #},1789, 2004),
                                                                                                       #MockImageDataSource(),
        (r'/((?:fonts|css|js|stylesheets|images)/.+)', tornado.web.StaticFileHandler, { 'path': os.getcwd() }),
        (r'/(_.+)', StaticFileHandler, dict(path=os.getcwd())),
        (r'/(.+\.mp3)', StaticFileHandler, dict(path=os.getcwd())),
    ], debug=True)

    app.listen(8008)
    tornado.ioloop.IOLoop().instance().start()
