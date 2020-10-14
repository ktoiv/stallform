import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from app.database.data_accessor import DataAccessor
import pickle


def train_neural_network():

    da = DataAccessor('stallform', 'horse_performances')
    da.connect()

    data = da.find({})

    df = pd.DataFrame(data)


    driver_da = DataAccessor('stallform', 'driver_stats')
    driver_da.connect()
    driver_df = pd.DataFrame(driver_da.find({}))

    coach_da = DataAccessor('stallform', 'coach_stats')
    coach_da.connect()
    coach_df = pd.DataFrame(coach_da.find({}))


    coach_df = coach_df.rename(columns={'name': 'coachName', 'total': 'coach_total', 'win%': 'coach_win%'})


    driver_df = driver_df.rename(columns={'name': 'driverName', 'total': 'driver_total', 'win%': 'driver_win%'})


    df2 = pd.merge(df, coach_df, on="coachName")

    final_df = pd.merge(df2, driver_df, on="driverName")


    nn_columns = [ 'startTrack', 'distance', 'winner',
           'rear_shoes', 'front_shoes', 'month', 'breed',
           'car_start', 'coach_total','coach_win%', 
           'driver_total', 'driver_win%']

    columns_to_remove = list(filter(lambda c: c not in nn_columns, final_df.columns))


    for column in columns_to_remove:
        del final_df[column]



    final_df.head()

    final_df['breed'] = final_df['breed'] == 'L'


    final_df["rear_shoes"] = final_df["rear_shoes"].astype(int)
    final_df["front_shoes"] = final_df["front_shoes"].astype(int)
    final_df["breed"] = final_df["breed"].astype(int)
    final_df["car_start"] = final_df["car_start"].astype(int)
    final_df["winner"] = final_df["winner"].astype(int)


    final_df.head()

    train = final_df.sample(frac=0.8,random_state=200) #random state is a seed value
    test = final_df.drop(train.index)

    X = train.drop(['winner'], axis=1)
    y = train['winner']

    model = Sequential()
    model.add(Dense(16, input_dim=11, activation='relu'))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(6, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(X, y, epochs=15, batch_size=10)


    tX = test.drop(['winner'], axis=1)
    ty = test['winner']
    _, accuracy = model.evaluate(tX, ty)

    accuracy

    file = open('nn_model', 'wb')

    # dump information to that file
    pickle.dump(model, file)

    # close the file
    file.close()