import pandas as pd
import sys
from sklearn.model_selection import train_test_split

def filter_df(df):
    # return df[:25]
    '''
    Function to filter audio files based on df columns
    df column options: [age,age_of_english_onset,age_sex,birth_place,english_learning_method,
    english_residence,length_of_english_residence,native_language,other_languages,sex]
    :param df (DataFrame): Full unfiltered DataFrame
    :return (DataFrame): Filtered DataFrame
    '''

    # Leaving this here as reference for future use
    # usa = df[df.english_residence.str.contains("['usa']", regex=False)][:50]
    # can = df[df.english_residence.str.contains("['canada']", regex=False)][:50]
    # uk = df[df.english_residence.str.contains("['uk']", regex=False)][:50]
    # australia = df[df.english_residence.str.contains("['australia']", regex=False)][:50]
    # ireland = df[df.english_residence.str.contains("['ireland']", regex=False)][:50]
    # uk_usa = df[df.english_residence.str.contains("['uk','usa']", regex=False)][:50]

    # Every time you want to change to use a new col, make sure to change 'accent(southsplit)' 
    # to the name of the new column
    new_eng = df[df['accent(southsplit)'] == 'New England']
    nyc = df[df['accent(southsplit)'] == 'New York City']
    south_in = df[df['accent(southsplit)'] == 'Inland South'][:100]
    south_low = df[df['accent(southsplit)'] == 'Lowland South'][:100]
    midland = df[df['accent(southsplit)'] == 'Midland'][:100]
    north_cent = df[df['accent(southsplit)'] == 'North Central']
    north = df[df['accent(southsplit)'] == 'North'][:100]
    west = df[df['accent(southsplit)'] == 'West'][:100]

    # return south_in.append(south_low).append(midland).append(north)
    return west.append(north).append(midland).append(south_low).append(south_in)
    # return df


    # return usa.append(can).append(uk).append(australia).append(ireland).append(uk_usa)

    # df_new['birth_place'].apply(lambda col: col['birth_place'] = col['birth_place'].str[-1])

def split_people(df,test_size=0.1):
    '''
    Create train test split of DataFrame
    :param df (DataFrame): Pandas DataFrame of audio files to be split
    :param test_size (float): Percentage of total files to be split into test
    :return X_train, X_test, y_train, y_test (tuple): Xs are list of df['language_num'] and Ys are df['native_language']
    '''


    return train_test_split(df['ID'],df['accent(southsplit)'],test_size=test_size, stratify=df['accent(southsplit)']) # random_state = 1234
    # return train_test_split(df['language_num'],df['native_language'],test_size=test_size) # random_state = 1234


if __name__ == '__main__':
    '''
    Console command example:
    python bio_data.csv
    '''

    csv_file = sys.argv[1]
    df = pd.read_csv(csv_file)
    filtered_df = filter_df(df)
    print(split_people(filtered_df))
