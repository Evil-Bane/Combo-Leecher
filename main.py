import re
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import os
import threading
import logging
import random
import webbrowser  # Import webbrowser for opening links
from concurrent.futures import ThreadPoolExecutor
import ttkbootstrap as tb  # Import ttkbootstrap for advanced theming and animations

# Setup logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize global variables
combined_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+:\w+\b')
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.bing.com"
}
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    # Add more user agents here
]
proxies = []
site_list = ['pastebin.com', 'throwbin.com', 'zerobin.com', 'badcord.ct8.pl', 'justpaste.it']
max_retries = 5  # Maximum number of retries for a request

# Function to get random headers
def get_random_headers():
    headers['User-Agent'] = random.choice(user_agents)
    return headers

# Function to load proxies from a file
def load_proxies():
    global proxies
    proxy_file = filedialog.askopenfilename(title="Load Proxy File")
    if proxy_file:
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
        logging.info("Proxies loaded successfully.")
        messagebox.showinfo("Success", "Proxies loaded successfully.")
    else:
        messagebox.showerror("Error", "No proxy file selected.")

# Function to get a random proxy
def get_proxy():
    if proxies:
        proxy = random.choice(proxies)
        if "@" in proxy:
            auth, ip_port = proxy.split("@")
            username, password = auth.split(":")
            return {
                "http": f"http://{username}:{password}@{ip_port}",
                "https": f"http://{username}:{password}@{ip_port}"
            }
        else:
            return {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
    else:
        return None

# Function to get keywords from a file
def get_keywords():
    current_path = os.path.dirname(os.path.realpath(__file__))
    root = Tk()
    root.withdraw()
    key_file = filedialog.askopenfilename(initialdir=current_path, title="Load Keywords File")
    root.destroy()
    if key_file:
        with open(key_file, "r", encoding='utf-8', errors='ignore') as f:
            return f.read().splitlines()
    else:
        return []

# Function to get links from HTML content
def get_links(html):
    data = []
    parse_html = BeautifulSoup(html, 'html.parser')
    links = parse_html.find_all('a', href=True)
    exclusions = ["www.netflix.com", "www.bing.com", "microsoft.com", "wikipedia.org", 
                  "www.imdb.com", "www.pinterest.com", "www.maps.google", ".pdf", 
                  "www.youtube.com", "www.facebook.com", "www.instagram.com", 
                  "http://www.google.", "www.paypal.com", "/search?q=", 
                  "play.google.com", "steamcommunity.com", "www.reddit.com", 
                  "www.amazon.", "business.facebook.com", "facebook.com", 
                  "yahoo.com", "msn.com", "tiktok.com"]
    for link in links:
        href = link['href']
        if all(excl not in href for excl in exclusions) and href.startswith("http"):
            data.append(href)
    return data

# Function to fetch data with proxy support
def fetch_data_with_proxy(url, retries=0):
    if retries >= max_retries:
        logging.error(f"Max retries reached for URL: {url}")
        return []
    proxy = get_proxy()
    try:
        req = requests.get(url, headers=get_random_headers(), proxies=proxy, timeout=10)
        req.raise_for_status()
        return get_links(req.text)
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url} with proxy {proxy}: {e}")
        return fetch_data_with_proxy(url, retries + 1)

# Function to fetch data without proxy support
def fetch_data_without_proxy(url):
    try:
        req = requests.get(url, headers=get_random_headers(), timeout=10)
        req.raise_for_status()
        return get_links(req.text)
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return []

# Function to get data using keywords and website list
def get_data(keyword, website_list, unique_links):
    def fetch_data(site_link):
        url = f'https://www.bing.com/search?q=site:{site_link} {keyword}'
        return fetch_data_with_proxy(url) if use_proxy.get() else fetch_data_without_proxy(url)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_data, website_list)
        for scraped_links in results:
            with open("Links.txt", 'a') as save:
                for link in scraped_links:
                    if link not in unique_links:
                        unique_links.add(link)
                        save.write(link + '\n')
    return unique_links

# Function to leech combos from a link
def leech_combo(link, unique_combos, combo_list):
    try:
        req = requests.get(link, headers=get_random_headers(), proxies=get_proxy() if use_proxy.get() else None, timeout=10)
        req.raise_for_status()
        combo = combined_pattern.findall(req.text)
        with open("Combos.txt", 'a') as save:
            for item in combo:
                if item not in unique_combos:
                    unique_combos.add(item)
                    save.write(item + '\n')
                    combo_list.insert(END, item)
        return unique_combos
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {link}: {e}")
        return unique_combos

