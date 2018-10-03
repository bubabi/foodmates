from collections import defaultdict
from io import StringIO

import numpy
import random as rand

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from common.models import Condition
from .resources import ConditionResource


def place_prediction(given_conditions):

    for e in given_conditions:
        if len(e) == 0:
            return -1
        else:
            break

    condition_resource = ConditionResource()
    dataset = condition_resource.export()
    data = pd.read_csv(StringIO(dataset.csv))

    features = ['pay', 'time', 'kitchen', 'hunger']
    X = data[features].copy()
    y = data[['place']].copy()
    target_cond = defaultdict(list)

    for user_cond in given_conditions:
        if len(user_cond) == 0:
            continue
        target_cond['pay'].extend([int(i) for i in list(user_cond.values_list('pay', flat=True))])
        target_cond['time'].extend([int(i) for i in list(user_cond.values_list('time', flat=True))])
        target_cond['kitchen'].extend([int(i) for i in list(user_cond.values_list('kitchen', flat=True))])
        target_cond['hunger'].extend([int(i) for i in list(user_cond.values_list('hunger', flat=True))])

    # counting freq
    conditions_freq_info = {}
    for features in list(target_cond):
        # print(list(target_cond[features]))
        value = pd.Series(list(target_cond[features])).value_counts().reset_index().values.tolist()
        conditions_freq_info[features] = value

    max_freq_conds = [[], []]
    freq_dict = {}
    for k in conditions_freq_info:
        if len(conditions_freq_info[k]) >= 2:
            max_freq_conds[0].append(conditions_freq_info[k][0][0])
            freq_dict[k] = conditions_freq_info[k][0][1]
            max_freq_conds[1].append(conditions_freq_info[k][1][0])

        else:
            max_freq_conds[0].append(conditions_freq_info[k][0][0])
            freq_dict[k] = conditions_freq_info[k][0][1]
            max_freq_conds[1].append(conditions_freq_info[k][0][0])

    given_conditions = [max_freq_conds[0] if (rand.random() < 0.5) else max_freq_conds[1]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=324)
    place_classifier = DecisionTreeClassifier(max_leaf_nodes=10, random_state=0)
    place_classifier.fit(X_train, y_train)
    predictions = place_classifier.predict(X_test)

    dataframe_output = pd.DataFrame(given_conditions, columns=['pay', 'time', 'kitchen', 'hunger'])
    place_id = place_classifier.predict(dataframe_output)
    score = accuracy_score(y_true=y_test, y_pred=predictions)

    cond_count = 0
    for cond in conditions_freq_info['pay']:
        cond_count += cond[1]

    context = {'place_id': place_id,
               'score': score,
               'max_freq_conds': max_freq_conds[0],
               'freq_dict': freq_dict,
               'total_cond_count': cond_count}

    return context



