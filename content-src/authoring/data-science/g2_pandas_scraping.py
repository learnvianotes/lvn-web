from kit import *

G = "Pandas"

FLOWERS = '''
        import pandas as pd
        from io import StringIO

        csv = """species,size,fragrance,height_cm
        rose,medium,mild,48.55
        shoeblack plant,medium,mild,147.07
        shoeblack plant,medium,none,102.93
        hibiscus,large,none,184.00
        shoeblack plant,large,mild,83.07
        rose,small,strong,35.20
        hibiscus,large,,126.69
        rose,medium,mild,88.11
        """
        df = pd.read_csv(StringIO(csv))       # same call you'd use with a file path
'''


@topic(G, "pandas-basics", "Series & DataFrames", "table")
def _():
    yield lead("Pandas gives Python two labelled data structures — the one-dimensional `Series` and the two-dimensional `DataFrame` — the everyday tools for tabular data.")
    yield cards(
        ("Series", "One column: values plus an **index** (labels). Like a NumPy array with names.", "list"),
        ("DataFrame", "A table: several Series sharing one index — rows and named columns, like a spreadsheet or SQL table.", "table"),
    )
    yield section("Series", "list")
    yield code('''
        import numpy as np
        import pandas as pd
        s = pd.Series(np.array(["g", "e", "e", "k", "s"]))
        print(s.tolist(), s.index.tolist())      # ['g', 'e', 'e', 'k', 's'] [0, 1, 2, 3, 4]
        prices = pd.Series([40, 25, 60], index=["tea", "milk", "coffee"])
        print(prices["coffee"], prices.max())    # 60 60
        print(prices[prices > 30].to_dict())     # {'tea': 40, 'coffee': 60}
    ''')
    yield section("Creating DataFrames", "table-plus")
    yield code('''
        import pandas as pd
        from_rows = pd.DataFrame([["a", 10], ["b", 15], ["c", 14]], columns=["Name", "Age"])
        from_dict = pd.DataFrame({"Name": ["Tom", "Jack", "Steve", "Ricky"], "Age": [28, 34, 29, 42]})
        print(from_rows.shape, from_dict.shape)          # (3, 2) (4, 2)
        print(from_dict)
    ''', check=False)
    yield shell('''
        (3, 2) (4, 2)
            Name  Age
        0    Tom   28
        1   Jack   34
        2  Steve   29
        3  Ricky   42
    ''', caption="Output")
    yield warn("Building a DataFrame from a NumPy array of mixed values (as the notebook does with `np.array([['a', 10], …])`) turns **every** value into a string — `Age` would be text. Use lists or a dict so each column keeps its own type.", "Pitfall")
    yield code('''
        import numpy as np
        import pandas as pd
        bad = pd.DataFrame(np.array([["a", 10], ["b", 15]]), columns=["Name", "Age"])
        good = pd.DataFrame([["a", 10], ["b", 15]], columns=["Name", "Age"])
        print(bad["Age"].tolist(), good["Age"].tolist())    # ['10', '15'] [10, 15]
    ''')
    yield section("Selecting columns and rows", "click")
    yield code(FLOWERS + '''
        print(df.columns.tolist())             # ['species', 'size', 'fragrance', 'height_cm']
        print(type(df["species"]).__name__)    # Series
        print(df[["species", "fragrance"]].shape)   # (8, 2)
        print(df.loc[3, "species"])            # hibiscus      ← by label
        print(df.iloc[0]["species"], df.iloc[0]["height_cm"])   # rose 48.55     ← by position
    ''')
    yield table(
        ["Syntax", "Selects"],
        ["`df[\"col\"]`", "One column → Series"],
        ["`df[[\"a\", \"b\"]]`", "Several columns → DataFrame"],
        ["`df.loc[row_label, col_label]`", "By labels (slices include the end)"],
        ["`df.iloc[i, j]`", "By integer position (slices exclude the end)"],
        ["`df[df[\"x\"] > 5]`", "Rows matching a condition"],
    )
    yield section("Reading and writing files", "file-spreadsheet")
    yield code('''
        import pandas as pd
        df = pd.DataFrame({"Names": ["Geeks", "For", "Geeks"]}, index=["a", "b", "c"])
        df.to_csv("names.csv")                         # writes the index too
        back = pd.read_csv("names.csv", index_col=0)   # read it back, using column 0 as the index
        print(back.equals(df))                         # True
        df.to_csv("names_no_index.csv", index=False)   # usually what you want for exports
    ''')
    yield note("`read_csv` has many options: `sep`, `header`, `index_col`, `usecols` (pick columns), `nrows` (read only the first n rows), `skiprows`, `parse_dates`. There's also `read_excel`, `read_json`, `read_sql` and `to_…` counterparts.")