# Function to start scraping process
def start_scraping(root, scraped_links_list, site_list):
    key_list = keyword_list.get(0, END)
    if key_list:
        total_keywords = len(key_list)
        keywords_processed = 0
        links_processed = 0
        unique_links = set()

        # Clear the Links.txt file before scraping
        open("Links.txt", "w").close()

        progress_bar.config(mode='determinate', maximum=total_keywords)
        for keyword in key_list:
            unique_links = get_data(keyword, site_list, unique_links)
            keywords_processed += 1
            progress_bar.step(1)
            keyword_label.config(text=f"Keywords Processed: {keywords_processed}/{total_keywords}")
            unique_links_label.config(text=f"Unique Links Scraped: {len(unique_links)}")
            root.update()

            # Update the scraped links list in real-time
            update_scraped_links_list(scraped_links_list)

        messagebox.showinfo("Task Complete", "All links leeched, Proceeding to leech combos!")

        total_links = len(unique_links)
        links_progress_bar.config(mode='determinate', maximum=total_links)

        unique_combos = set()
        with open("Links.txt", 'r') as get_links_file:
            for link in get_links_file:
                unique_combos = leech_combo(link.strip(), unique_combos, combo_list)
                links_processed += 1
                links_progress_bar.step(1)
                links_label.config(text=f"Links Processed: {links_processed}/{total_links}")
                combos_label.config(text=f"Unique Combos Leeched: {len(unique_combos)}")
                root.update()

        start_button.config(state=NORMAL)
        load_keywords_button.config(state=NORMAL)
        keyword_list.config(state=NORMAL)
        messagebox.showinfo("Task Complete", "Combo leeching finished!")
    else:
        messagebox.showerror("Error", "No keywords added.")

# Function to load keywords from a file
def load_keywords():
    keywords = get_keywords()
    if keywords:
        keyword_list.delete(0, END)
        for keyword in keywords:
            keyword_list.insert(END, keyword)
        start_button.config(state=NORMAL)
    else:
        messagebox.showerror("Error", "No keywords file selected.")

# Function to update scraped links list in the GUI
def update_scraped_links_list(scraped_links_list):
    with open("Links.txt", "r") as file:
        links = file.readlines()
        scraped_links_list.delete(0, END)
        for link in links:
            scraped_links_list.insert(END, link.strip())

# Function to toggle proxy usage
def toggle_proxy():
    if use_proxy.get():
        load_proxies_button.grid(row=2, column=2, pady=5, padx=10, sticky='ew')
    else:
        load_proxies_button.grid_forget()

