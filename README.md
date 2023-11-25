# OpeningOracle

## Wikipedia Scraping 

### Description of methods

#### Naming conventions and forming URLs: 

Wikipedia has a standard for how the URLs for chess openings are constructed; in relation to how Chess.com's openings are named, i.e. to get a Wikipedia URL for a particular opening given the name from Chess.com, we follow the following rules: 

- Defense -> Defence 

- " " -> "_"

- Accented letters do not exist (NOTE: Not an issue for ASCII based URLs)

- Apostrophes ("'") are replaced with "%27"

- Exclude variations; i.e., anything after a ":" is truncated

#### Constructing URLs from the above results

After standardizing the names, the format for Wikipedia URLs for pages about a specific opening is: 

    http://en.wikipedia.org/wiki/[opening_name]

    Ex. http://en.wikipedia.org/wiki/Sicilian_Defence

Using these results, we can get the wikipedia pages for all the openings gathered from Chess.com (32 total), including their variations *(to be completed later).*