# DataJobScrape

## Instructions
1. Verify chromedriver is the same version as your browser.
1B. Optional: Set max number of pages for each job site from url_max_pages in DataJobScrape/jobSpider/listings.py
2. From DataJobScrape/jobSpider Run scrapy crawl listing -o urls.jl
2B. listing script only works on one start url at a time, so comment out the current url and uncomment the next to scrape other job sites.
3. Once url.jl is created Run scrapy crawl job -o job.csv
3A. Optional: Run python3 ./plotting/plot.py to generate simple plots.

## Scraped Job Information
- Job Title
- Job Category
- Employment type
- Location
- Description
- Salary
- Required Skills / Requirements / Qualifications /  Who We Need

## Scraped Job sites
1. https://www.usajobs.gov
2. https://www.progressivedatajobs.org/job-postings/
3. https://outerjoin.us
4. https://weworkremotely.com

## Plots
- Average Salary by Location, Schedule(permanent, temporary, contract) ,and type(full-time/part-time) 
- Counts of key terms in Requirements
  - Each term only counted once per job

## Potential sites to scrape:
### JS
1. https://www.usajobs.gov
2. https://icrunchdata.com/jobs/?&p=1&s=3785
3. https://builtin.com/jobs
4. https://www.f6s.com/jobs?sort=newest
5. https://appstate.joinhandshake.com/stu
### Less JS
1. https://datajobs.com
2. https://www.progressivedatajobs.org/job-postings/
3. https://hired.com
4. https://outerjoin.us
5. https://weworkremotely.com

## Info to plot
- Average salary within a location with 25+ jobs, full-time/part-time, permanant/temp
- Counts of programming languages 
- Plot years of experience by salary
- Topic modeling grouped by job types for Description, Responsibilites, & skills
