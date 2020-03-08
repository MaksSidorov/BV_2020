import pandas as pd
import numpy as np
import catboost


def make_predict(df):
    try:
        val = df['номер_валка'].values.tolist()
        dct = dict()
        df = df.drop(['номер_валка'], axis=1)
        # Загрузка модели
        model = catboost.CatBoostRegressor()
        model.load_model(fname='model')
        ans = model.predict(df)
        for i in range(len(ans)):
            if val[i] not in dct.keys():
                dct[val[i]] = 0
            dct[val[i]] += ans[i]
        ans = []
        for key, val in dct.items():
            ans.append([key, val])
        return ans
    except Exception as err:
        print(err)






