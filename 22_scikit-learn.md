# 22 - Scikit-learn

<!-- nav:start -->
**Previous:** [21 - Seaborn](21_seaborn.md) | **Index:** [All guides](README.md) | **Next:** [23 - PyTorch](23_pytorch.md)
<!-- nav:end -->

Quick reference for machine learning with scikit-learn: preprocessing, models, evaluation, tuning and saving.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Scikit-learn?

Scikit-learn (`sklearn`) is the standard Python library for **classical machine learning** on tabular data. Machine learning means a program learns patterns from example data instead of following hand-written rules: show it past customers with a "churned yes / no" label, and it learns to predict churn for new customers. Scikit-learn provides ready-made algorithms (models) plus everything around them: data preprocessing, splitting, evaluation, tuning and pipelines, all with the same simple `fit` / `predict` interface.

### Why use it?

- **Consistent API**: every model uses `fit`, `predict`, `score`; switching models is one line.
- **Complete toolkit**: preprocessing, models, metrics, cross-validation and tuning in one library.
- **Pipelines** prevent common mistakes like data leakage and make deployment easy.
- **Well documented and tested**; the reference in industry and teaching.
- **Right tool for tabular data**: often beats deep learning on spreadsheets and database tables.

### Types of machine learning

| Type | Goal | Example | Models |
|---|---|---|---|
| Regression (supervised) | Predict a number | House price | LinearRegression, RandomForestRegressor |
| Classification (supervised) | Predict a category | Spam or not | LogisticRegression, RandomForestClassifier |
| Clustering (unsupervised) | Find groups without labels | Customer segments | KMeans, DBSCAN |
| Dimensionality reduction | Fewer columns, keep information | Visualise 50 features in 2D | PCA |

### Key terms

| Term | Meaning |
|---|---|
| Features (`X`) | Input columns the model learns from |
| Target (`y`) | The column to predict |
| Training / test set | Data to learn from / data held back to check performance |
| Model / estimator | An algorithm object with `fit` and `predict` |
| Hyperparameter | Setting you choose before training (`max_depth`) |
| Overfitting | Model memorises training data and fails on new data |
| Data leakage | Information from the test data or the answer sneaks into training |
| Pipeline | Preprocessing steps + model as one object |

