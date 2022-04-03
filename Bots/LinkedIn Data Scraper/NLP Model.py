import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import collections
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from wordcloud import WordCloud

import matplotlib.pyplot as plt
from textblob import Word
from textblob import TextBlob

# Import data from linkedin_data.db
import sqlite3

# Create connection
connection = sqlite3.connect("/data/linkedin_data.db3")
# Load data as data frame
job_details = pd.read_sql_query("SELECT position, company, location, details from positions", connection)

# Verify that result of SQL query is stored in the dataframe
print(job_details.head())
connection.close()

# Clean Data - Job Titles
counter = collections.Counter(job_details['position'])
print(counter)
print(counter.most_common(5))

# We understand the most common job titles in the data set are:
# Data Scientist, Senior Data Scientist, Data Scientist I, Machine Learning Engineer, Data Scientist II

# Let's group job titles by keyword - "Data Scientist" or "Machine Learning"
job_details['position_group'] = np.where(job_details.position.str.contains("Data Scientist"), "Data Scientist",
                                         np.where(job_details.position.str.contains("Machine Learning"),
                                                  "Machine Learning Engineer", "Other Analytics"))

counter = collections.Counter(job_details["position_group"])
print(counter)

# Plot the Results
plt.figure()
job_details.position_group.hist()  # improve visualizations
# plt.show()

# Let's group job titles by experience - i.e.(Senior v. Entry Level)
job_details['experience'] = np.where(job_details.position.str.contains("Senior"), "Senior",
                                     np.where(job_details.position.str.contains("Sr."), "Senior",
                                              np.where(job_details.position.str.contains("Director"), "Senior",
                                                       "Entry Level")))
counter = collections.Counter(job_details["experience"])
print(counter)

# Plot the Results
plt.figure()
job_details.experience.hist()  # improve visualizations
# plt.show()

# Preprocess Text Data
# Lower case
job_details['details'] = job_details['details'].apply(lambda x: " ".join(x.lower() for x in x.split()))
# remove tabulation and punctuation
job_details['details'] = job_details['details'].str.replace('[^\w\s]', ' ')
# digits
job_details['details'] = job_details['details'].str.replace('\d+', '')

# remove stop words
stop = stopwords.words('english')
job_details['details'] = job_details['details'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))

# lemmatization
job_details['details'] = job_details['details'].apply(
    lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

print("Preprocessed data: \n")
print(job_details.head())

other_stop_words = ['junior', 'senior', 'experience', 'etc', 'job', 'work', 'company', 'technique',
                    'candidate', 'skill', 'skills', 'language', 'menu', 'inc', 'new', 'plus', 'years',
                    'technology', 'organization', 'ceo', 'cto', 'account', 'manager', 'data', 'scientist', 'mobile',
                    'developer', 'product', 'revenue', 'strong', 'business', 'team', 'science', 'e', 'sexual',
                    'orientation', 'equal', 'opportunity']

job_details['details'] = job_details['details'].apply(
    lambda x: " ".join(x for x in x.split() if x not in other_stop_words))

# Visualize the Data
total_words = job_details.groupby(['position_group']).sum().reset_index()
total_words = total_words[["position_group", "details"]]
print("Aggregated job descriptions: \n")
print(total_words)

# Word Clouds
# Visualize data
jobs_list = total_words.position_group.unique().tolist()
for job in jobs_list:
    # Start with one review:
    text = total_words[total_words.position_group == job].iloc[0].details
    # Create and generate a word cloud image:
    wordcloud = WordCloud().generate(text)
    print("\n***", job, "***\n")
    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.show()

# Converting text to features
vectorizer = TfidfVectorizer()
# Tokenize and build vocabulary
top_5 = ('Data Scientist', 'Senior Data Scientist', 'Data Scientist I', 'Machine Learning Engineer',
         'Data Scientist II')  # try to pull value direct from counter, so it always pulls in top 5 job titles

# selecting rows based on condition
top_science = job_details[job_details['position'].isin(top_5)]

X = vectorizer.fit_transform(top_science.details)
y = top_science.position

# split data into 80% training and 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=109)
print("train data shape: ", X_train.shape)
print("test data shape: ", X_test.shape)

# Fit model
clf = MultinomialNB()
clf.fit(X_train, y_train)
# Predict
y_predicted = clf.predict(X_test)

y_train.hist()
y_test.hist()

# evaluate the predictions
print("Accuracy score is: ", accuracy_score(y_test, y_predicted))
print("Classes: (to help read Confusion Matrix)\n", clf.classes_)
print("Confusion Matrix: ")

print(confusion_matrix(y_test, y_predicted))
print("Classification Report: ")
print(classification_report(y_test, y_predicted))

print(clf.coef_)
print(clf.coef_.shape)

technical_skills = ['python', 'c', 'r', 'c++', 'java', 'hadoop', 'scala', 'flask', 'pandas', 'spark', 'scikit-learn',
                    'numpy', 'php', 'sql', 'mysql', 'css', 'mongdb', 'nltk', 'fastai', 'keras', 'pytorch', 'tensorflow',
                    'linux', 'Ruby', 'JavaScript', 'django', 'react', 'reactjs', 'ai', 'ui', 'tableau']
feature_array = vectorizer.get_feature_names()
# number of overall model features
features_numbers = len(feature_array)
# max sorted features number
n_max = int(features_numbers * 0.1)

# initialize output dataframe
output = pd.DataFrame()
for i in range(0, len(clf.classes_)):
    print("\n****", clf.classes_[i], "****\n")
    class_prob_indices_sorted = clf.feature_log_prob_[i, :].argsort()[::-1]
    raw_skills = np.take(feature_array, class_prob_indices_sorted[:n_max])
    print("list of unprocessed skills :")
    print(raw_skills)

    # Extract technical skills
    top_technical_skills = list(set(technical_skills).intersection(raw_skills))[:6]
    # print("Top technical skills",top_technical_skills)

    # Extract adjectives

    # Delete technical skills from raw skills list
    # At this steps, raw skills list doesnt contain the technical skills
    # raw_skills = [x for x in raw_skills if x not in top_technical_skills]
    # raw_skills = list(set(raw_skills) - set(top_technical_skills))

    # transform list to string
    txt = " ".join(raw_skills)
    blob = TextBlob(txt)
    # top 6 adjective
    top_adjectives = [w for (w, pos) in TextBlob(txt).pos_tags if pos.startswith("JJ")][:6]
    # print("Top 6 adjectives: ",top_adjectives)

    output = output.append({'job_title': clf.classes_[i],
                            'technical_skills': top_technical_skills,
                            'soft_skills': top_adjectives},
                           ignore_index=True)

print(output)
output.to_clipboard()