@topic(G, "pandas-analysis", "Exploring a Dataset", "chart-bar")
def _():
    yield lead("A first pass over any new dataset: look at it, check types and missing values, summarise, filter, group. Here with a small version of the notebook's flower dataset.")
    yield section("First look", "eye")
    yield code(FLOWERS + '''
        print(df.shape)                                  # (8, 4)
        print(df.head(2).to_dict("records"))             # [{'species': 'rose', 'size': 'medium', 'fragrance': 'mild', 'height_cm': 48.55}, {'species': 'shoeblack plant', 'size': 'medium', 'fragrance': 'mild', 'height_cm': 147.07}]
        print(df.dtypes.astype(str).to_dict())           # {'species': 'str', 'size': 'str', 'fragrance': 'str', 'height_cm': 'float64'}
    ''')
    yield table(
        ["Method", "Tells you"],
        ["`df.head(n)` / `df.tail(n)`", "First / last rows"],
        ["`df.shape`", "(rows, columns)"],
        ["`df.info()`", "Column types and non-null counts"],
        ["`df.describe()`", "Count, mean, std, min, quartiles, max of numeric columns"],
        ["`df[\"col\"].value_counts()`", "How often each value appears"],
        ["`df.isna().sum()`", "Missing values per column"],
    )
    yield section("Missing values", "alert-circle")
    yield code(FLOWERS + '''
        print(df.isna().sum().to_dict())                 # {'species': 0, 'size': 0, 'fragrance': 1, 'height_cm': 0}
        filled = df.fillna({"fragrance": "unknown"})
        print(filled.loc[6, "fragrance"])                # unknown
        print(len(df.dropna()))                          # 7
    ''')
    yield note("Decide per column: **drop** rows (`dropna`), **fill** with a value or the mean/median (`fillna`), or keep and flag. Never silently ignore them.")
    yield section("Summaries", "chart-histogram")
    yield code(FLOWERS + '''
        print(df["species"].value_counts().to_dict())     # {'rose': 3, 'shoeblack plant': 3, 'hibiscus': 2}
        print(round(df["height_cm"].mean(), 2))           # 101.95
        print(df["height_cm"].describe()[["min", "max"]].tolist())   # [35.2, 184.0]
    ''')
    yield section("Filtering, sorting and grouping", "filter")
    yield code(FLOWERS + '''
        tall = df[df["height_cm"] > 100]
        print(tall["species"].tolist())                                   # ['shoeblack plant', 'shoeblack plant', 'hibiscus', 'hibiscus']
        print(df[(df["size"] == "medium") & (df["fragrance"] == "mild")].shape[0])   # 3
        print(df.sort_values("height_cm", ascending=False).iloc[0]["species"])       # hibiscus
        print(df.groupby("species")["height_cm"].mean().round(1).to_dict())
        # {'hibiscus': 155.3, 'rose': 57.3, 'shoeblack plant': 111.0}
    ''', check=False)
    yield warn("Combine conditions with `&` (and), `|` (or), `~` (not) — **not** `and`/`or` — and wrap each condition in parentheses.")
    yield section("New columns", "column-insert-right")
    yield code(FLOWERS + '''
        df["height_m"] = (df["height_cm"] / 100).round(2)
        df["is_tall"] = df["height_cm"] > 100
        print(df.loc[1, "height_m"], df.loc[1, "is_tall"])   # 1.47 True
    ''')


G = "Web Scraping"

QUOTES_HTML = '''
        html = """
        <div class="quote">
          <span class="text">“The world as we have created it is a process of our thinking.”</span>
          <small class="author">Albert Einstein</small> <a href="/author/Albert-Einstein">(about)</a>
          <a class="tag" href="/tag/change/">change</a> <a class="tag" href="/tag/thinking/">thinking</a>
        </div>
        <div class="quote">
          <span class="text">“It is our choices that show what we truly are.”</span>
          <small class="author">J.K. Rowling</small> <a href="/author/J-K-Rowling">(about)</a>
          <a class="tag" href="/tag/choices/">choices</a>
        </div>
        """
'''


