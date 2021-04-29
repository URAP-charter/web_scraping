# Web-Scraping with Scrapy: Spiders and Utilities
Our goal is a scalable, robust web-crawling pipeline (in Python) applicable across web designs and accessible for researchers with minimal computational skills. Our method involves using Scrapy spiders to recursively gather website links (to a given depth), collect and parse items (text, images, PDFs, and .docs) using BeautifulSoup and textract, and saving them locally and/or to MongoDB. 

The most recent web scraper is `scrapy/schools/schools/spiders/scrapy_vanilla.py`. See usage notes below.

Expect our spider and setup to continue being improved on, with better documentation and maybe even a web portal/user interface in the future. But if you're just trying to scrape website text, this should prove resilient as is.


## Usage notes
`scrapy_vanilla.py` uses scrapy's LinkExtractor to crawl recursively--meaning that it will crawl not just the a given input URL, but also those links it finds that start with that. For instance, if you feed it `site.com`, it will scrape `site.com/page`-- but not 'yelp.com' or other places outside the given root. 

URLs to scrape are loaded from `scrapy/schools/schools/spiders/test_urls.csv`. The simplest way to feed the spider new URLs is by updating this file. To test scalability, feel free to use the full list of 6K+ charter school URLs (gathered in 2018) in `scrapy/charter_schools_urls_2018.csv`. 

You'll get best results if you deploy the spider from within a scrapy project, like in our `scrapy/schools/` folder, because we've fine-tuned the `items.py`, `middlewares.py`, `settings.py`, and `pipelines.py` configurations (all under `scrapy/schools/schools/`)--and `scrapy_vanilla.py` draws on these.


## Running the web scraper

### Method 1: install and run locally

If not yet installed, [install MongoDB](https://docs.mongodb.com/manual/installation/).

Navigate to the `/web_scraping/scrapy/schools` directory.
Then run the following commands:
```bash
# Create and start a virtual environment for Python dependencies.
python3 -m venv .venv
source .venv/bin/activate
# Install dependencies.
pip3 install -r requirements.txt
```
If you want to store results into MongoDB, ensure that:

```python
'schools.pipelines.MongoDBPipeline': 300
```
is one of the key-value pairs of `ITEM_PIPELINES` in `/web_scraping/scrapy/schools/schools/settings.py` by uncommenting the line. If you don't want to use the pipeline, remove the element.

Furthermore, ensure that in `/web_scraping/scrapy/schools/schools/settings.py`, that:
```python
# This next line must NOT be commented.
MONGO_URI = 'mongodb://localhost:27017' 
# This next line is commented.
# MONGO_URI = 'mongodb://mongodb_container:27017'

Also, ensure the line
MONGO_DATABASE = 'schoolSpider'
is uncommented.
```
Start MongoDB. This step depends on the operating system. On Ubuntu 18.04, this is:
```bash
sudo systemctl -l start mongodb
```
With Docker, you can start it with:
```bash
docker pull mongo
docker run -p 27017:27017 --name mongodb mongo
```
To stop MongoDB running in Docker:
```bash
docker stop mongodb
```

Finally to run, navigate to `/web_scraping/scrapy/schools/schools/` and run:

```bash
scrapy crawl schoolspider -a school_list=spiders/test_urls.csv -o schoolspider_output.json
```

This line means to run the schoolspider crawler with the given csv or tsv input file
and append the output to a json file. Note that subsequent runs of the crawler wsill append output, rather than replace. 
Appending to a json file is optional and the crawler can be run without doing this. Not specified in this command, is that data is saved behind the scenes
to a MongoDB database named "schoolSpider" if the MongoDB pipeline is used.

## Adding Logging
To add a log output file, you'll need to add '-L' and '--logfile' flags. The -L flag specifies the level of logging, such as 'INFO', 'DEBUG', or 'ERROR', and specifies what types of log messages appear in the log file. The --logfile flag specifies the output file location, such as './schoolspider\_log\_1\_1\_2021.log'

A sample command with a log file:

```bash
scrapy crawl schoolspider -a school_list=spiders/test_urls.csv -o schoolspider_output.json -L INFO --logfile ../logs/schoolspider_log_4_13_2021.log
```

When you're finished and you don't need to run the scraper anymore run:
```
# Deactivate the environment.
deactivate
```

### Method 2: install and run in a container.

Firstly, [get Docker](https://docs.docker.com/get-docker/).

If you want to use MongoDB, ensure that in `/web_scraping/scrapy/schools/schools/settings.py`, that:
```python
# This next line is commented.
# MONGO_URI = 'mongodb://localhost' 
# This next line must NOT be commented.
MONGO_URI = 'mongodb://mongodb_container:27017'

Also, ensure that you uncomment the line:
MONGO_DATABASE = 'schoolSpider'
```
And, that:
```python
'schools.pipelines.MongoDBPipeline': 300
```
is one of the key-value pairs in of `ITEM_PIPELINES` in `/web_scraping/scrapy/schools/schools/settings.py` by uncommenting the line. If you don't want to use the pipeline, remove the element.

You will also need to set the "MONGO\_USERNAME" and "MONGO\_PASSWORD" properties in order to connect to MongoDB. 

Finally, inside `/web_scraping`, run:
```bash
# build the containers and run in the background
docker-compose up --build -d 
# to shutdown when finished
docker-compose down
```
No output json file is created through this method. Rather, the primary method of storing data is through MongoDB
(if it's enabled). Data inside MongoDB is persisted through a volume defined in `docker-compose.yml`.

The Mongo container can be easily accessed by "exec"ing into the container:
```bash
docker exec -it mongodb_container bash
```
Note: if running on a Windows machine, you will need to prefix that command with 'winpty'

From there, you can enter 'mongo' to start the Mongo CLI within the container, and it can be navigated the same as Mongo on your computer.

### Running a "Swarm" of Spiders

With Docker, we can easily run a group of spiders from a long input list.

Start by instantiating a MongoDB on your local machine:
```bash
docker run -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME=username -e MONGO_INITDB_ROOT_PASSWORD=password mongo
```

Next, build the school spider container, from the same directory as "Dockerfile" (scrapy/schools):
```bash
docker build . -t schoolcrawler
```

Finally, run the crawler:
```bash
docker run --network='host' -d schoolcrawler
```

Progress can be checked in the logs:
```bash
docker logs [containerid] --follow
```

Or by checking Mongo:
```bash
docker exec -it mongodb bash
mongo -u username -p password
show dbs
```


## Updates to come
- Distributed crawling: Coordinating spiders vertically using instances of scrapyd and a big data platform with Spark, Hadoop, and HIVE
- Error checking: Middlewares to check crawling fidelity and backup crawling approach (wget)
- Crawling history: Crawling websites over time using Internet Archive ([see example code here](http://sangaline.com/post/wayback-machine-scraper/))
