import pickle
import os
import pandas as pd

# Select pickles 
def main():
    os.system('cls||clear')

    # Change cwd to the pickles folder
    os.chdir('./Raw Data/Knox_Pickles')

    output_dict = {
        "AFG": {
            "Highres": {
                "Prior": pd.read_pickle('Afghanistan_priortohmi_hr_200_permutations'),
                "During": pd.read_pickle('Afghanistan_duringhmi_hr_200_permutations'),
                "After": pd.read_pickle('Afghanistan_afterhmi_hr_200_permutations')
            },
            "Lowres": {
                "Prior": pd.read_pickle('Afghanistan_priortohmi_200_permutations'),
                "During": pd.read_pickle('Afghanistan_duringhmi_200_permutations'),
                "After": pd.read_pickle('Afghanistan_afterhmi_200_permutations')
            }
            
        },
        "IRQ": {
            "Highres": {
                "Prior": pd.read_pickle('Iraq_priortohmi_200_permutations'),
                "During": pd.read_pickle('Iraq_duringhmi_200_permutations'),
                "After": None
            },
            "Lowres": {
                "Prior": pd.read_pickle('Iraq_priortohmi_200_permutations'),
                "During": pd.read_pickle('Iraq_duringhmi_200_permutations'),
                "After": None
            }

        },
        "SOM": {
            "Highres": {
                "Prior": None,
                "During": pd.read_pickle('Somalia_duringhmi_200_permutations'),
                "After": None
            },
            "Lowres": {
                "Prior": None,
                "During": pd.read_pickle('Somalia_duringhmi_200_permutations'),
                "After": None
            }
        },
        "LKA": {
            "Highres": {
                "Prior": None,
                "During": None,
                "After": pd.read_pickle('SriLanka_afterhmi_200_permutations')
            },
            "Lowres": {
                "Prior": None,
                "During": None,
                "After": pd.read_pickle('SriLanka_afterhmi_200_permutations')
            }
        }
    }

    with open('knox_tables_v3.pickle', 'wb') as handle:
        pickle.dump(output_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
if __name__ == "__main__":
    main()


