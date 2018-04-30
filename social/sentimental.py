from sklearn.externals import joblib
import numpy as np

forest = joblib.load('finalized_model.sav')
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(analyzer="word", \
                             tokenizer=None, \
                             preprocessor=None, \
                             stop_words=None, \
                             max_features=5000)
def sentimnet(comment_tex):
    comment = comment_tex
    clean_train_reviews = joblib.load('fit_transform.sav')
    train_data_features = vectorizer.fit_transform(clean_train_reviews)

    np.asarray(train_data_features)

    clean_test_reviews = []
    from KaggleWord2VecUtility import KaggleWord2VecUtility

    for i in xrange(0, len(comment)):
        clean_test_reviews.append(" ".join(KaggleWord2VecUtility.review_to_wordlist(comment[i], True)))

    test_data_features = vectorizer.transform(clean_test_reviews)
    np.asarray(test_data_features)

    sentiment = forest.predict(test_data_features)
    return sentiment


