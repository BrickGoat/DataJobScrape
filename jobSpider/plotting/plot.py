import matplotlib.pyplot as plt
import pandas as pd

def plotSalaries():
    cols = ["Location", "Schedule", "Type"]
    for col in cols:
        df = pd.read_csv('job.csv')
        df = df.dropna(subset=["Salary"])
        df[col] = df[[col]].fillna("NA")
        if col == "Location":
            df[col] = df[col].apply(lambda x: x.split("/"))
            df = df.explode(col)
        xy = df.groupby(by=col).mean()
        plt.clf()
        plt.bar(xy.index, xy.Salary)
        plt.title(f"Average Salary by {col}")
        plt.xticks(rotation = 20)
        plt.savefig(f"Salary_by_{col}.png")

def plotLangs():
    df = pd.read_csv('job.csv')
    df[['Requirements']] = df[['Requirements']].fillna("NA")
    df.iloc[:,3] = df[['Requirements']].apply(lambda x: x.Requirements.split("/"), axis=1)
    df = df.explode("Requirements")
    xy = df.groupby(by="Requirements").size()
    plt.clf()
    plt.bar(list(xy.index), xy)
    plt.title(f"Counts of Requirement terms")
    plt.xticks(rotation = 20)
    plt.savefig("terms.png")

plotSalaries()
plotLangs()