**Where it fits:** uses data prepared with [17 - Pandas](17_pandas.md); serve the trained model with [39 - FastAPI](39_fastapi.md). Deep learning and pretrained models: [23 - PyTorch](23_pytorch.md), [24 - Hugging Face](24_hugging-face.md); text features via [29 - Embeddings](29_embeddings-vector-db.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| scikit-learn documentation | https://scikit-learn.org/stable/ |
| User guide | https://scikit-learn.org/stable/user_guide.html |
| API reference | https://scikit-learn.org/stable/api/index.html |
| Choosing the right estimator (map) | https://scikit-learn.org/stable/machine_learning_map.html |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and Import](#1-install-and-import)
2. [The ML Workflow](#2-the-ml-workflow)
3. [The Estimator API](#3-the-estimator-api)
4. [Load Data (X and y)](#4-load-data-x-and-y)
5. [Train / Test Split](#5-train--test-split)
6. [Scaling Numeric Features](#6-scaling-numeric-features)
7. [Encoding Categorical Features](#7-encoding-categorical-features)
8. [Missing Values](#8-missing-values)
9. [ColumnTransformer](#9-columntransformer)
10. [Pipelines](#10-pipelines)
11. [Regression Models](#11-regression-models)
12. [Classification Models](#12-classification-models)
13. [Clustering and Dimensionality Reduction](#13-clustering-and-dimensionality-reduction)
14. [Regression Metrics](#14-regression-metrics)
15. [Classification Metrics](#15-classification-metrics)
16. [Cross-Validation](#16-cross-validation)
17. [Hyperparameter Tuning](#17-hyperparameter-tuning)
18. [Feature Importance](#18-feature-importance)
19. [Imbalanced Classes](#19-imbalanced-classes)
20. [Save and Load a Model](#20-save-and-load-a-model)
21. [Full Example](#21-full-example)
22. [Which Model to Use](#22-which-model-to-use)
23. [Troubleshooting](#23-troubleshooting)
24. [Try It](#24-try-it)

---

## 0. Flags and Parameters

> The meaning of the parameters that appear again and again in scikit-learn. Parameters are set when you create an object (`Model(param=value)`), before `fit`. Use this when you see `RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42)` and want to know what each argument does.

```text
RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1)
|                      |                 |            |                |
|                      |                 |            |                +-- use all CPU cores
|                      |                 |            +------------------- fixed seed: same result every run
|                      |                 +-------------------------------- each tree at most 8 levels deep
|                      +-------------------------------------------------- number of trees
+------------------------------------------------------------------------- the model class
```

These settings are called **hyperparameters**: you choose them; the model learns everything else from data. See defaults with `help(RandomForestClassifier)` or `model.get_params()`.

| Parameter | Used in | Meaning | Example |
|---|---|---|---|
| `test_size` | `train_test_split` | Share of rows kept for testing | `test_size=0.2` |
| `random_state` | almost everything | Seed for randomness: same number = same result | `random_state=42` |
| `stratify` | `train_test_split` | Keep class proportions equal in train and test | `stratify=y` |
| `shuffle` | splits, `KFold` | Shuffle rows before splitting (`False` for time series) | `shuffle=False` |
| `n_jobs` | forests, CV, search | CPU cores to use; `-1` = all | `n_jobs=-1` |
| `cv` | `cross_val_score`, search | Number of folds, or a splitter object | `cv=5` |
| `scoring` | CV, search | Metric to optimise: `"accuracy"`, `"f1"`, `"roc_auc"`, `"r2"`, `"neg_root_mean_squared_error"` | `scoring="f1"` |
| `n_estimators` | forests, boosting | Number of trees | `n_estimators=300` |
| `max_depth` | trees, forests | Max tree depth; lower = simpler, less overfitting | `max_depth=8` |
| `min_samples_leaf` | trees, forests | Minimum rows in a leaf; higher = smoother | `min_samples_leaf=5` |
| `learning_rate` | boosting | Step size; lower = slower but often better | `learning_rate=0.05` |
| `C` | `LogisticRegression`, `SVC` | Inverse regularisation: smaller = simpler model | `C=1.0` |
| `alpha` | `Ridge`, `Lasso` | Regularisation strength: larger = simpler model | `alpha=1.0` |
| `max_iter` | linear models, MLP | Max training iterations (raise if "did not converge") | `max_iter=1000` |
| `class_weight` | classifiers | `"balanced"` = give rare classes more weight | `class_weight="balanced"` |
| `n_neighbors` | `KNeighbors*` | Number of neighbours used | `n_neighbors=5` |
| `n_clusters` | `KMeans` | Number of clusters | `n_clusters=4` |
| `n_components` | `PCA` | Dimensions to keep (int) or variance to keep (0 to 1) | `n_components=0.95` |
| `handle_unknown` | `OneHotEncoder` | `"ignore"` = unseen categories become all zeros instead of an error | `handle_unknown="ignore"` |
| `strategy` | `SimpleImputer` | Fill value: `"mean"`, `"median"`, `"most_frequent"`, `"constant"` | `strategy="median"` |
| `remainder` | `ColumnTransformer` | What to do with columns not listed: `"drop"` or `"passthrough"` | `remainder="drop"` |
| `param_grid` | `GridSearchCV` | Dict of parameter lists to try; pipeline steps use `step__param` | `{"model__C": [0.1, 1, 10]}` |

---

## 1. Install and Import

> Installing scikit-learn and the usual companions. Package name is `scikit-learn`, import name is `sklearn`. Use it in any classic ML task on tabular data (not deep learning).

```powershell
pip install scikit-learn pandas numpy matplotlib joblib
uv add scikit-learn pandas              # with uv
```

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
```

## 2. The ML Workflow

> The standard steps of a machine learning project. Each step maps to a scikit-learn tool shown in the sections below. Use it as a checklist for every modelling task.

```text
1. Define the target (y) and features (X)
2. Split into train and test          -> train_test_split
3. Preprocess (impute, scale, encode) -> SimpleImputer, StandardScaler, OneHotEncoder
4. Combine into a pipeline            -> Pipeline, ColumnTransformer
5. Train a baseline, then better models -> fit
6. Evaluate with cross-validation     -> cross_val_score
7. Tune hyperparameters               -> GridSearchCV / RandomizedSearchCV
8. Final check on the test set ONCE   -> score / metrics
9. Save the pipeline                  -> joblib.dump
```

## 3. The Estimator API

> The same few methods on every scikit-learn object. `fit` learns from data; `predict` or `transform` applies what was learned. Use it always; once you know this, every model and transformer works the same way.

| Method | On | Does |
|---|---|---|
| `fit(X, y)` | models, transformers | Learn from training data |
| `predict(X)` | models | Predict labels / values |
| `predict_proba(X)` | classifiers | Probability for each class |
| `score(X, y)` | models | Default metric (accuracy or R2) |
| `transform(X)` | transformers | Apply learned transformation |
| `fit_transform(X)` | transformers | Fit and transform in one step (training data only) |
| `get_params()` / `set_params()` | all | Read / change hyperparameters |

```python
model = SomeModel(param=value)      # 1. create
model.fit(X_train, y_train)         # 2. learn
y_pred = model.predict(X_test)      # 3. predict
```

Learned attributes end with `_`: `model.coef_`, `scaler.mean_`, `model.feature_importances_`.

## 4. Load Data (X and y)

> Getting features `X` (inputs) and target `y` (what to predict). From a DataFrame, or from built-in example datasets. Use it for the start of every task.

```python
df = pd.read_csv("houses.csv")
X = df.drop(columns=["price"])      # features: DataFrame
y = df["price"]                     # target: Series

from sklearn.datasets import load_iris, fetch_california_housing
X, y = load_iris(return_X_y=True, as_frame=True)                 # classification
X, y = fetch_california_housing(return_X_y=True, as_frame=True)  # regression
```

`X` must be 2D (rows x columns); `y` is 1D. One feature only: `X = df[["size"]]` (double brackets).

## 5. Train / Test Split

> Keeping some data aside to measure performance on unseen rows. `train_test_split` shuffles and splits rows; the test set is used only at the end. Use it in every model; evaluating on training data gives falsely good results.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y   # stratify for classification
)
```

Time series: do not shuffle; train on the past, test on the future (`shuffle=False` or `TimeSeriesSplit`).

## 6. Scaling Numeric Features

> Putting numeric columns on a similar scale. Fit the scaler on training data only, then transform train and test with it. Use it for distance or gradient based models (linear / logistic regression, SVM, KNN, PCA, neural nets). Tree models do not need it.

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

scaler = StandardScaler()                   # mean 0, std 1
X_train_s = scaler.fit_transform(X_train)   # learn mean / std from TRAIN
X_test_s = scaler.transform(X_test)         # apply the SAME numbers to TEST
```

| Scaler | Result | Use when |
|---|---|---|
| `StandardScaler` | mean 0, std 1 | Default choice |
| `MinMaxScaler` | range 0 to 1 | Need bounded values |
| `RobustScaler` | uses median / IQR | Data has outliers |

## 7. Encoding Categorical Features

> Turning text categories into numbers models can use. One-hot creates one 0/1 column per category; ordinal maps categories to ordered integers. Use it in any text / category column (city, product type, size S/M/L).

```python
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder

ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
ohe.fit_transform(X_train[["city"]])            # Berlin -> [1, 0, 0]
ohe.get_feature_names_out()

ord_enc = OrdinalEncoder(categories=[["S", "M", "L"]])   # order matters
ord_enc.fit_transform(X_train[["size"]])        # S -> 0, M -> 1, L -> 2

LabelEncoder().fit_transform(y)                 # for the TARGET only
```

| Encoder | Use for |
|---|---|
| `OneHotEncoder` | Categories without order (city, colour) |
| `OrdinalEncoder` | Categories with order (small < medium < large), or tree models |
| `LabelEncoder` | The target `y` of a classifier |

## 8. Missing Values

> Filling empty values so models can train. `SimpleImputer` learns a fill value (mean, median, most frequent) from training data. Most models fail on NaN (some, like `HistGradientBoosting`, handle it themselves).

```python
from sklearn.impute import SimpleImputer, KNNImputer

num_imp = SimpleImputer(strategy="median")
cat_imp = SimpleImputer(strategy="most_frequent")
X_train_num = num_imp.fit_transform(X_train[["age", "income"]])

KNNImputer(n_neighbors=5)                       # fill from similar rows
SimpleImputer(strategy="median", add_indicator=True)   # also add "was missing" columns
```

## 9. ColumnTransformer

> Different preprocessing for different columns in one object. A list of `(name, transformer, columns)`; results are joined side by side. Use it for real datasets with both numeric and categorical columns (almost always).

```python
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.pipeline import Pipeline

num_cols = ["age", "income"]
cat_cols = ["city", "segment"]

preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]), num_cols),
    ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
], remainder="drop")

# Select columns by type instead of by name
make_column_selector(dtype_include="number")
make_column_selector(dtype_include=object)
```

## 10. Pipelines

> Preprocessing steps and a model chained into one object. `fit` runs every step on training data; `predict` applies the same steps to new data. Use it always. Prevents data leakage, keeps code short, and you save ONE object for production.

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("prep", preprocess),
    ("model", LogisticRegression(max_iter=1000)),
])
pipe.fit(X_train, y_train)
pipe.predict(X_test)
pipe.score(X_test, y_test)

pipe.named_steps["model"].coef_             # access a step
pipe.set_params(model__C=0.5)               # step name + __ + parameter

make_pipeline(StandardScaler(), LogisticRegression())   # auto-named steps
```

## 11. Regression Models

> Models that predict a number (price, demand, temperature). Same `fit` / `predict` API; they differ in how they learn the relationship. Use this when the target is continuous.

```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor

DummyRegressor(strategy="mean")             # baseline: always predicts the mean
LinearRegression()                          # simple, interpretable
Ridge(alpha=1.0)                            # linear + L2 regularisation
Lasso(alpha=0.1)                            # linear + L1 (sets some coefficients to 0)
DecisionTreeRegressor(max_depth=5)
RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
HistGradientBoostingRegressor()             # fast, strong, handles NaN
```

## 12. Classification Models

> Models that predict a category (spam / not spam, churn yes / no, species). Same API; `predict_proba` gives class probabilities. Use this when the target is a label.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.dummy import DummyClassifier

DummyClassifier(strategy="most_frequent")   # baseline
LogisticRegression(max_iter=1000)           # strong linear baseline
DecisionTreeClassifier(max_depth=5)
RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
HistGradientBoostingClassifier()            # often best on tabular data
KNeighborsClassifier(n_neighbors=5)
SVC(probability=True)                       # needs scaling; slow on big data
GaussianNB()                                # fast, simple

proba = model.predict_proba(X_test)[:, 1]   # probability of the positive class
```

## 13. Clustering and Dimensionality Reduction

> Finding groups without labels (clustering) and compressing many columns into few (PCA). Only `X` is used (no `y`); scale the data first. Use it for customer segmentation, anomaly detection, visualising high-dimensional data.

```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

X_s = StandardScaler().fit_transform(X)

km = KMeans(n_clusters=4, n_init="auto", random_state=42)
labels = km.fit_predict(X_s)
km.inertia_                                  # within-cluster spread (elbow method)
silhouette_score(X_s, labels)                # -1 to 1, higher = better separated

DBSCAN(eps=0.5, min_samples=5).fit_predict(X_s)   # finds clusters of any shape, -1 = noise

pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_s)                # for plotting
pca.explained_variance_ratio_                # variance kept per component
```

## 14. Regression Metrics

> Numbers that say how good a regression model is. Compare `y_test` with `y_pred`. Use it for evaluating and comparing regression models.

```python
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             root_mean_squared_error, r2_score,
                             mean_absolute_percentage_error)

mean_absolute_error(y_test, y_pred)             # MAE: average error, same unit as y
root_mean_squared_error(y_test, y_pred)         # RMSE: punishes big errors more
r2_score(y_test, y_pred)                        # R2: 1 = perfect, 0 = as good as the mean
mean_absolute_percentage_error(y_test, y_pred)  # MAPE: error in % (bad if y near 0)
```

| Metric | Read as | Better |
|---|---|---|
| MAE | "Off by X on average" | Lower |
| RMSE | Like MAE but big misses count more | Lower |
| R2 | Share of variation explained | Higher (max 1) |

## 15. Classification Metrics

> Numbers and tables that say how good a classifier is. Compare true labels with predicted labels (or probabilities). Use this when evaluating classifiers; accuracy alone is misleading for imbalanced data.

```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, classification_report, roc_auc_score,
                             ConfusionMatrixDisplay)

accuracy_score(y_test, y_pred)
precision_score(y_test, y_pred)         # of predicted positives, how many are right
recall_score(y_test, y_pred)            # of real positives, how many were found
f1_score(y_test, y_pred)                # balance of precision and recall
roc_auc_score(y_test, proba)            # ranking quality, uses probabilities
print(classification_report(y_test, y_pred))
confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay.from_predictions(y_test, y_pred)   # plot
```

```text
                 Predicted NO   Predicted YES
Actual NO        TN             FP  (false alarm)
Actual YES       FN (missed)    TP
```

| Metric | Focus on it when |
|---|---|
| Accuracy | Classes are balanced |
| Precision | False alarms are costly (spam filter) |
| Recall | Missing a positive is costly (fraud, disease) |
| F1 | You need a balance, classes are imbalanced |
| ROC AUC | Comparing models independent of threshold |

Multi-class: add `average="macro"` or `"weighted"` to precision / recall / f1.

## 16. Cross-Validation

> Evaluating on several train / validation splits instead of one. Data is split into k folds; each fold is the validation set once; you get k scores. Use it for comparing models or settings reliably, especially on small datasets.

```python
from sklearn.model_selection import cross_val_score, cross_validate, StratifiedKFold, KFold, TimeSeriesSplit

scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="f1")
scores.mean(), scores.std()

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)   # classification
cv = KFold(n_splits=5, shuffle=True, random_state=42)             # regression
cv = TimeSeriesSplit(n_splits=5)                                  # time series

res = cross_validate(pipe, X_train, y_train, cv=cv,
                     scoring=["accuracy", "f1"], return_train_score=True)
```

Train score much higher than validation score = overfitting.

## 17. Hyperparameter Tuning

> Searching for the best model settings. Try combinations with cross-validation; keep the best. Grid = all combinations, Random = a sample. Use it after you have a working pipeline and baseline.

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import randint

param_grid = {
    "model__n_estimators": [100, 300],
    "model__max_depth": [None, 5, 10],
}
search = GridSearchCV(pipe, param_grid, cv=5, scoring="f1", n_jobs=-1)
search.fit(X_train, y_train)
search.best_params_
search.best_score_
best_model = search.best_estimator_         # already refit on all training data

search = RandomizedSearchCV(pipe, {"model__n_estimators": randint(100, 500)},
                            n_iter=20, cv=5, random_state=42, n_jobs=-1)
```

Parameter names in a pipeline: `<step name>__<parameter>` (two underscores).

## 18. Feature Importance

> Which features the model relies on most. Tree models expose `feature_importances_`; linear models `coef_`; permutation importance works for any model. Use it for explaining a model, removing useless features, sanity-checking for leakage.

```python
from sklearn.inspection import permutation_importance

names = pipe.named_steps["prep"].get_feature_names_out()
imp = pipe.named_steps["model"].feature_importances_        # tree models
pd.Series(imp, index=names).sort_values(ascending=False).head(10)

result = permutation_importance(pipe, X_test, y_test, n_repeats=10, random_state=42)
pd.Series(result.importances_mean, index=X_test.columns).sort_values(ascending=False)
```

A single feature with huge importance can mean data leakage (it contains the answer).

## 19. Imbalanced Classes

> One class is much rarer than the other (fraud 1%, normal 99%). Weight rare classes more, choose better metrics, and adjust the decision threshold. Use this when accuracy looks great but the model never predicts the rare class.

```python
LogisticRegression(class_weight="balanced", max_iter=1000)
RandomForestClassifier(class_weight="balanced")
train_test_split(X, y, stratify=y, test_size=0.2)

proba = model.predict_proba(X_test)[:, 1]
y_pred = (proba >= 0.3).astype(int)          # lower threshold = more positives, higher recall
```

Use F1, recall, precision or ROC AUC instead of accuracy. For resampling (SMOTE), see the `imbalanced-learn` package.

## 20. Save and Load a Model

> Storing a trained pipeline to use later or in an API. `joblib.dump` writes the fitted object to a file; `joblib.load` reads it back. Use it after training, before serving predictions (for example with FastAPI).

```python
import joblib

joblib.dump(pipe, "model.joblib")
pipe = joblib.load("model.joblib")
pipe.predict(new_df)                     # new_df needs the same columns as training X
```

Load with the same scikit-learn version you saved with. Never load model files from untrusted sources (they can run code). Serving: see [39 - FastAPI](39_fastapi.md).

## 21. Full Example

> An end-to-end classification pipeline you can copy. Split, preprocess by column type, train, cross-validate, test, save. Use it as a template for a new tabular ML task.

```python
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.read_csv("customers.csv")
X = df.drop(columns=["churn"])
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]),
     make_column_selector(dtype_include="number")),
    ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]),
     make_column_selector(dtype_include=object)),
])

pipe = Pipeline([
    ("prep", preprocess),
    ("model", HistGradientBoostingClassifier(random_state=42)),
])

print("CV F1:", cross_val_score(pipe, X_train, y_train, cv=5, scoring="f1").mean())
pipe.fit(X_train, y_train)
print(classification_report(y_test, pipe.predict(X_test)))
joblib.dump(pipe, "churn_model.joblib")
```

## 22. Which Model to Use

> A starting point for choosing a model. Match the task and data size; always compare against a dummy baseline. Use it for starting a new problem.

| Situation | Start with |
|---|---|
| Any task | `DummyClassifier` / `DummyRegressor` as baseline |
| Need an interpretable model | `LogisticRegression` / `LinearRegression` / `Ridge` |
| Tabular data, best accuracy | `HistGradientBoosting*`, `RandomForest*` |
| Small dataset, few features | `LogisticRegression`, `SVC`, `KNeighbors*` |
| Many features, want selection | `Lasso`, `LogisticRegression(penalty="l1", solver="liblinear")` |
| Text data | `TfidfVectorizer` + `LogisticRegression` |
| No labels, find groups | `KMeans`, `DBSCAN` |
| Too many columns to plot | `PCA` |

Official chooser: search "scikit-learn choosing the right estimator".

## 23. Troubleshooting

| Error / problem | Fix |
|---|---|
| `ValueError: Expected 2D array, got 1D array` | Use `X = df[["col"]]` or `x.reshape(-1, 1)` |
| `could not convert string to float` | Encode text columns (OneHotEncoder) inside a ColumnTransformer |
| `Input X contains NaN` | Add `SimpleImputer`, or use `HistGradientBoosting*` |
| `ConvergenceWarning: lbfgs failed to converge` | Scale features and / or raise `max_iter` |
| `Found unknown categories` at predict time | `OneHotEncoder(handle_unknown="ignore")` |
| Test score much worse than train score | Overfitting: simplify model (`max_depth`, regularisation), more data, cross-validate |
| Score is suspiciously perfect | Data leakage: target info in a feature, or preprocessing fitted on all data before splitting |
| Accuracy high but rare class never predicted | Imbalance: see section 19 |
| Feature names mismatch warning | Predict with a DataFrame with the same columns as training |
| `InconsistentVersionWarning` when loading model | Use the same scikit-learn version as when saving, or retrain |
| Grid search is slow | `n_jobs=-1`, `RandomizedSearchCV`, fewer values, smaller `cv` |

## 24. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: First pipeline

On the iris dataset, split stratified, train a scaled logistic regression in a pipeline and print test accuracy.

<details markdown="1">
<summary>Solution</summary>

```python
X, y = load_iris(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_tr, y_tr)
print(pipe.score(X_te, y_te))
```

</details>

### Exercise 2: Mixed columns

Preprocess numeric columns (median impute + scale) and categorical columns (most frequent + one-hot) together.

<details markdown="1">
<summary>Solution</summary>

```python
prep = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num_cols),
    ("cat", make_pipeline(SimpleImputer(strategy="most_frequent"),
                          OneHotEncoder(handle_unknown="ignore")), cat_cols),
])
```

</details>

### Exercise 3: Cross-validation and tuning

5-fold F1 score for the pipeline, then grid-search `C` in [0.1, 1, 10].

<details markdown="1">
<summary>Solution</summary>

```python
cross_val_score(pipe, X_tr, y_tr, cv=5, scoring="f1_macro").mean()
search = GridSearchCV(pipe, {"logisticregression__C": [0.1, 1, 10]}, cv=5, scoring="f1_macro")
search.fit(X_tr, y_tr)
search.best_params_
```

</details>

---

<!-- nav:start -->
**Previous:** [21 - Seaborn](21_seaborn.md) | **Index:** [All guides](README.md) | **Next:** [23 - PyTorch](23_pytorch.md)
<!-- nav:end -->