@topic(G, "scraping-basics", "requests & BeautifulSoup", "world-www")
def _():
    yield lead("Web scraping = download a page's HTML (`requests`), then pick out the data you need (`BeautifulSoup`). It's how you build datasets that don't come as a CSV.")
    yield steps(
        ("Request", "`requests.get(url, headers=…)` downloads the page."),
        ("Parse", "`BeautifulSoup(html, \"html.parser\")` turns HTML text into a searchable tree."),
        ("Extract", "`find` / `find_all` / `select` locate elements; `.text` and `.get(\"href\")` read them."),
        ("Store", "Collect rows in a list, then save with pandas (`to_csv`)."),
    )
    yield section("1. Download the page", "download")
    yield code('''
        import requests

        headers = {"User-Agent": "Mozilla/5.0 (compatible; LearnViaNotesBot/1.0)"}
        r = requests.get("https://quotes.toscrape.com/page/1/", headers=headers, timeout=10)
        print(r.status_code)          # 200 means OK; 404 not found, 403 forbidden, 429 too many requests
        html = r.text                 # decoded text (r.content is the raw bytes)
    ''', run=False)
    yield note("Some sites reject requests without a browser-like `User-Agent` header — that's why the notebook sets one. Always pass a `timeout` so a slow site can't hang your script.")
    yield section("2. Parse and extract", "code")
    yield code(QUOTES_HTML + '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        first = soup.find("div", class_="quote")                      # first match (or None)
        print(first.find("small", class_="author").text)              # Albert Einstein

        for q in soup.find_all("div", class_="quote"):                # every match
            text = q.find("span", class_="text").text.strip("“”")
            tags = [t.text for t in q.find_all("a", class_="tag")]
            print(text[:22], "|", ", ".join(tags))
    ''', check=False)
    yield shell('''
        Albert Einstein
        The world as we have c | change, thinking
        It is our choices that | choices
    ''', caption="Output")
    yield table(
        ["Call", "Returns"],
        ["`soup.find(tag, class_=…)`", "The first matching element, or `None`"],
        ["`soup.find_all(tag, attrs={…})`", "A list of all matches"],
        ["`soup.select(\"div.quote span.text\")`", "Matches for a CSS selector"],
        ["`el.text` / `el.get_text(strip=True)`", "The element's text"],
        ["`el.get(\"href\")` / `el[\"href\"]`", "An attribute (`get` returns `None` if missing)"],
    )
    yield code(QUOTES_HTML + '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        print([a.get("href") for a in soup.select("div.quote > a:not(.tag)")])   # ['/author/Albert-Einstein', '/author/J-K-Rowling']
        print(len(soup.select("a.tag")))                                          # 3
    ''')
    yield section("Parsers", "settings")
    yield table(
        ["Parser", "Install", "Notes"],
        ["`html.parser`", "Built in", "Good default"],
        ["`lxml`", "`pip install lxml`", "Fastest"],
        ["`html5lib`", "`pip install html5lib`", "Most forgiving with broken HTML, slowest"],
    )
    yield section("Scrape responsibly", "shield-check")
    yield dodont(
        "Check the site's terms and `robots.txt`, identify yourself in the User-Agent, pause between requests (`time.sleep(1)`), and prefer an official API when there is one.",
        "Hammering a site with rapid requests, scraping personal data, or ignoring a site's terms — it can get you blocked or break the law.",
    )


@topic(G, "scraping-projects", "Scraping Multiple Pages", "files")
def _():
    yield lead("Real datasets span many pages. Loop over page URLs, reuse the same extraction code, collect rows, and save them as a table — the notebook's quotes and books scrapers.")
    yield section("Page URLs", "link")
    yield code('''
        urls = [f"https://quotes.toscrape.com/page/{page}/" for page in range(1, 6)]
        print(urls[0])       # https://quotes.toscrape.com/page/1/
        print(len(urls))     # 5
    ''')
    yield section("Extract → rows → DataFrame", "table")
    yield code(QUOTES_HTML + '''
        import pandas as pd
        from bs4 import BeautifulSoup

        def parse_quotes(html):
            rows = []
            for q in BeautifulSoup(html, "html.parser").find_all("div", class_="quote"):
                rows.append({
                    "quote": q.find("span", class_="text").text[1:-1],       # strip the curly quotes
                    "author": q.find("small", class_="author").text,
                    "details": q.find("a").get("href"),
                    "tags": ",".join(t.text for t in q.find_all("a", class_="tag")),
                })
            return rows

        pages = [html, html]                        # stand-ins for page 1 and page 2
        rows = [row for page in pages for row in parse_quotes(page)]
        df = pd.DataFrame(rows)
        print(df.shape, df.columns.tolist())        # (4, 4) ['quote', 'author', 'details', 'tags']
        print(df.loc[0, "tags"])                    # change,thinking
        df.to_csv("quotes.csv", index=False)
    ''')
    yield section("The full live scraper", "world")
    yield code('''
        import time
        import requests
        import pandas as pd
        from tqdm import tqdm                              # progress bar: pip install tqdm

        rows = []
        for page in tqdm(range(1, 11)):
            r = requests.get(f"https://quotes.toscrape.com/page/{page}/", timeout=10)
            if r.status_code != 200:
                break                                     # no more pages
            rows += parse_quotes(r.text)
            time.sleep(0.5)                               # be polite
        pd.DataFrame(rows).to_csv("quotes.csv", index=False)
    ''', run=False)
    yield section("Books: fields from attributes", "books")
    yield code('''
        from bs4 import BeautifulSoup
        html = """
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3"><article class="product_pod">
          <a href="a-light-in-the-attic_1000/index.html"><img src="../media/cache/2c/da/cover.jpg"></a>
          <p class="star-rating Three"></p>
          <h3><a href="a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
          <p class="price_color">£51.77</p> <p class="instock availability"> In stock </p>
        </article></li>
        """
        book = BeautifulSoup(html, "html.parser").find("article", class_="product_pod")
        title = book.h3.a["title"]                                   # the full title lives in an attribute
        rating = book.find("p", class_="star-rating")["class"][-1]   # the rating is a CSS class
        price = float(book.find("p", class_="price_color").text.lstrip("£"))
        stock = book.find("p", class_="instock").text.strip()
        link = "https://books.toscrape.com/catalogue/" + book.h3.a["href"]
        print(title, rating, price, stock)     # A Light in the Attic Three 51.77 In stock
        print(link)                            # https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
    ''')
    yield note("Visible text is often shortened (“A Light in the ...”); the complete value sits in an attribute (`title`, `alt`, `data-*`). Inspect the page (right-click → *Inspect*) before writing selectors.")
    yield section("Joining list pages with detail pages", "arrows-join")
    yield p("The notebook scrapes 50 list pages for title/price/link, then visits each book's own page for extra fields (UPC, tax, reviews) and joins the two tables. Join on a shared key, not on row position:")
    yield code('''
        import pandas as pd
        books = pd.DataFrame({"link": ["b1", "b2"], "title": ["Attic", "Velvet"]})
        details = pd.DataFrame({"link": ["b2", "b1"], "upc": ["u-2", "u-1"]})
        print(books.merge(details, on="link").to_dict("records"))
        # [{'link': 'b1', 'title': 'Attic', 'upc': 'u-1'}, {'link': 'b2', 'title': 'Velvet', 'upc': 'u-2'}]
    ''', check=False)
    yield warn("The notebook builds the final table with `df['UPC'] = df_2['UPC']` next to `df_1['Title']` — that only lines up if both lists are in exactly the same order and length. A failed detail page (the notebook's 404) silently shifts every row. Use `merge` on the link.", "Correction")


