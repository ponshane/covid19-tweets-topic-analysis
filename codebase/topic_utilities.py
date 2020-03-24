import re
import matplotlib.pyplot as plt

def make_perplexity_plots(log_path, output_path):
    # https://stackoverflow.com/questions/37570696/how-to-monitor-convergence-of-gensim-lda-model

    p = re.compile("(-*\d+\.\d+) per-word .* (\d+\.\d+) perplexity")
    matches = [p.findall(line) for line in open(log_path)]

    # not every line has perplexity information
    matches = [m for m in matches if len(m) > 0]

    # pick match tuple "There is only one match in one line"
    tuples = [t[0] for t in matches]

    # furthermore to extract likelihood and perplexity
    liklihood = [float(t[0]) for t in tuples]
    perplexity = [float(t[1]) for t in tuples]

    iters = list(range(0,len(tuples)))
    plt.plot(iters,perplexity,c="black")
    plt.ylabel("perplexity")
    plt.xlabel("iteration")
    plt.title("Topic Model Convergence")
    plt.grid()
    plt.savefig(output_path)
    plt.close()