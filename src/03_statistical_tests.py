"""Hypothesis tests on inflation-adjusted movie revenue.

Tests 1-3 are taken from the project's final presentation. Test 4 was corrected
after the project: the original version passed a single-row table to
chi2_contingency, which always returns chi2 = 0 and p = 1. It now uses a
chi-square goodness-of-fit test. The corrected test has not been re-run.

Run 01_data_preparation.py first.
"""

import pandas as pd
from scipy.stats import chisquare, f_oneway, ttest_ind

df = pd.read_csv("data/final_integrated_dataset.csv")
results = {}

# ---- 1. ANOVA: Revenue Across Genres ----
grouped = df.dropna(subset=["primary_genre", "revenue_constant_2024"])
genre_groups = [g["revenue_constant_2024"].values for _, g in grouped.groupby("primary_genre")]
anova_stat, anova_p = f_oneway(*genre_groups)
results["genre_revenue_anova"] = {
    "statistic": anova_stat,
    "p_value": anova_p,
}

# ---- 2. t-test: 1970s vs 1980s ----
df_70s = df[df["release_year"].between(1970, 1979)]["revenue_constant_2024"].dropna()
df_80s = df[df["release_year"].between(1980, 1989)]["revenue_constant_2024"].dropna()

t_stat, t_p = ttest_ind(df_70s, df_80s, equal_var=False)
results["70s_vs_80s"] = {
    "statistic": t_stat,
    "p_value": t_p,
}

# ---- 3. t-test: Eastwood vs Scorsese ----
eastwood_rev = df[df["director"] == "Clint Eastwood"]["revenue_constant_2024"].dropna()
scorsese_rev = df[df["director"] == "Martin Scorsese"]["revenue_constant_2024"].dropna()

t2_stat, t2_p = ttest_ind(eastwood_rev, scorsese_rev, equal_var=False)
results["eastwood_vs_scorsese"] = {
    "statistic": t2_stat,
    "p_value": t2_p,
}

# ---- 4. Chi-square: Summer vs Winter release counts (corrected) ----
# Goodness-of-fit test against equal expected counts for the two seasons.
summer = df[df["release_season"] == "Summer"]
winter = df[df["release_season"] == "Winter"]
chi2, p = chisquare([len(summer), len(winter)])
results["summer_vs_winter"] = {
    "statistic": chi2,
    "p_value": p,
}

# ---- Print Results ----
print("\nSTATISTICAL TEST RESULTS:")
print(pd.DataFrame(results).T)

# ---- Save Results ----
pd.DataFrame(results).T.to_csv("data/statistical_test_results.csv", index=True)
