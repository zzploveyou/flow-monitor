import pandas as pd
import numpy as np
from glob import glob
import os


def main():
    res = set()
    for filename in glob(os.path.join("flow", "*.csv")):
        base = os.path.splitext(os.path.basename(filename))[0]
        df = pd.read_csv(filename, index_col=0, header=None)
        data = np.array([[int(i[:-1]), int(j[:-1])] for i, j in df.values])
        up, down = data.sum(axis=0)
        res.add((base, up, down))
    for base, up, down in sorted(res, key=lambda t: t[1]+t[2], reverse=True):
        print(f"{up/1000:2.2f}G {down/1000:2.2f}G {base}")


if __name__ == '__main__':
    main()
