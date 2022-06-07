# web-lang-analysis
This is the code for my bachelor's degree thesis. I am analysing the change in Estonian internet language based on Estonian tweets.
Due to Twitter's Developer Policy, I cannot share the Twitter dataset. There are approximately 1.6 million Estonian tweets in the dataset ranging from year 2009 to 2018.

For tagging the web language attributes, I wrote an EstNLTK 1.6 tagger based on this retagger: https://github.com/estnltk/ettenten-experiments/tree/master/weblang_detection. I didn't write the retagger.

For performance reasons 'use_unknown_words' and 'use_missing_commas' were not implemented for this version.
'use_unknown_words' and 'use_missing_commas' attributes have to be set to 'False' when creating the tagger.

The tagger can detect words containing foreign z-letters as well. For that, the user has to provide a list of z-letter words that the tagger should not tag (Estonian words containing the letter 'z'). 
The name of the user dictionary file has to be 'z_words.txt' and each line has to consist of one word.
An empty 'z_words.txt' file is included.

A tutorial for WebLangTagger is included ('weblangtagger_tutorial.ipynb') and a notebook 'andmetest_1.ipynb' from my thesis is included as well, where an overview of tweeting dynamics is made.
Other notebooks from my thesis aren't included with this repository (tagging the web language attributes, doing a morphological analysis and tagging None-words, plotting the findings).
