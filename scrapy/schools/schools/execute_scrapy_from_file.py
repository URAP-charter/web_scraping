from scrapy import cmdline

SCRAPY_RUN_CMD = "scrapy crawl schoolspider -a school_list="

def execute_scrapy_from_file(filename):
    run_cmd = SCRAPY_RUN_CMD + str(filename)
    print(run_cmd)
    try:
        cmdline.execute(run_cmd.split())
        return 0
    except:
        return 1

