"""Exploratory plots for the integrated movie dataset.

Taken from the project's final presentation. Run 01_data_preparation.py first.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

df = pd.read_csv("data/final_integrated_dataset.csv")
os.makedirs("figures", exist_ok=True)

# Movies Released by Year
df["release_year"].value_counts().sort_index().plot(figsize=(10, 4))
plt.title("Movies Released by Year")
plt.tight_layout()
plt.savefig("figures/eda_movies_by_year.png")
plt.close()

# Log Revenue Distribution
plt.figure(figsize=(8, 5))
np.log1p(df["revenue_constant_2024"]).hist(bins=40)
plt.title("Log Revenue Distribution")
plt.savefig("figures/eda_log_revenue.png")
plt.close()

# Revenue vs Budget (Scatterplot)
plt.figure(figsize=(8, 6))
plt.scatter(df["budget_constant_2024"], df["revenue_constant_2024"], alpha=0.4)
plt.xlabel("Budget")
plt.ylabel("Revenue")
plt.title("Revenue vs Budget")
plt.tight_layout()
plt.savefig("figures/eda_revenue_vs_budget.png")
plt.close()

# Revenue vs Genre (Boxplot)
genre_counts = df["primary_genre"].value_counts()
top_genres = genre_counts[genre_counts > 50].index
subset = df[df["primary_genre"].isin(top_genres)]
plt.figure()
sns.boxplot(data=subset, x="primary_genre", y="revenue_constant_2024")
plt.title("Revenue by Primary Genre")
plt.xticks(rotation=45)
plt.savefig("figures/eda_revenue_by_genre.png", dpi=150, bbox_inches="tight")
plt.close()
