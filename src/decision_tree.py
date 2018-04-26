import graphviz
from sklearn import tree
from sklearn.preprocessing import LabelBinarizer
from sklearn.tree import DecisionTreeClassifier

from loans import LoanDataLoader
import numpy as np
import pandas as pd
from sklearn_pandas import DataFrameMapper

DROP = 888

_FEATURES = [
    ('_id_x', DROP),
    ('_id_y', DROP),
    ("credit_score", None),
    ("first_payment_date", DROP),
    ("first_time_homebuyer_flag", DROP),
    ("maturity_date", DROP),
    ("metro_stat_area", DROP),
    ("morg_insur_percent", None),
    ("num_units", None),
    ('occupancy_stat', LabelBinarizer()),
    ("combined_loan_to_val", None),
    ("orig_debt_to_income", None),
    ("orig_upb", None),
    ("orig_loan_to_val", None),
    ("orig_interest_rate", None),
    ('channel', LabelBinarizer()),
    ('prepay_penalty_flag', LabelBinarizer()),
    ('product_type', DROP),
    ('loan_purpose', DROP),
    ("property_state", DROP),
    ("property_type", LabelBinarizer()),
    ("postal_code", DROP),
    ("loan_seq_num", DROP),
    ('seller_name', DROP),
    ("orig_loan_term", DROP),
    ("num_borrowers", None),
    ('service_name', DROP),
    ('super_conform_flag', DROP),
    ("monthly_report_period", DROP),
    ("curr_actual_upb", None),
    ("curr_loan_deliq_status", None),
    # ('default', LabelBinarizer()),
    ("loan_age", None),
    ("remaining_months_maturity", DROP),
    ("repurchase_flag", DROP),
    ("modify_flag", DROP),
    ("zero_bal_code", DROP),
    ("zero_bal_date", DROP),
    ("curr_interest_rate", None),
    ('curr_deferred_upb', DROP),
    ("due_date_last_paid", DROP),
    ("mi_recoveries", DROP),
    ("net_sales_proceeds", DROP),
    ("non_mi_recoveries", DROP),
    ("expenses", DROP),
    ("legal_costs", DROP),
    ("maintenance_costs", DROP),
    ("taxes_and_insurance", DROP),
    ("misc_expenses", DROP),
    ("actual_loss_calc", DROP),
    ("modif_cost", DROP)
]

mapping = {}


def pick_non_nan(df, col):
    if col in mapping:
        return mapping[col]
    count = 0
    while True:
        sample = list(df[col].sample())[0]
        if sample not in [" ", ' ', '', float('nan'), np.NaN, np.NAN]:
            mapping[col] = sample
            return sample
        count = count + 1
        if count >= len(df[col]):
            print("All data in column is NaN")
            return 0

def fix_df(df):
    for col in df.columns:
        print("Cleaning {}..".format(col))
        df[col] = df[col].replace([" ", ' ', '', float('nan'), np.NaN, np.NAN], pick_non_nan(df, col))
    return df


_FEATURES = {v[0]: v[1] for v in _FEATURES}

loader = LoanDataLoader("data/", debug=False)
db = loader.db
print("Loading origin loans...")
orig_loans = list(db.origin_loans.find())

print("Loading monthly loans...")

monthly_loans = list(db.monthly_loans.find())

df1 = pd.DataFrame(orig_loans)
df2 = pd.DataFrame(monthly_loans)

# Merge and drop
df = pd.merge(df1, df2, how='right', on='loan_seq_num')

to_drop = []
for k, v in _FEATURES.items():
    if v == DROP:
        df.drop([k], 1, inplace=True)
        to_drop.append(k)

for d in to_drop:
    _FEATURES.pop(d)


default = df['curr_loan_deliq_status'].isin(['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'])
df['default'] = default
df = fix_df(df)
df.drop(['curr_loan_deliq_status'], 1, inplace=True)
_FEATURES.pop('curr_loan_deliq_status')

y = []
for row in df['default']:
    if row:
        y.append(0)
    else:
        y.append(1)

# Number of defaults isn't equal to non-defaults for 50-50 ratio
if sum(y) != len(y)-sum(y):
    defaulted = df.loc[df['default']]
    nondefaulted = df.loc[df['default'] == False]
    df = nondefaulted.sample(len(y)-sum(y))
    df = df.append(defaulted)

tw = 2

def featurize(df, features):
    list_features = [(k, v, {}) for k, v in features.items()]
    return DataFrameMapper(list(filter(lambda x: x[0] in df.columns, list_features)))


def fill_nan(data):
    x = 0
    arr = np.zeros(shape=data.shape)
    for row in data:
        y = 0
        for col in row:
            if col and not isinstance(col, str):
                arr[x][y] = float(col)
            else:
                arr[x][y] = 0  # np.NAN
            y = y + 1
        x = x + 1
    return arr


df_x = df[df.columns.drop('default')]

df_y = df['default']

featurized = featurize(df, _FEATURES)
featurized.fit_transform(df_x, df_y)
x = fill_nan(featurized.transform(df_x))
y = []
for row in df_y:
    if row:
        y.append(0)
    else:
        y.append(1)


clf = DecisionTreeClassifier()
clf = clf.fit(x, y)

dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=featurized.transformed_names_,
                                class_names=["Defaulted", "Didn't Default"],
                                filled=True, rounded=True,
                                special_characters=True)

graph = graphviz.Source(dot_data)
graph.render("test_out")
print("Not Defaulted ratio {}".format(sum(y) / len(y)))
print("Defaulted ratio {}".format((len(y) - sum(y)) / len(y)))
