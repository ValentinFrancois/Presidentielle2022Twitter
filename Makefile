ISORT_ARGS = \
	--project md_commons \
	--known-local-folder $(PROJECT)

isort:
	isort $(ISORT_ARGS) tweet_postprocesser tweet_scrapper main.py