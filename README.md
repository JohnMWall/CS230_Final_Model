# CS230_Final_Model

A deep learning model is developed which can predict the native country on the basis of the spoken english accent

Overview:

Using audio samples from [The Speech Accent Archive] (http://accent.gmu.edu/), we wanted to show that a deep neural network can classify the countries of english residence of a speaker.

Dependencies:

Python 3.5 (https://www.python.org/download/releases/2.7/)
Keras (https://keras.io/)
Numpy (http://www.numpy.org/)
BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/)
Pydub (https://github.com/jiaaro/pydub)
Sklearn (http://scikit-learn.org/stable/)
Librosa (http://librosa.github.io/librosa/)
Data:

We started with the data from The Speech Accent Archive, a collection of more than 2400 audio samples from people for over 177 countries speaking the same English paragraph. The paragraph contains most of the consonants, vowels, and clusters of standard American English.

Model:

• Converted wav audio files into Mel Frequency Cepstral Coefficients graph.

• The MFCC was fed into a 2-Dimensional Convolutional Neural Network (CNN) to predict the native language class.

Challenges & Solutions:
• Computationally expensive: Uses only native english origin for a smaller subset of 645 speakers

• Small dataset: MFCCs were sliced into smaller segments. These smaller segments were fed into the neural network where predictions were made. Using an ensembling method, a majority vote was taken to predict the native language class.

Running Model:
├── src
├── accuracy.py ├── fromwebsite.py ├── getaudio.py ├── getsplit.py ├── trainmodel.py ├── models
├── cnn_model138.h5 ├── logs
├── events.out.tfevents.1506987325.ip-172-31-47-225 └── audio

Note- Run all the python files as described below on the terminal

Run getaudio.py to download audio files to the audio directory. All audio files listed in bio_metadata.csv will be downloaded. Use nativeenglish.csv for this model
Command: python getaudio.py nativeenglish.csv

To filter audio samples to feed into the CNN:
Edit the filter_df method in getsplit.py
This will filter audio files from the csv when calling trainmodel.py
To make predictions on audio files:
Run trainmodel.py to train the CNN
Command: python trainmodel.py nativeenglish.csv milestonemodel

Running trainmodel.py will save the trained model as milestonemodel.h5 in the model directory and output the results to the console.
This script will also save a TensorBoard log file into the logs directory.
####### To add/change performance metric calculations

Open accuracy.py
There you should see several functions such as confusion matrix, accuracy, and F1 score
Make the changes that you'd like, then make sure to add a line invoking the function in trainmodel.py
Note: Micro-F1 takes the F1 score as the dot product over all test classes as share_of_class_in_test_set * F1_score divided by the total number of non-zero test classes. This is because for certain distributions, classes will be included in the confusion matrix even though they don't appear in the test class, so needlessly detract from the F1 score.
Performance

With the inconsistent labels and smaller set of 645 speakers, the model was able to predict the correct country of english residence at around 73% accuracy when given a test sample from the 645 native english speakers.
