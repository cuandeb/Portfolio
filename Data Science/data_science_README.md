# Data Science

These two projects were part of a course I took during my MSc. called "Data Science in Python". Having
used Python for data analysis and simulation for a number of years this was my first foray into using
Python for data science and it is a topic I found really stimulating and enjoyable. 

The two projects are described below and I received an A+ grade with full marks from the School of 
Computer Science for both. 

## Web APIs and Data Analysis

This project consisted of two main parts. The goal was to interface with a web API of our choosing to 
request data that could then be analysed from a data science standpoint. The topic I chose to approach 
was film and box office details as I thought it would be a step away from the typical physics based 
analysis I was familiar with.

The first notebook *Film Data Extraction* comprises of functions used to interface and request film 
data from "The Movie Database" API. This required elements of web scraping to extract the names
of hundreds of films from IMDB which could then be used to request data from the API. This data
once received was stored in JSON format. These JSON files are the repository as a zip file in 
case an example of the data is needed. 

The second notebook, *Film Data Analysis* is focused primarily on loading these JSON files into 
dataframes and performing statistical analysis such as regression models, heatmaps, correlation plots. 
Example data included box office performance, budget, genre, production companies, language.  
The first section of the notebook deals with data cleaning and organisation to prepare the data 
for analysis. The second section deals with the analysis itself and makes extensive use of 
Python packages such as Pandas, Matplotlib, Numpy, and Stats. 

## Web Scraping and Text Classification

This project involved scraping thousands of news articles from a website and sorting them by category. 
These categories included UK News, US News, Film, Lifestyle etc. The news articles were stored
as JSON items with a headline, category, and snipped of text from the article. 

From these compiled items, 3 categories were chosen and were used to train a number of machine
learning text classification models. The main model analysed was the k-nearest neighbour model but
a comparison was made between various other ML models for text classification. By splitting the
articles into training and test sets the perfomance of each model was analysed and tested on 
their ability to identify the category of a set of articles. 