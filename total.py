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
    
    print("+--------+----------+-----------------+")
    print("| {:^6s} | {:^6s} |{:^17s}|".format("Upload", "Download", "Name"))
    print("+--------+----------+-----------------+")
    for base, up, down in sorted(res, key=lambda t: t[1]+t[2], reverse=True)[:15]:
        print(f"|{up/1000:^6.2f}G |  {down/1000:^6.2f}G | {base:<16s}|")
    print("+--------+----------+-----------------+")


if __name__ == '__main__':
    main()
