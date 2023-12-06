# OpeningOracle

## Description

OpeningOracle is a solution for chess players to find statistically successful openings to play based on their own description of how they like to play. Both experienced and inexperienced players can benefit from this; experienced players who know their preferred playstyle can find new openings they may not have known about before, and new players who are not yet sure how they like to play can find openings based on different playstyles. 

The primary goal of OpeningOracle, and what sets it apart from other applications, is that users can arbitrarily describe their playstyle. There are current applications that provide opening recommendations based on pre-set parameters, like the user's self-reported skill level, some keywords to choose from, and/or a color to play with. At the time of writing, we did not come across any solutions that allow the user to arbitrarily define their own playstyle, and very few that operate independently of the user's reported playstyle. 

## Data Sources 

To collect data, we used the following sources: 

- [Wikipedia](http://wikipedia.com) to scrape descriptions of chess openings.
- [Chess.com](http://chess.com/openings) as a starting point to get opening ECO codes, names, and descriptions.
- [Lichess Dataset from Kaggle](http://www.kaggle.com/datasets/datasnaek/chess) as one source of opening success rates, and to get the ECOs/names of openings not on [Chess.com](http://chess.com/openings). 
- [High Elo Chess Games Dataset from Kaggle](http://www.kaggle.com/datasets/arashnic/chess-opening-dataset) to get the color/side for each opening (i.e. which color plays, responds to, or initiates an opening), and as a second source of opening success rates.

Detailed descriptions of our [methods](##methods) for [data collection](###data-collection), [aggregation](###data-aggregation-&-analysis), and [analysis](###data-aggregation-&-analysis) can be found in sections further down.

## Methods

We used a variety of methods to collect, aggregate, and standardize data from [different sources](##data-sources). 

### Data Collection

#### Chess.com Openings

As a starting point, we used [chess.com](http://chess.com) to gather a preliminary list of chess openings and short descriptions for each. To do this, we used the base URL (as a GET request) 

    "https://www.chess.com/callback/eco/advanced-search?keyword=&useFavorites=false&page=" 

We were able to find this API endpoint by examining the network traffic when visiting the site via the (normal) url "[chess.com/openings](http://chess.com/openings). With this URL, we added a number on the end, starting with 1 and ending with 5, to get the corresponding pages from [chess.com](http://chess.com).

Since each page is in a standard format, after getting the raw html content from each page, we simply pulled the elements tagged with the "post-view-content" class. Then, we parsed these elements and pulled the opening's name and URL to the description. After that, it is trivial to create an index from the content.

#### Kaggle Datasets 

We discovered two public datasets on Kaggle that we used to gather the success rates for each opening (by ECO), and to get the names of more openings to [scrape from Wikipedia](####wikipedia-scraping). 

##### 1. Lichess Dataset 

The [Lichess dataset](http://www.kaggle.com/datasets/datasnaek/chess) contains data on more than 20,000 unique chess games. Using this dataset, we found openings not available on chess.com and scraped these descriptions on Wikipedia. Additionally, we calculated the success rate for each opening in the dataset, identified by the ECO. 

##### 2. High Elo Openings Dataset 

[The high elo chess games dataset](http://www.kaggle.com/datasets/arashnic/chess-opening-dataset) contains 1755 unique openings (including variations). With this dataset, we were able to narrow down the success rates of different variations of a particular opening to provide the user more nuanced responses.

Notably, we were not able to scrape the descriptions of individual variations for an opening due to restraints on the format and availability of these specific descriptions on Wikipedia. Many of these variations are available on the wikipedia page for the parent opening, but do not have a page for themselves. Additionally, many variations share ECO codes. Thus, we identified openings by ECO (allowing some overlap) and used the same description as the parent opening for a particular variation. For example, the "King's Pawn Opening, Rukertort Variation" uses the same description as the "King's Pawn Opening," but importantly, the two have different success rates *and* are played by different colors. Using the different success rates and colors, we can calculate which variation is more successful for a particular color. This is where the separation comes from in the responses containing variations, not necessarily solely from the description of the openings. 

#### Wikipedia Scraping

To collect data from Wikipedia, we created wikipedia URLs for each opening we got from previous sources (the two datasets and chess.com). The rules for constructing the wikipedia URL for a chess opening are as follows: 

- Defense -> Defence 

- " " -> "_"

- Accented letters do not exist (NOTE: Not an issue for ASCII based URLs)

- Apostrophes ("'") are replaced with "%27"

- Exclude variations; i.e., truncate anything after a ":" or ","

After constructing the wikipedia URL for each opening, we scraped the content of that page and added these descriptions to our index. Additionally, we saved the raw content for each so we could process them later (without having to scrape the pages again). 

Wikipedia has variations on the format of particular pages, which becomes slightly problematic when trying to differentiate between an opening and its variations. Thus, we used the methods described in the [above section](#####2.-high-elo-openings-dataset) to account for this nuance. 

### Data Aggregation & Analysis 


#### Naming conventions and forming URLs: 

Wikipedia has a standard for how the URLs for chess openings are constructed; in relation to how Chess.com's openings are named, i.e. to get a Wikipedia URL for a particular opening given the name from Chess.com, we follow the following rules: 



#### Constructing URLs from the above results

After standardizing the names, the format for Wikipedia URLs for pages about a specific opening is: 

    http://en.wikipedia.org/wiki/[opening_name]

    Ex. http://en.wikipedia.org/wiki/Sicilian_Defence

Using these results, we can get the wikipedia pages for all the openings gathered from Chess.com (32 total), including their variations *(to be completed later).*