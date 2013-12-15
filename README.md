# Ra ebook scraper

A python scraper for [Ra](http://qntm.org/ra).

Run as:

```
$ ./scrape.py
$ ./build.py
```

A `Ra.epub` file will be created in the current directory.

Also a `scrape.json` file will be created. This will be reused if `scrape.py` is rerun to avoid redownloading everything.

`kindlegen` or similar may be used to create a mobi file if desired.

## Dependencies

Known dependencies are `requests`, `lxml`, `epubbuilder`, and `genshi`. If someone would submit a `requirements.txt` via a pull request it would be appreciated.