@topic(G, "selenium", "Dynamic Pages with Selenium", "browser")
def _():
    yield lead("Some pages build their content with JavaScript after loading — `requests` only sees the empty shell. Selenium drives a real browser, so you scrape what a user actually sees.")
    yield cards(
        ("requests + BeautifulSoup", "Fast and light. Works when the data is in the HTML the server sends.", "bolt"),
        ("Selenium", "Slower, needs a browser. Needed for infinite scroll, clicks, logins and JavaScript-rendered content (YouTube, dashboards).", "browser"),
    )
    yield section("Setup (Selenium 4.6+)", "settings")
    yield shell('''
        pip install selenium beautifulsoup4
    ''')
    yield note("Selenium 4.6 and later include **Selenium Manager**, which downloads a matching driver automatically. You no longer install `chromedriver` by hand.")
    yield warn("Most of the notebook's Selenium cells failed with *“This version of ChromeDriver only supports Chrome version 114 — current browser version is 127”*. That's the classic manual-driver problem: the driver and the browser must match. Letting Selenium Manager handle it (just `webdriver.Chrome()`) avoids it.", "What went wrong in the notebook")
    yield section("Scrolling a dynamic page", "arrow-down")
    yield code('''
        import time
        from bs4 import BeautifulSoup
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new")        # no visible window
        driver = webdriver.Chrome(options=options)    # Selenium Manager finds a matching driver
        try:
            driver.get("https://quotes.toscrape.com/scroll")
            last = driver.execute_script("return document.body.scrollHeight")
            while True:                               # scroll until the page stops growing
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
                height = driver.execute_script("return document.body.scrollHeight")
                if height == last:
                    break
                last = height
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print(len(soup.find_all("div", class_="quote")))
        finally:
            driver.quit()                             # always close the browser
    ''', run=False)
    yield section("Waiting for elements", "clock")
    yield code('''
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # Better than time.sleep: wait up to 10 s, continue as soon as the element appears.
        first = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote span.text"))
        )
        print(first.text)
    ''', run=False)
    yield table(
        ["Selenium", "Does"],
        ["`driver.get(url)`", "Open a page"],
        ["`driver.find_element(By.CSS_SELECTOR, …)`", "Find one element (`find_elements` for all)"],
        ["`element.click()` / `.send_keys(\"text\")`", "Interact like a user"],
        ["`driver.execute_script(js)`", "Run JavaScript (e.g. scroll)"],
        ["`driver.page_source`", "The current HTML — hand it to BeautifulSoup"],
        ["`driver.quit()`", "Close the browser (use `try/finally`)"],
    )
    yield note("Big sites like YouTube change their HTML often and forbid scraping in their terms; their official APIs (e.g. the YouTube Data API) are the reliable, allowed route.")
