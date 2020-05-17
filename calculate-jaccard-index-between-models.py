import argparse

import numpy as np
import pandas as pd
import seaborn as sns; sns.set(rc={'figure.figsize':(10,10)})
import matplotlib.pyplot as plt

from codebase.topic_utilities import calculate_jaccard_matrix_between_models

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-tl', '--tag_list', type=str, nargs="+", required=True, dest="tag_list",
                        help='tag list, where each tag inside will be appended to suffix to get the file')
    parser.add_argument('-s', '--suffix', type=str, required=True, dest="suffix",
                        help='suffix string for locating summary file')  
    args = parser.parse_args()

    tag_list = args.tag_list
    suffix = args.suffix
    model_path = "./models/"
    figure_path = "./figures/"

    # using zip to create moving window: (elem1, elem2), (elem2, elem3), ...
    for model1, model2 in zip(tag_list[:-1], tag_list[1:]):
        m1 = pd.read_csv(f"{model_path}{model1}{suffix}")
        m2 = pd.read_csv(f"{model_path}{model2}{suffix}")
        m1_ws = m1.relevant_words.to_dict()
        m2_ws = m2.relevant_words.to_dict()

        jaccardMatrix = calculate_jaccard_matrix_between_models(m1_ws, m2_ws)
        
        plt.figure()
        sns.heatmap(jaccardMatrix)
        png_path = f"{figure_path}{model1}-{model2}-jac-mat.png"
        plt.savefig(png_path)
        
        print("*"*20)
        print(f"PNG is saved in {png_path}")
        # print indicator
        # pick_similar_topic_from_past(jaccardMatrix)
        print("topic_id,pre Topic,evolution score,topic label,relevant words")
        for idx in range(jaccardMatrix.shape[1]):
            maxv = np.max(jaccardMatrix[:,idx])
            max_idx = np.argmax(jaccardMatrix[:,idx])
            rel_words = m2_ws[idx]
            print(f'{idx},{max_idx},{maxv},,{rel_words}')
        print("*"*20)