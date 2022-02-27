import pandas as pd




if __name__ == '__main__':
    result_df = pd.read_csv('./temp/results_example.csv')
    points_df = pd.read_csv('./2022_Voorjaar/points.csv')
    teams_df = pd.read_csv('./2022_Voorjaar/teams.csv')
    
    print(result_df.head())