import pickle
import os
import pandas as pd

# Select pickles 
def main():
    os.system('cls||clear')

    # Change cwd to the pickles folder
    os.chdir('./Raw Data/Knox_Pickles')
    cwd = os.getcwd()

    output_dict = {
        "AFG": {
            "Prior": pd.read_pickle('Afghanistan_priortohmi_200_permutations'),
            "During": pd.read_pickle('Afghanistan_duringhmi_200_permutations'),
            "After": pd.read_pickle('Afghanistan_afterhmi_200_permutations')
        },
        "IRQ": {
            "Prior": pd.read_pickle('Afghanistan_priortohmi_200_permutations'),
            "During": pd.read_pickle('Afghanistan_duringhmi_200_permutations'),
            "After": pd.read_pickle('Afghanistan_afterhmi_200_permutations')
        },
        "SOM": {
            "Prior": pd.read_pickle('Afghanistan_priortohmi_200_permutations'),
            "During": pd.read_pickle('Afghanistan_duringhmi_200_permutations'),
            "After": pd.read_pickle('Afghanistan_afterhmi_200_permutations')
        },
        "LKA": {
            "Prior": pd.read_pickle('Afghanistan_priortohmi_200_permutations'),
            "During": pd.read_pickle('Afghanistan_duringhmi_200_permutations'),
            "After": pd.read_pickle('Afghanistan_afterhmi_200_permutations')
        }
    }

    with open('knox_tables.pickle', 'wb') as handle:
        pickle.dump(output_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
if __name__ == "__main__":
    main()