# Function to create the main GUI
def create_gui():
    global start_button, progress_bar, keyword_label, links_progress_bar, links_label, keyword_list, load_keywords_button, links_list, notebook, scrape_tab, leech_tab, about_tab, scraped_links_list, unique_links_label, combos_label, combo_list, load_proxies_button, use_proxy, root

    root = tb.Window(themename="darkly")
    root.title("Combo Leecher")
    root.state('zoomed')  # Set to full screen
    root.resizable(True, True)

    use_proxy = BooleanVar()  # Define use_proxy here

    notebook = tb.Notebook(root, bootstyle="primary")
    notebook.pack(fill=BOTH, expand=True)

    scrape_tab = tb.Frame(notebook, bootstyle="secondary")
    leech_tab = tb.Frame(notebook, bootstyle="secondary")
    about_tab = tb.Frame(notebook, bootstyle="secondary")

    notebook.add(scrape_tab, text="Scrape Links")
    notebook.add(leech_tab, text="Leech Combos")
    notebook.add(about_tab, text="About Us")

    # Scrape Links Tab
    title_label = tb.Label(scrape_tab, text="Combo Leecher", font=("Helvetica", 30, "bold"), bootstyle="inverse-dark")
    title_label.grid(row=0, column=0, columnspan=3, pady=20)

    creator_label = tb.Label(scrape_tab, text="Created by: Evil Bane", font=("Helvetica", 16), bootstyle="inverse-dark")
    creator_label.grid(row=1, column=0, columnspan=3, pady=10)

    load_keywords_button = tb.Button(scrape_tab, text="Load Keywords", command=load_keywords, bootstyle="success-outline", width=20)
    load_keywords_button.grid(row=2, column=0, pady=10, padx=20, sticky='ew')

    proxy_toggle = tb.Checkbutton(scrape_tab, text="Use Proxy", variable=use_proxy, command=toggle_proxy, bootstyle="secondary", width=20)
    proxy_toggle.grid(row=2, column=1, pady=10, padx=20, sticky='ew')

    load_proxies_button = tb.Button(scrape_tab, text="Load Proxies", command=load_proxies, bootstyle="success-outline", width=20)
    load_proxies_button.grid(row=2, column=2, pady=5, padx=10, sticky='ew')
    load_proxies_button.grid_forget()

    keyword_frame = tb.Frame(scrape_tab, bootstyle="secondary")
    keyword_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=20, sticky='nsew')

    keyword_list_scrollbar = tb.Scrollbar(keyword_frame, bootstyle="secondary")
    keyword_list_scrollbar.pack(side=RIGHT, fill=Y)

    keyword_list = Listbox(keyword_frame, height=8, yscrollcommand=keyword_list_scrollbar.set, bg="#444", fg="white", selectbackground="#4CAF50", font=("Helvetica", 16))
    keyword_list.pack(side=LEFT, fill=BOTH, expand=True)
    keyword_list_scrollbar.config(command=keyword_list.yview)

    stats_frame = tb.Frame(scrape_tab, bootstyle="secondary")
    stats_frame.grid(row=4, column=0, rowspan=2, columnspan=2, pady=10, padx=20, sticky='nsew')

    keyword_label = tb.Label(stats_frame, text="Keywords Processed: 0/0", font=("Helvetica", 16), bootstyle="inverse-dark")
    keyword_label.pack(pady=10)

    unique_links_label = tb.Label(stats_frame, text="Unique Links Scraped: 0", font=("Helvetica", 16), bootstyle="inverse-dark")
    unique_links_label.pack(pady=10)

    start_button = tb.Button(scrape_tab, text="Start Scraping", command=lambda: threading.Thread(target=start_scraping, args=(root, scraped_links_list, site_list)).start(), bootstyle="danger", state=DISABLED, width=20)
    start_button.grid(row=4, column=2, pady=20, padx=20, sticky='nsew')

    progress_bar = tb.Progressbar(scrape_tab, mode='determinate', length=600, bootstyle="info")
    progress_bar.grid(row=6, column=0, columnspan=3, pady=20)

    scraped_links_frame = tb.Frame(scrape_tab, bootstyle="secondary")
    scraped_links_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=20, sticky='nsew')

    scraped_links_scrollbar = tb.Scrollbar(scraped_links_frame, bootstyle="secondary")
    scraped_links_scrollbar.pack(side=RIGHT, fill=Y)

    scraped_links_list = Listbox(scraped_links_frame, height=8, yscrollcommand=scraped_links_scrollbar.set, bg="#444", fg="white", selectbackground="#4CAF50", font=("Helvetica", 16))
    scraped_links_list.pack(side=LEFT, fill=BOTH, expand=True)
    scraped_links_scrollbar.config(command=scraped_links_list.yview)

    # Leech Combos Tab
    combo_list_frame = tb.Frame(leech_tab, bootstyle="secondary")
    combo_list_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    combo_list_scrollbar = tb.Scrollbar(combo_list_frame, bootstyle="secondary")
    combo_list_scrollbar.pack(side=RIGHT, fill=Y)

    combo_list = Listbox(combo_list_frame, height=8, yscrollcommand=combo_list_scrollbar.set, bg="#444", fg="white", selectbackground="#4CAF50", font=("Helvetica", 16))
    combo_list.pack(side=LEFT, fill=BOTH, expand=True)
    combo_list_scrollbar.config(command=combo_list.yview)

    combos_label = tb.Label(leech_tab, text="Unique Combos Leeched: 0", font=("Helvetica", 16), bootstyle="inverse-dark")
    combos_label.pack(pady=10)

    links_label = tb.Label(leech_tab, text="Links Processed: 0/0", font=("Helvetica", 16), bootstyle="inverse-dark")
    links_label.pack(pady=10)

    links_progress_bar = tb.Progressbar(leech_tab, mode='determinate', length=600, bootstyle="info")
    links_progress_bar.pack(pady=20)

    # About Us Tab
    about_title_label = tb.Label(about_tab, text="About Combo Leecher", font=("Helvetica", 30, "bold"), bootstyle="inverse-dark")
    about_title_label.pack(pady=20)

    about_creator_label = tb.Label(about_tab, text="Created by: Evil Bane", font=("Helvetica", 20), bootstyle="inverse-dark")
    about_creator_label.pack(pady=10)

    contact_label = tb.Label(about_tab, text="Contact:", font=("Helvetica", 18), bootstyle="inverse-dark")
    contact_label.pack(pady=10)

    telegram_label = tb.Label(about_tab, text="Telegram: https://t.me/Evil_BaneOP", font=("Helvetica", 16), bootstyle="inverse-dark", cursor="hand2")
    telegram_label.pack(pady=5)
    telegram_label.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/Evil_BaneOP"))

    github_label = tb.Label(about_tab, text="GitHub: https://github.com/Evil-Bane", font=("Helvetica", 16), bootstyle="inverse-dark", cursor="hand2")
    github_label.pack(pady=5)
    github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Evil-Bane"))

    root.mainloop()

if __name__ == "__main__":
    create_gui()
