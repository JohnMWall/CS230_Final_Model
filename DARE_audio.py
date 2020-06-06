import tqdm
import pandas as pd
import urllib.request
import os
import sys
import requests
import time
import re
from pydub import AudioSegment
from bs4 import BeautifulSoup
import ipdb

class GetAudio:

    def __init__(self, csv_filepath, output_csv_filepath, destination_folder= 'audioDARE/', wait= 1.5, debug=False ):
        '''
        Initializes GetAudio class object
        :param destination_folder (str): Folder where audio files will be saved
        :param wait (float): Length (in seconds) between web requests
        :param debug (bool): Outputs status indicators to console when True
        '''
        self.csv_filepath = csv_filepath
        self.output_csv_filepath = output_csv_filepath
        self.audio_df = pd.read_csv(csv_filepath)
        self.urlRootPage = 'https://asset.library.wisc.edu/1711.dl/'
        self.destination_folder = destination_folder
        self.wait = wait
        self.debug = False
        self.checkPrint = True

    def downloadfile(self, name, url, speakerID):
        if url != 'None':
            tmp_name = "tmp.mp4"
            r=requests.get(url)
            print("****Connected****")
            with open(tmp_name,'wb') as f:
                print(url)
                print("Donloading.....")
                for chunk in r.iter_content(chunk_size=255): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                print("Done")

            sound = AudioSegment.from_file(tmp_name, 'mp4')
            sound.export(name, format="wav")
            print("Converted to WAV")
            os.remove(tmp_name)
        else:
            print('Skipping: {}'.format(speakerID))

    def get_htmls(self, urls):
        '''
        Retrieves html in text form from ROOT_URL
        :param urls (list): List of urls from which to retrieve html
        :return (list): list of HTML strings
        '''
        htmls = []
        for url in urls:
            if self.checkPrint:
                print('downloading from {}'.format(url))
            htmls.append(requests.get(url).text)
            time.sleep(self.wait)

        return(htmls)


    def check_path(self):
        '''
        Checks if self.destination_folder exists. If not, a folder called self.destination_folder is created
        '''
        if not os.path.exists(self.destination_folder):
            if self.debug:
                print('{} does not exist, creating'.format(self.destination_folder))
            os.makedirs(self.destination_folder)

    def get_audio(self):
        '''
        Retrieves all audio files from 'language_num' column of self.audio_df
        If audio file already exists, move on to the next
        :return (int): Number of audio files downloaded
        '''

        self.check_path()
        speakerPageURL = self.audio_df['href'].values.tolist()
        speakerID = self.audio_df['ID'].values.tolist()
        htmls = self.get_htmls(speakerPageURL)
        bss = [BeautifulSoup(html,'html.parser') for html in htmls]
        samples = []
        indexCount = 0
        for bs in bss:
            row = []
            row.append(speakerPageURL[indexCount])
            row.append(speakerID[indexCount])
            #must first find Arthur the Rat
            flagArthur = False #make sure that there is an Arthur the Rat recording
            for link in bs.find_all('li'):

                name = link.find('p', class_= "acaption")
                if name is None: 
                    continue
                name = "".join(name.strings)
                #print(name)

                if name != 'Arthur the Rat':
                    continue

                audioName = link.find('source', type= "audio/mp4").get('src')
                #print(audioName)

                if audioName.startswith(self.urlRootPage): #arthur the rat is listed first if it is there
                    flagArthur = True
                    row.append('Yes')
                    row.append(audioName)
                    break

            if not flagArthur:
                row.append('No')
                row.append('None')

            indexCount += 1
            samples.append(row)
        allInfoDF = pd.DataFrame(samples)
        #print(allInfoDF)

        df = pd.DataFrame(speakerPageURL, columns=['href'])

        df['ID'] = allInfoDF.iloc[:,1]
        df['Arthur the Rat'] = allInfoDF.iloc[:,2]
        df['mp4 URL'] = allInfoDF.iloc[:,3]

        df.to_csv(self.output_csv_filepath,index=False)

        counter = 0

        for speaker in tqdm.tqdm(df['mp4 URL']):
            if not os.path.exists(self.destination_folder +'{}.wav'.format(speakerID[counter])):
                if speaker != 'None':
                    (filename, headers) = urllib.request.urlretrieve(speaker) #need to change this
                    self.downloadfile(self.destination_folder + "{}.wav".format(speakerID[counter]), speaker, speakerID[counter])
                counter += 1

        return counter

if __name__ == '__main__':
    '''
    Example console command
    python DARE_audio.py audio_metadata.csv outPutFile.csv
    '''
    input_csv_file = sys.argv[1]
    output_csv_file = sys.argv[2]
    ga = GetAudio(csv_filepath=input_csv_file, output_csv_filepath= output_csv_file)
    ga.get_audio()