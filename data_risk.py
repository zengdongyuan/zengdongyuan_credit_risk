# -*- coding: utf-8 -*-


#%%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVC
import scipy as sp
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import roc_curve, auc

df = pd.read_csv("credit_risk_dataset.csv")

df.head()

df.info()

df.shape

df.isnull().sum()

df.dropna(axis=0,inplace=True)

df.shape

df.describe()

df = df[df['person_age'] <= 90]
df = df[df['person_emp_length'] <= 60]

perc_default = df.loan_status.sum() / len(df.loan_status)
print(f'The percentage of defaulters in the data is {perc_default*100} %')
df['loan_status'].value_counts().plot(kind='pie',explode=[0.1,0],autopct="%1.1f%%")

continuous_variables = ['person_age','person_income', 'person_emp_length', 'loan_amnt', 'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length']

#bar chart of numerical feature
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig.subplots_adjust(hspace=0.5, wspace=0.5)

for i, var in enumerate(continuous_variables):
    row = i // 4
    col = i % 4
    ax = axes[row, col]

    ax.hist(df[var], bins=50, color='skyblue', edgecolor='black')
    ax.set_xlabel(var.replace('_', ' ').title())
    ax.set_ylabel('Frequency')
    ax.set_title(f'Distribution of {var.replace("_", " ").title()}')

plt.show()

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# pie chart of categorical feature
columns_to_plot = ['person_home_ownership', 'loan_intent', 'cb_person_default_on_file', 'loan_grade']
for i, column_name in enumerate(columns_to_plot):
    level_counts = df[column_name].value_counts()
    axs[i//2, i%2].pie(level_counts, labels=level_counts.index, autopct='%1.1f%%', startangle=140)
    axs[i//2, i%2].set_title(f'{column_name.replace("_", " ").title()} Distribution')
    axs[i//2, i%2].axis('equal')

plt.tight_layout()
plt.show()

#%%

#correlation between differnet features
fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(df.corr(), vmax =.8, square = True, annot = True,cmap='Greens' )
plt.title('Confusion Matrix',fontsize=15);

sns.pairplot(df,hue="loan_status")

df['loan_to_emp_length_ratio'] =  df['person_emp_length']/ df['loan_amnt']

df['int_rate_to_loan_amt_ratio'] = df['loan_int_rate'] / df['loan_amnt']

df_categorized=pd.get_dummies(df,columns=["person_home_ownership","loan_intent","loan_grade","cb_person_default_on_file"])

df_categorized.columns

#data spliting
y=df_categorized.loan_status
X = df_categorized.drop("loan_status",axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y,random_state=126)

#model training
clf = SVC(class_weight="balanced",kernel="rbf")
param_distributions = {"C": sp.stats.uniform(0.1, 10), "gamma": sp.stats.uniform(0.01, 0.1)}
random_search = RandomizedSearchCV(clf, param_distributions=param_distributions, n_iter=10, cv=3,
                                                           scoring="balanced_accuracy", n_jobs=-1)
random_search.fit(X_train, y_train)

model = random_search.best_estimator_
print("Best parameter selection is: %s, Best score is: %0.2f" % (random_search.best_params_, random_search.best_score_))

y_pred = model.predict(X_test)

#perfomance of model
accuracy = metrics.accuracy_score(y_test, y_pred)
print("Accuracy: ", accuracy)

cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
classification_report = metrics.classification_report(y_test, y_pred)
print("confusion matrix")
display(pd.DataFrame(cnf_matrix))#%%

fpr, tpr, thresholds = roc_curve(y_test, y_pred)
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure()
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC)')
plt.legend(loc="lower right")
plt.show()
