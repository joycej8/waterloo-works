# WaterlooWorks Job Scraper

This project provides a tool to scrape job postings from your WaterlooWorks shortlist page using Selenium.

## Prerequisites
- Python 3.x installed on your system.
- A valid WaterlooWorks account for accessing job postings.
- WebDriver installed.

## Setup Instructions

1. **Clone the Repository**  
   Clone this repository to your local system by running:
   ```bash
   git clone git@github.com:joycej8/waterloo-works.git

2. **Install Required Dependencies**
    Install the required Python dependencies by running:
    ```bash
    pip install -r requirements.txt

3. **Configure App Settings**
Update the appsettings.json file to include your WaterlooWorks username and password.

3. **Configure User Preferences**
Update the user_preferences.yaml file to include your preferences and priority for job rankings. 

## Usage
Run the scraper (main.py) and view extracted job postings in an Exel file `waterloo_works_shortlist.xlsx`