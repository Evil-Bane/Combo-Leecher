# Combo Leecher by Evil Bane

## Overview

Combo Leecher is a Python-based GUI application designed to scrape and leech combos (email:password pairs) from various websites. The tool allows users to input keywords, utilize proxies, and efficiently gather data through multithreading. It features an advanced themed interface for ease of use.

## Features

- **Keyword-Based Scraping:** Scrapes links from specified websites based on provided keywords.
- **Proxy Support:** Option to use proxies for anonymous and secure scraping.
- **Combo Extraction:** Extracts email:password combos from the scraped links.
- **User-Friendly GUI:** Interactive and aesthetic interface built with `ttkbootstrap`.
- **Logging:** Detailed logging for monitoring the scraping process.
- **Multithreading:** Efficient scraping using multiple threads.
- **Advanced Theming:** Aesthetic and functional GUI with `ttkbootstrap`.

## Installation

To run Combo Leecher, you need Python installed on your machine. Follow the steps below to set up the application:

1. **Clone the repository:**

    ```sh
    git clone https://github.com/Evil-Bane/combo-leecher.git
    cd combo-leecher
    ```

2. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```sh
    python combo_leecher.py
    ```

## Usage

### Scraping Links

1. **Load Keywords:** Load a file containing keywords to use for scraping.
2. **Load Proxies (Optional):** Load a proxy list to enable proxy usage.
3. **Start Scraping:** Click the "Start Scraping" button to begin the scraping process.
4. **View Results:** Scraped links are saved in `Links.txt`.

### Leeching Combos

1. **Leech Combos:** The tool will automatically extract combos from the scraped links.
2. **View Results:** Leeched combos are saved in `Combos.txt`.

### GUI Features

- **Keywords Processed:** Displays the number of keywords processed.
- **Unique Links Scraped:** Shows the count of unique links scraped.
- **Unique Combos Leeched:** Displays the count of unique combos leeched.
- **Proxy Toggle:** Option to enable or disable proxy usage.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Author

Evil Bane

- **Telegram:** [https://t.me/Evil_BaneOP](https://t.me/Evil_BaneOP)
- **GitHub:** [https://github.com/Evil-Bane](https://github.com/Evil-Bane)

## Acknowledgements

Thanks to the developers of the `requests` library, `beautifulsoup4`, and the `ttkbootstrap` team for their awesome work.
