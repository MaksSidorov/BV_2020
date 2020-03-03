import pandas as pd
import numpy as np
import catboost

def make_data(fname):
    df_t = pd.read_excel(fname, sheet_name='Проверка')
    df_r = pd.read_excel(fname, sheet_name='Рулоны')
    df_v = pd.read_excel(fname, sheet_name='Валки')

    arr = df_v['материал_валка'].values
    for i in range(len(arr)):
        arr[i] = int(arr[i][14:])
    df_v['материал_валка'] = arr

    df_t['положение_в_клети'] = df_t['положение_в_клети'] == 'верх'
    df_t['положение_в_клети'] = df_t['положение_в_клети'].astype('int')
    df_t['время'] = (df_t['дата_вывалки'] - df_t['дата_завалки']).astype('int64') / 1000000000

    rul_ids = dict()
    v = []
    c = -1
    for i in df_t['дата_завалки']:
        if str(i) not in rul_ids.keys():
            rul_ids[str(i)] = c
            c += 1
        v.append(c)
    df_t['rul_id'] = v

    times = np.array([])
    for i in df_t['дата_вывалки']:
        if i not in times:
            times = np.append(times, i)

    ids = []
    c = 0
    for i in df_r['Время_обработки']:
        if c < len(times) and i > times[c]:
            c += 1
        ids.append(c)
    df_r['rul_id'] = ids

    times = []
    for i in df_t['дата_вывалки'].values.tolist():
        if i not in times:
            times.append(int(i))

    df_r = df_r.loc[df_r['rul_id'] < len(times)]

    time = []
    for i in range(len(times)):
        lst = df_r.loc[df_r['rul_id'] == i]['Время_обработки'].values.tolist()
        lst.append(times[i])
        for j in range(1, len(lst)):
            time.append((lst[j] - lst[j - 1]) / 1000000000)
    df_r['time'] = time

    df_r['Марка'] = df_r['Марка'].str[len('Марка стали'):].astype('int')

    df_t = df_t.drop(['дата_завалки', 'дата_вывалки'], axis=1)
    df_r = df_r.drop(['Время_обработки'], axis=1)

    df_v = pd.get_dummies(df_v, columns=['материал_валка'])

    df_r['Толщина_х_Ширина'] = df_r['Толщина'] * df_r['Ширина']
    df_rl = pd.DataFrame()

    df_rl['sum_tol'] = df_r.groupby(['rul_id'])['Толщина'].sum()
    df_rl['Толщина_х_Ширина'] = df_r.groupby(['rul_id'])['Толщина'].median()
    df_rl['median_time'] = df_r.groupby(['rul_id'])['time'].median()
    df_rl['sum_mass'] = df_r.groupby(['rul_id'])['Масса'].sum()
    df_rl['counts'] = df_r.groupby(['rul_id'])['Масса'].count()

    counter_df_train = df_r.groupby(['rul_id', 'Марка'])['Толщина_х_Ширина'].sum()
    cat_counts_train = counter_df_train.reset_index().pivot(index='rul_id',columns='Марка', values='Толщина_х_Ширина')
    mass = df_r.groupby(['rul_id', ])['Толщина_х_Ширина'].sum()
    cat_counts_train = cat_counts_train.fillna(0)
    cat_counts_train.columns = ['Marka_tol_sh_sum_' + str(i) for i in cat_counts_train.columns]
    for i in cat_counts_train.columns:
        cat_counts_train[i] /= mass
    df_rl = pd.merge(df_rl, cat_counts_train, on='rul_id')

    counter_df_train = df_r.groupby(['rul_id', 'Марка'])['time'].sum()
    cat_counts_train = counter_df_train.reset_index().pivot(index='rul_id', columns='Марка', values='time')
    mass = df_r.groupby(['rul_id', ])['time'].sum()
    cat_counts_train = cat_counts_train.fillna(0)
    cat_counts_train.columns = ['Marka_time_sum_' + str(i) for i in cat_counts_train.columns]
    for i in cat_counts_train.columns:
        cat_counts_train[i] /= mass
    df_rl = pd.merge(df_rl, cat_counts_train, on='rul_id')

    counter_df_train = df_r.groupby(['rul_id', 'Марка'])['Масса'].sum()
    cat_counts_train = counter_df_train.reset_index().pivot(index='rul_id',columns='Марка', values='Масса')
    mass = df_r.groupby(['rul_id', ])['Масса'].sum()
    cat_counts_train = cat_counts_train.fillna(0)
    cat_counts_train.columns = ['Marka_sum_' + str(i) for i in cat_counts_train.columns]
    for i in cat_counts_train.columns:
        cat_counts_train[i] /= mass
    df_rl = pd.merge(df_rl, cat_counts_train, on='rul_id')

    counter_df_train = df_r.groupby(['rul_id', 'Марка'])['Толщина'].median()
    cat_counts_train = counter_df_train.reset_index().pivot(index='rul_id',columns='Марка', values='Толщина')
    cat_counts_train = cat_counts_train.fillna(0)
    cat_counts_train.columns = ['Marka_tol_median_' + str(i) for i in cat_counts_train.columns]
    df_rl = pd.merge(df_rl, cat_counts_train, on='rul_id')

    dct = {}
    iz = df_t['износ'].values
    v = df_t['номер_валка'].values
    valu = []
    for i in range(len(v)):
        if v[i] not in dct.keys():
            valu.append(0)
            dct[v[i]] = 0
        else:
            valu.append(dct[v[i]])
            dct[v[i]] += iz[i]
    df_t['доп_износ'] = valu

    df_t = pd.merge(df_t, df_rl, on='rul_id')

    df_t = pd.merge(df_t, df_v, on='номер_валка')

    df_t['time/mass'] = df_t['время'] / df_t['sum_mass']

    return df_t.drop(['rul_id'], axis=1)

def make_predict(df):
    val = df['номер_валка'].values.tolist()
    dct = dict()
    df = df.drop(['номер_валка'], axis=1)
    model = catboost.load_model('model.cbm')
    ans = model.predict(df)
    for i in range(len(ans)):
        if val[i] not in dct.keys():
            dct[val[i]] = 0
        dct[val[i]] += ans[i]

    return dct






