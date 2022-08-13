import time
import tqdm
import os 
import sys
sys.path.append(os.getcwd())

from data_processing import CompetitionData
import config as cfg
import gather 






if __name__ == '__main__':

    data = CompetitionData()   
    data.update_matches()
    data.save_files_to_results()
