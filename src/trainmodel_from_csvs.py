import pandas as pd
from collections import Counter
import sys
sys.path.append('../dialectdetect-master/src>')
import getsplit


from tensorflow import keras 
from keras import utils
import accuracy
import multiprocessing
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler

from keras.metrics import Precision, Recall
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, GlobalAveragePooling2D
from keras.layers import MaxPool2D, Conv2D
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping, TensorBoard

DEBUG = True
SILENCE_THRESHOLD = .01
RATE = 24000
N_MFCC = 13
COL_SIZE = 100
EPOCHS = 20 #10 #35#250

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

def get_file(language_num):
    return np.loadtxt('../mfccs/{}.csv'.format(language_num), delimiter=',')

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

def make_segments(mfccs,labels):
    '''
    Makes segments of mfccs and attaches them to the labels
    :param mfccs: list of mfccs
    :param labels: list of labels
    :return (tuple): Segments with labels
    '''
    segments = []
    seg_labels = []
    for mfcc,label in zip(mfccs,labels):
        for start in range(0, int(mfcc.shape[1] / COL_SIZE)):
            segments.append(mfcc[:, start * COL_SIZE:(start + 1) * COL_SIZE])
            seg_labels.append(label)
    return(segments, seg_labels)

def segment_one(mfcc):
    '''
    Creates segments from on mfcc image. If last segments is not long enough to be length of columns divided by COL_SIZE
    :param mfcc (numpy array): MFCC array
    :return (numpy array): Segmented MFCC array
    '''
    segments = []
    for start in range(0, int(mfcc.shape[1] / COL_SIZE)):
        segments.append(mfcc[:, start * COL_SIZE:(start + 1) * COL_SIZE])
    return(np.array(segments))

def create_segmented_mfccs(X_train):
    '''
    Creates segmented MFCCs from X_train
    :param X_train: list of MFCCs
    :return: segmented mfccs
    '''
    segmented_mfccs = []
    for mfcc in X_train:
        segmented_mfccs.append(segment_one(mfcc))
    return(segmented_mfccs)


