# Country Information Scraper

A FastAPI web application that fetches and displays detailed information about countries using the REST Countries API, utilizing Scrapy for data fetching.

## Features

- Fetch country data by name, capital, region, subregion, language, or currency.
- Display information such as capital, population, region, and more.
- Handle errors gracefully, providing meaningful messages for not found and network errors.
- **Asynchronous Processing**: Utilizes asynchronous programming with `asyncio` and `Scrapy` for efficient data retrieval.
- **Testing**: Includes a comprehensive suite of unit tests to ensure application reliability.

## Prerequisites

- **Python 3.7 or higher**
- **Git**
- **Virtual Environment Tool**: Recommended to use `venv` or `virtualenv` to manage project dependencies separately.

**Ensure you have Python and Git installed on your machine.**

## Installation

**1. Clone the Repository**

Open your terminal or command prompt and run:

```
git clone https://github.com/yourusername/country-information-scraper.git
cd country-information-scraper
```

Replace yourusername with your GitHub username if you've forked the repository.

**2. Create a Virtual Environment**

On Windows:
python -m venv venv
venv\Scripts\activate

On macOS and Linux:

python3 -m venv venv
source venv/bin/activate

**3. Upgrade pip (Optional but Recommended)**

```
python -m pip install --upgrade pip
```

**4. Install Requirements**

```
pip install -r requirements.txt
```

**5. Configure Environment Variables (Optional)**

If your application requires environment variables (e.g., for API keys), set them up accordingly. For this project, no additional environment variables are needed.

## Running the Application

**1. Start the FastAPI Server**

Run the following command to start the server:

```
uvicorn country_scraper.main:app --reload
```

**2. Access the Application**

API Root: http://127.0.0.1:8000/
Interactive API Documentation (Swagger UI): http://127.0.0.1:8000/docs
Alternative API Documentation (ReDoc): http://127.0.0.1:8000/redoc

## Running Tests

To ensure that everything is working correctly, run the test suite:

```
pytest
```

Usage

```
GET /countries/
```

Fetch country information based on a specific search criterion. Only one search criterion can be used per request.

## Query Parameters

- name: (string) Name of the country.
- capital: (string) Capital city of the country.
- region: (string) Region where the country is located (e.g., Europe, Asia).
- subregion: (string) Subregion where the country is located (e.g., Northern Europe).
- language: (string) Language spoken in the country (use full language name, e.g., english).
- currency: (string) Currency used in the country (e.g., USD, Euro).

## Usage Notes

- Single Criterion: Only one search criterion should be provided per request. Providing multiple criteria will result in a 400 Bad Request error.
- Case Sensitivity: Search parameters are not case-sensitive.
- Language Input: For the language parameter, use the full language name in English (e.g., english, spanish).

## Examples

Request:

```
GET /countries/?name=Poland HTTP/1.1
Host: 127.0.0.1:8000
```

Response (Status Code: 200):

```
[
  {
    "name": {
      "common": "Poland",
      "official": "Republic of Poland",
      // ...
    },
    "capital": ["Warsaw"],
    "region": "Europe",
    "subregion": "Central Europe",
    "languages": {
      "pol": "Polish"
    },
    "currencies": {
      "PLN": {
        "name": "Polish złoty",
        "symbol": "zł"
      }
    },
    // Additional country details...
  }
]
```

## Error Handling Examples

No Criteria Provided

Request:

```
GET /countries/ HTTP/1.1
Host: 127.0.0.1:8000
```

Response (Status Code: 400):

```
{
  "detail": "No search criteria provided."
}
```

## Project Structure

- country_scraper/: Main application package.
- main.py: Defines the FastAPI application and API endpoint.
- services.py: Contains the Scrapy spider and functions for data retrieval.
- tests/: Contains unit tests for the application.
- test_main.py: Test suite for the API endpoint.
- requirements.txt: Lists project dependencies.
- pytest.ini: Configuration file for Pytest.
- .gitignore: Specifies files and directories to be ignored by Git.
- README.md: Project documentation.
