YEAR_MONTH = [f'2020-{str(month).zfill(2)}' for month in range(3, 12)]

ALL_DATES = [   ['03-'+str(day).zfill(2) for day in range(23, 30)],
                ['04-'+str(day).zfill(2) for day in range(6, 13)],
                ['04-'+str(day).zfill(2) for day in range(20, 27)],
                ['05-'+str(day).zfill(2) for day in range(4, 11)],
                ['05-'+str(day).zfill(2) for day in range(18, 25)],
                ['06-'+str(day).zfill(2) for day in range(1, 8)],
                ['06-'+str(day).zfill(2) for day in range(15, 22)],
                ['07-'+str(day).zfill(2) for day in range(28, 32)] + ['08-01', '08-02'],
                ['08-'+str(day).zfill(2) for day in range(10, 17)],
                ['08-'+str(day).zfill(2) for day in range(24, 31)],
                ['09-'+str(day).zfill(2) for day in range(7, 14)],
                ['09-'+str(day).zfill(2) for day in range(21, 28)],
                ['10-'+str(day).zfill(2) for day in range(5, 12)],
                ['10-'+str(day).zfill(2) for day in range(19, 26)],
                ['11-'+str(day).zfill(2) for day in range(2, 9)],
                ['11-'+str(day).zfill(2) for day in range(16, 23)],   ] # 16 dates in total

SELECTED_COUNTRIES = ['United States', 'United Kingdom', 'Canada', 'Australia', 'France', 'Germany', 'Spain', 'Turkey']

SELECTED_DOMAINS = ["bbc", "cnn", "nytimes", "reuters", 'washingtonpost', "theguardian", "breitbart", "foxnews", "dailymail.co.uk"]

VERBOSE = 100000

MBFC_SOURCE_URL = 'https://mediabiasfactcheck.com/{page}/'