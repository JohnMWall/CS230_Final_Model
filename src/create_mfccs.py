import pandas as pd
from collections import Counter
import sys
sys.path.append('../dialectdetect-master/src>')
import getsplit


from tensorflow.keras import utils
import accuracy
import multiprocessing
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import MaxPool2D, Conv2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard

DEBUG = True
SILENCE_THRESHOLD = .01
RATE = 24000
N_MFCC = 13

def to_categorical(y):
    '''
    Converts list of languages into a binary class matrix
    :param y (list): list of languages
    :return (numpy array): binary class matrix
    '''
    lang_dict = {}
    print(set(y))
    for index,language in enumerate(set(y)):
        lang_dict[language] = index
    y = list(map(lambda x: lang_dict[x],y))
    return utils.to_categorical(y, len(lang_dict))

def to_categorical_v2(y_train, y_test):
    '''
    Converts list of languages into a binary class matrix
    :param y (list): list of languages
    :return (numpy array): binary class matrix
    '''
    lang_dict = {}
    print(set(y_train.append(y_test)))
    for index,language in enumerate(set(y_train.append(y_test))):
        lang_dict[language] = index
    y_train = list(map(lambda x: lang_dict[x],y_train))
    y_test = list(map(lambda x: lang_dict[x],y_test))
    return utils.to_categorical(y_train, len(lang_dict)), utils.to_categorical(y_test, len(lang_dict))

def get_wav(file_id):
    '''
    Load wav file from disk and down-samples to RATE
    :param file_id (list): list of file names
    :return (numpy array): Down-sampled wav file
    '''
    print('{}.wav'.format(file_id))
    y, sr = librosa.load('../audio/{}.wav'.format(file_id))
    return(librosa.core.resample(y=y,orig_sr=sr,target_sr=RATE, scale=True))

def to_mfcc(wav):
    '''
    Converts wav file to Mel Frequency Ceptral Coefficients
    :param wav (numpy array): Wav form
    :return (2d numpy array: MFCC
    '''
    return(librosa.feature.mfcc(y=wav, sr=RATE, n_mfcc=N_MFCC))

def remove_silence(wav, thresh=0.04, chunk=5000):
    '''
    Searches wav form for segments of silence. If wav form values are lower than 'thresh' for 'chunk' samples, the values will be removed
    :param wav (np array): Wav array to be filtered
    :return (np array): Wav array with silence removed
    '''

    tf_list = []
    for x in range(len(wav) / chunk):
        if (np.any(wav[chunk * x:chunk * (x + 1)] >= thresh) or np.any(wav[chunk * x:chunk * (x + 1)] <= -thresh)):
            tf_list.extend([True] * chunk)
        else:
            tf_list.extend([False] * chunk)

    tf_list.extend((len(wav) - len(tf_list)) * [False])
    return(wav[tf_list])

def normalize_mfcc(mfcc):
    '''
    Normalize mfcc
    :param mfcc:
    :return:
    '''
    mms = MinMaxScaler()
    return(mms.fit_transform(np.abs(mfcc)))

if __name__ == '__main__':
    '''
    Console command example:
    python trainmodel.py bio_metadata.csv model50
    '''

    # Load arguments
    file_name = sys.argv[1]

    # Load metadata
    df = pd.read_csv(file_name)
    df = df['ID'] # changed from language_num to ID to work with DARE instead of SAA

    # Get resampled wav files using multiprocessing
    if DEBUG:
        print('Loading wav files....')
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    wavs = pool.map(get_wav, df)
    # X_test = pool.map(get_wav, X_test)

    # Convert to MFCC
    if DEBUG:
        print('Converting to MFCC....')
    mfccs = pool.map(to_mfcc, wavs)
    # X_train = pool.map(to_mfcc, X_train)
    # X_test = pool.map(to_mfcc, X_test)

    for mfcc, num in zip(mfccs, df):
        print(mfcc.shape)
        np.savetxt('../mfccs/{}.csv'.format(num), mfcc, delimiter =",")

