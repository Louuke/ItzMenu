import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from sklearn.datasets import load_iris
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.naive_bayes import GaussianNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier

from itzmenu_client.client import ItzMenuClient
from itzmenu_api.persistence.schemas import WeekMenuRead
from itzmenu_api.persistence.enums import DietType

client = ItzMenuClient(host='https://itz-dev.jannsen.org')
lst = client.get_menu_by_timestamp_range()
lst: list[WeekMenuRead]

rows = []
for menu in lst:
    for day in menu.menus:
        for category in day.categories:
            for meal in category.meals:
                row = {t.name: 0 for t in DietType.values()}
                row |= {t.name: 1 for t in meal.curated_diet_type}
                name_col = {'name': meal.name}
                name_col |= row
                rows.append(name_col)
df = pd.DataFrame(rows)
df['MIXED'] = (df['MIXED'] | df['PESCETARIANISM']).astype(int)
df.drop(columns=['PESCETARIANISM'], inplace=True)
df.drop_duplicates(inplace=True)

# Tokenize the meal names
stop_words = stopwords.words('german')
df['name'] = df['name'].apply(lambda x: word_tokenize(x))
# Remove stop words
df['name'] = df['name'].apply(lambda x: [word for word in x if word.lower() not in stop_words + ['oder']])
df['name'] = df['name'].apply(lambda x: ' '.join(x))

# Remove punctuation
df['name'] = df['name'].str.replace(r'\((\s?[A-Z]\s?(,\s)?)+\)', '', regex=True)
df['name'] = df['name'].str.replace(r'[?|!|\'|"|#|\-]', '', regex=True)
df['name'] = df['name'].str.replace(r'\s/\s', ' oder ', regex=True)
df['name'] = df['name'].str.replace(r'[.|,|)|(|\|/]', ' ', regex=True)
df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)

# Remove single characters
df['name'] = df['name'].apply(lambda x: ' '.join([word for word in x.split(' ') if len(word) > 1]))

# Stem the words
stemmer = SnowballStemmer('german', ignore_stopwords=True)
df['name'] = df['name'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))

x_train, x_test, y_train, y_test = train_test_split(df['name'], df.drop(columns=['name', 'UNKNOWN']), test_size=0.2,
                                                    shuffle=True)
vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, 3), norm='l2')
vectorizer.fit(x_train)

x_train = vectorizer.transform(x_train)
x_test = vectorizer.transform(x_test)

svm = LinearSVC(random_state=42)
classifier = MultiOutputClassifier(svm, n_jobs=-1)
classifier.fit(x_train, y_train)
predictions = classifier.predict(x_test)

print('AUC score:', roc_auc_score(y_test, predictions))
pass
