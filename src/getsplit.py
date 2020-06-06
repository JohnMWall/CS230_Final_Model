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

    # arabic = df[df.native_language.str.contains('arabic')][:25]
    # spanish = df[df.native_language.str.contains('spanish')][:25]
    # mandarin = df[df.native_language.str.contains('mandarin')][:25]
    # english = df[df.native_language.str.contains('english')][:25]
    # return english

    # mandarin = mandarin[mandarin.length_of_english_residence < 10][:25]
    # arabic = arabic[arabic.length_of_english_residence < 10][:25]

    # usa = df[df.english_residence.str.contains("['usa']", regex=False)][:50]
    # can = df[df.english_residence.str.contains("['canada']", regex=False)][:50]
    # uk = df[df.english_residence.str.contains("['uk']", regex=False)][:50]
    # australia = df[df.english_residence.str.contains("['australia']", regex=False)][:50]
    # ireland = df[df.english_residence.str.contains("['ireland']", regex=False)][:50]
    # uk_usa = df[df.english_residence.str.contains("['uk','usa']", regex=False)][:50]

    canada = df[df.accent == 'Canada']
    new_eng = df[df.accent == 'New England']
    nyc = df[df.accent == 'New York City']
    south = df[df.accent == 'South'][:100]
    midland = df[df.accent == 'Midland'][:100]
    north_cent = df[df.accent == 'North Central']
    north = df[df.accent == 'North'][:100]
    west = df[df.accent == 'West'][:60]

    return south.append(midland).append(north)
    # return df


    # return usa.append(can).append(uk).append(australia).append(ireland).append(uk_usa)

    # df_new['birth_place'].apply(lambda col: col['birth_place'] = col['birth_place'].str[-1])

def split_people(df,test_size=0.2):
    '''
    Create train test split of DataFrame
    :param df (DataFrame): Pandas DataFrame of audio files to be split
    :param test_size (float): Percentage of total files to be split into test
    :return X_train, X_test, y_train, y_test (tuple): Xs are list of df['language_num'] and Ys are df['native_language']
    '''


    return train_test_split(df['language_num'],df['accent'],test_size=test_size) # random_state = 1234
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
