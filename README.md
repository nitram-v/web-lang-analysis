# web-lang-analysis
This is the code for my bachelor's degree thesis. I am analysing the change in Estonian internet language based on Estonian tweets.
Due to Twitter's Developer Policy, I cannot share the Twitter dataset. There are approximately 1.6 million Estonian tweets in the dataset ranging from year 2009 to 2018.

For tagging the web language attributes, I wrote an EstNLTK 1.6 tagger based on this retagger: https://github.com/estnltk/ettenten-experiments/tree/master/weblang_detection. I didn't write the retagger.

The tagger can detect words containing foreign z-letters as well. For that, the user has to provide a list of z-letter words that the tagger should not tag (Estonian words containing the letter 'z').
