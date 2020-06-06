from collections import Counter
import numpy as np

def predict_class_audio(MFCCs, model):
    '''
    Predict class based on MFCC samples
    :param MFCCs: Numpy array of MFCCs
    :param model: Trained model
    :return: Predicted class of MFCC segment group
    '''
    MFCCs = MFCCs.reshape(MFCCs.shape[0],MFCCs.shape[1],MFCCs.shape[2],1)
    y_predicted = model.predict_classes(MFCCs,verbose=0)
    return(Counter(list(y_predicted)).most_common(1)[0][0])


def predict_prob_class_audio(MFCCs, model):
    '''
    Predict class based on MFCC samples' probabilities
    :param MFCCs: Numpy array of MFCCs
    :param model: Trained model
    :return: Predicted class of MFCC segment group
    '''
    MFCCs = MFCCs.reshape(MFCCs.shape[0],MFCCs.shape[1],MFCCs.shape[2],1)
    y_predicted = model.predict_proba(MFCCs,verbose=0)
    return(np.argmax(np.sum(y_predicted,axis=0)))

def predict_class_all(X_train, model):
    '''
    :param X_train: List of segmented mfccs
    :param model: trained model
    :return: list of predictions
    '''
    predictions = []
    for mfcc in X_train:
        predictions.append(predict_class_audio(mfcc, model))
        # predictions.append(predict_prob_class_audio(mfcc, model))
    return predictions

def confusion_matrix(y_predicted,y_test):
    '''
    Create confusion matrix
    :param y_predicted: list of predictions
    :param y_test: numpy array of shape (len(y_test), number of classes). 1.'s at index of actual, otherwise 0.
    :return: numpy array. confusion matrix
    '''
    confusion_matrix = np.zeros((len(y_test[0]),len(y_test[0])),dtype=int )
    for index, predicted in enumerate(y_predicted):
        confusion_matrix[np.argmax(y_test[index])][predicted] += 1
    return(confusion_matrix)

def get_accuracy(y_predicted,y_test):
    '''
    Get accuracy
    :param y_predicted: numpy array of predictions
    :param y_test: numpy array of actual
    :return: accuracy
    '''
    c_matrix = confusion_matrix(y_predicted,y_test)
    return( np.sum(c_matrix.diagonal()) / float(np.sum(c_matrix)))

def get_f1_score(y_predicted, y_test):
    '''
    Get F1 Score
    '''

    c_matrix = confusion_matrix(y_predicted,y_test)
    precisions = np.sum(c_matrix, axis = 0)
    for i,p in enumerate(precisions):
        if p == 0:
            precisions[i] = 1
    # print("Precisions:", precisions)
    recalls = np.sum(c_matrix, axis = 1)
    for i,r in enumerate(recalls):
        if r == 0:
            recalls[i] = 1
    # print("Recalls:", recalls)
    trues = np.array([c_matrix[i,i] for i in range(c_matrix.shape[0])])
    # print("Trues:", trues)
    precisions = np.divide(trues, precisions)
    # print("Updated P's:", precisions)
    recalls = np.divide(trues, recalls)
    # print("Updated R's:", recalls)

    f1s = [(2*precisions[i]*recalls[i])/(precisions[i]+recalls[i]) if (precisions[i]+recalls[i]) > 0 else 0 for i in range(c_matrix.shape[0]) ]

    return np.sum(f1s) / c_matrix.shape[0]

def get_micro_f1_score(y_predicted, y_test): 
    '''
    Get F1 Score
    '''

    c_matrix = confusion_matrix(y_predicted,y_test)
    precisions = np.sum(c_matrix, axis = 0)
    for i,p in enumerate(precisions):
        if p == 0:
            precisions[i] = 1
    # print("Precisions:", precisions)
    recalls = np.sum(c_matrix, axis = 1)
    for i,r in enumerate(recalls):
        if r == 0:
            recalls[i] = 1
    # print("Recalls:", recalls)
    trues = np.array([c_matrix[i,i] for i in range(c_matrix.shape[0])])
    # print("Trues:", trues)
    precisions = np.divide(trues, precisions)
    # print("Updated P's:", precisions)
    recalls = np.divide(trues, recalls)
    # print("Updated R's:", recalls)

    fractions_of_trues = trues/np.sum(trues)

    f1s = [(2*precisions[i]*recalls[i])/(precisions[i]+recalls[i]) if (precisions[i]+recalls[i]) > 0 else 0 for i in range(c_matrix.shape[0]) ]

    # return np.dot(f1s, fractions_of_trues) / len(fractions_of_trues[fractions_of_trues != 0])
    return np.sum(f1s) / len(fractions_of_trues[fractions_of_trues != 0])
    
if __name__ == '__main__':
    pass


