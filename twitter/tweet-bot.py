from twitter import *


auth = OAuth(
    consumer_key='2EKvFT82jxjvm30Mbc78jQ',
    consumer_secret='knomKYbkegpLMmGBY1fY77Qfr5c2cas9102eIYkejw',
    token='2363333767-H5oabPblH1gTJvpSXLkSSnOl5OXpkImY0B1Xbiw',
    token_secret='qK0CoZ2doaEHm2hgUMExLRiymUFY6KfuKZXSa5qOCH6iA'
)

twitter = Twitter(auth=auth)

twitter.statuses.update(status='Behold my awesomness')