def train_model(X_train,y_train,X_validation,y_validation, batch_size=64): #32 #64
    '''
    Trains 2D convolutional neural network
    :param X_train: Numpy array of mfccs
    :param y_train: Binary matrix based on labels
    :return: Trained model
    '''

    # Get row, column, and class sizes
    rows = X_train[0].shape[0]
    cols = X_train[0].shape[1]
    val_rows = X_validation[0].shape[0]
    val_cols = X_validation[0].shape[1]
    num_classes = len(y_train[0])

    # input image dimensions to feed into 2D ConvNet Input layer
    input_shape = (rows, cols, 1)
    X_train = X_train.reshape(X_train.shape[0], rows, cols, 1 )

    # This breaks the implementation, so reshaping to match X_train
    X_validation = X_validation.reshape(X_validation.shape[0],val_rows,val_cols,1)
    # X_validation = X_validation.reshape(X_validation.shape[0], rows, cols, 1 )


    print('X_train shape:', X_train.shape)
    print(X_train.shape[0], 'training samples')

    print('X_validation shape:', X_validation.shape)
    print(X_validation.shape[0], 'validation samples')

    model = Sequential()

    model.add(Conv2D(32, kernel_size=(3,3), activation='relu',
                     data_format="channels_last",
                     input_shape=input_shape))

    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Conv2D(64,kernel_size=(3,3), activation='relu'))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.35))

    model.add(Dense(num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adadelta',
                  metrics=['accuracy'])

    # Stops training if accuracy does not change at least 0.005 over 10 epochs
    es = EarlyStopping(monitor='accuracy', min_delta=.005, patience=10, verbose=1, mode='auto')

    # Creates log file for graphical interpretation using TensorBoard
    tb = TensorBoard(log_dir='../logs', histogram_freq=0, batch_size=batch_size, write_graph=True, write_grads=True,
                     write_images=True, embeddings_freq=0, embeddings_layer_names=None,
                     embeddings_metadata=None)

    # Image shifting
    datagen = ImageDataGenerator(width_shift_range=0.05)

    # Fit model using ImageDataGenerator
    model.fit(datagen.flow(X_train, y_train, batch_size=batch_size),
                        steps_per_epoch=len(X_train) / batch_size#batch_size #8 #32
                        , epochs=EPOCHS,
                        callbacks=[es,tb], validation_data=(X_validation,y_validation))

    return (model)

def save_model(model, model_filename):
    '''
    Save model to file
    :param model: Trained model to be saved
    :param model_filename: Filename
    :return: None
    '''
    model.save('../models/{}.h5'.format(model_filename))  # creates a HDF5 file 'my_model.h5'



############################################################




#######################################

if __name__ == '__main__':
    '''
        Console command example:
        python trainmodel.py bio_metadata.csv model50
        '''

    # Load arguments
    # print(sys.argv)
    file_name = sys.argv[1]
    model_filename = sys.argv[2]
    COL_SIZE = int(sys.argv[3])
    EPOCHS = int(sys.argv[4])

    # Load metadata
    df = pd.read_csv(file_name)


    # Filter metadata to retrieve only files desired
    filtered_df = getsplit.filter_df(df)

    # print("filterd df is empty {}".format(filtered_df))

    # Train test split
    X_train, X_test, y_train, y_test = getsplit.split_people(filtered_df)
    print(len(X_train) + len(X_test))

    # Get statistics
    train_count = Counter(y_train)
    test_count = Counter(y_test)

    print("Entering main")


    acc_to_beat = test_count.most_common(1)[0][1] / float(np.sum(list(test_count.values())))

    # To categorical
    # y_train = to_categorical(y_train)
    # y_test = to_categorical(y_test)

    y_train, y_test = to_categorical_v2(y_train, y_test)

    print(y_train[0])
    print(y_test[0])

    # Get resampled wav files using multiprocessing
    if DEBUG:
        print('Loading MFCC CSVs....')
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    X_train = pool.map(get_file, X_train)
    X_test = pool.map(get_file, X_test)

    for i in X_train:
        librosa.util.normalize(i)
    for i in X_test:
        librosa.util.normalize(i)

    # Create segments from MFCCs
    X_train, y_train = make_segments(X_train, y_train)
    X_validation, y_validation = make_segments(X_test, y_test)
    # X_validation, y_validation = make_segments(X_test, y_train)

    # Attempt to replace this with a new version that uses same y_train for both

    # Randomize training segments
    # X_train, _, y_train, _ = train_test_split(X_train, y_train, test_size=0.0)
    X_train, y_train = shuffle(X_train, y_train, random_state=230)

    # print("y_train shape:", len(y_train[0]))
    # print("y_train:", y_train[0])
    # print("y_validation shape:", len(y_validation[0]))
    # print("y_validation:", y_validation[0])

    # Train model
    model = train_model(np.array(X_train), np.array(y_train), np.array(X_validation),np.array(y_validation))

    # Make predictions on full X_test MFCCs
    y_predicted = accuracy.predict_class_all(create_segmented_mfccs(X_test), model)

    # Print statistics
    print('Training samples:', train_count)
    print('Testing samples:', test_count)
    print('Accuracy to beat:', acc_to_beat)
    print('Confusion matrix of total samples:\n', np.sum(accuracy.confusion_matrix(y_predicted, y_test),axis=1))
    # print('Confusion matrix of total samples:\n', np.sum(accuracy.confusion_matrix(y_predicted, y_train),axis=1))
    print('Confusion matrix:\n',accuracy.confusion_matrix(y_predicted, y_test))
    # print('Confusion matrix:\n',accuracy.confusion_matrix(y_predicted, y_train))
    print('Accuracy:', accuracy.get_accuracy(y_predicted,y_test))
    # print('Accuracy:', accuracy.get_accuracy(y_predicted,y_train))
    print('F1 Score:', accuracy.get_f1_score(y_predicted, y_test))
    print('Micro F1 Score:', accuracy.get_micro_f1_score(y_predicted,y_test))

    # Save model
    save_model(model, model_filename)
