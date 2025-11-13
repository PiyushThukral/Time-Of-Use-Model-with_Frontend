import pandas as pd
import kmedoids
from sklearn.metrics import pairwise_distances
import numpy as np
import numpy as np
import random

np.random.seed(42)
random.seed(42)

from pages import make_monthly_cons
#m1 = pd.read_csv(r"C:\Time-of-Use-Model-with-Frontend\for_clustering_VM\Month_1_consumer_df.csv")


class ConsumerClusterer:
    """
    Encapsulates the workflow for:
      1. Filtering consumers by total consumption (> 120).
      2. Computing median hourly profiles per consumer.
      3. Clustering each category (and, if needed, load‐bins within categories) using K‐Medoids.
      4. Extracting medoid profiles and the full set of clustered profiles.

    After calling `fit()`, the following attributes become available:
      - clustered_data: DataFrame with every consumer assigned a 'Cluster' label.
      - medoid_data:     DataFrame containing one row per medoid (per cluster),
                         including its hourly profile and static info.
    """

    def __init__(self, raw_df: pd.DataFrame, group_list, distance_metric, opt_flag, num_clusters, consumption_cols = None, time_blocks = None):
    #def __init__(self, raw_df: pd.DataFrame, group_list, distance_metric):
        """
        Parameters:
            raw_df: pd.DataFrame
                The original DataFrame (which we refer to as `m1`), containing at least:
                  - Date
                  - Consumer No
                  - Meter No
                  - Sanctioned_Load_KW
                  - Category
                  - MeterPhase_Name
                  - total_monthly_consumption
                  - Consumption_Hr_1 .. Consumption_Hr_24
        """
        self.raw_df = raw_df.copy()  # keep a copy of the input
        self.clustered_data = None
        self.medoid_data = None
        self.distance_metric = distance_metric
        self.opt_flag = opt_flag
        self.num_cluster = num_clusters

        self.group_list = group_list
        # Define which columns are “static” vs. “hourly‐consumption”


        self.relevant_cols = [
            'Date', 'Consumer No', 'Sanctioned_Load_KW',
            'Category','total_monthly_consumption'
        ]


        if consumption_cols is None or len(consumption_cols) == 0:
            self.consumption_cols = [f'Consumption_Hr_{i}' for i in range(time_blocks['first'], time_blocks['last'] + 1)]
        else:
            self.consumption_cols = consumption_cols

    def _flag_consumption(self):
        """
        Step 1: Filter consumers whose total_monthly_consumption > 120.
        Also removes rows where more than 2 values in consumption columns are 0.0.
        Adds a 'to_opt_flag' column and returns sub_data.
        """


        df = self.raw_df.copy()

        # Flag based on total consumption
        df['to_opt_flag'] = df['total_monthly_consumption'].apply(lambda x: "Yes" if x > 120 else "No")
        zero_counts = (df[self.consumption_cols] == 0.0).sum(axis=1)

        # Keep only rows with <= 2 zeros
        sub_data = df[zero_counts <= 2].copy()

        if "monthly_consumption" in self.group_list:

            sub_data = sub_data[sub_data['to_opt_flag'] == "Yes"].copy()
            return sub_data

        else:

            return sub_data


    def _compute_median_profiles(self, sub_data: pd.DataFrame):
        """
        Step 2: For sub_data (only flagged rows), compute:
          - median hourly consumption profile per 'Consumer No'
          - static info (Sanctioned_Load_KW, Category)
        Returns a merged DataFrame `final_df` with one row per Consumer No.
        """
        # (A) Compute median of each hourly column for every consumer
        median_profiles = (
            sub_data
            .groupby('Consumer No')[self.consumption_cols]
            .median()
            .reset_index()
        )

        # (B) Pull static info (assuming they are constant per Consumer No)
        static_info = (
            sub_data
            .groupby('Consumer No')[['Sanctioned_Load_KW', 'Category', 'total_monthly_consumption']]
            .first()
            .reset_index()
        )

        # (C) Merge them so final_df has:
        #     [Consumer No, Consumption_Hr_1 ... Consumption_Hr_24, Sanctioned_Load_KW, Category]
        final_df = pd.merge(median_profiles, static_info, on='Consumer No', how='left')
        return final_df


    def _cluster_per_category(self, final_df: pd.DataFrame):
        """
        Step 3: For each unique Category in final_df, run one of two paths:
          - If there are ≤ 5 consumers, assign each its own cluster (1..n).
          - If > 5 consumers, check range of Sanctioned_Load_KW:
              • If range = 0 → cluster all 5 clusters via K‐Medoids on hourly profiles.
              • If range > 0 → first bin into 3 load‐bins, then cluster each bin (5 clusters each).
        At the end, build:
          - self.clustered_data: concatenation of all clustered sub‐DataFrames
          - self.medoid_data:     concatenation of all medoid profiles (one per cluster)
        """
        all_clustered = []
        all_medoid_profiles = []

        unique_categories = None
        if 'Category' in self.group_list:
            unique_categories = final_df['Category'].unique()
        else:
            unique_categories = ['all']

        for idx,cat in enumerate(unique_categories):

            if cat != 'all':
                cat_df = final_df[final_df['Category'] == cat].copy()
            else:
                cat_df = final_df.copy()

            # (1) If ≤ 10 rows, just assign cluster labels 1..n
            if len(cat_df) <= 10:
                cat_df['load_bin'] = 'No Clustering'
                cat_df['consumption_bin'] = 'No Clustering'
                cluster_label = list(range(1, len(cat_df) + 1))
                clusters = [x + idx for x in cluster_label]
                cat_df['Cluster'] = clusters

                all_clustered.append(cat_df)

                # In this “small” case, every consumer is its own "medoid"
                all_medoid_profiles.append(cat_df)

                continue

            # Otherwise, check sanctioned_load range
            load_min = cat_df['Sanctioned_Load_KW'].min()
            load_max = cat_df['Sanctioned_Load_KW'].max()
            bin_range = load_max - load_min

            # (2) If all loads identical → cluster entire category as 5 clusters
            if bin_range == 0:
                X = cat_df[self.consumption_cols].values
                X_scaled = []

                for cons in range(len(X)):
                    row = X[cons]
                    row_mean = np.mean(row)
                    row_std = np.std(row)

                    # Avoid division by zero
                    if row_std == 0:
                        scaled_row = row  # or np.zeros_like(row) if you want zeroed output
                    else:
                        scaled_row = (row - row_mean) / row_std

                    X_scaled.append(scaled_row)

                # Convert list of arrays to a NumPy array
                X_Scaled = np.array(X_scaled)
                dist_matrix = pairwise_distances(X_Scaled, metric=self.distance_metric)

                len_x = len(X)

                if len_x - 10 > 10:
                    KMAX = 10
                else:
                    KMAX = len_x//2

                kmin, kmax = 3, KMAX
                #fp = kmedoids.dynmsc(dist_matrix, kmax, kmin)

                fp = None
                if self.opt_flag == "yes" or self.num_cluster is None:
                    fp = kmedoids.dynmsc(dist_matrix, kmax, kmin)


                else:
                    num = int(self.num_cluster)
                    fp = kmedoids.fasterpam(dist_matrix, num)

                cat_df['Cluster'] = fp.labels
                all_clustered.append(cat_df)


                # Extract medoid rows
                medoid_profiles = cat_df.iloc[fp.medoids][
                    ['Consumer No', 'Sanctioned_Load_KW', 'Category', 'Cluster'] + self.consumption_cols
                ]
                medoid_profiles['load_bin'] = 'Bin Range 0'
                medoid_profiles['consumption_bin'] = 'Bin Range 0'
                all_medoid_profiles.append(medoid_profiles)
                continue

            if 'Sanctioned_Load_KW' in self.group_list:
                #bin_edges = [0, 2.5, 5, 10, 15, 20, 25, 30, np.inf]
                #bin_labels = ['0-2.5', '2.5-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30+']

                unique_vals = cat_df['Sanctioned_Load_KW'].nunique()
                quantiles = min(unique_vals, 2)

                if quantiles > 1:

                    # Preview bin edges
                    _, bins = pd.qcut(
                        cat_df['Sanctioned_Load_KW'],
                        q=quantiles,
                        retbins=True,
                        duplicates='drop'
                    )

                    actual_bins = len(bins) - 1
                    bin_labels = [f'Q{i + 1}' for i in range(actual_bins)]

                    cat_df['load_bin'] = pd.qcut(
                        cat_df['Sanctioned_Load_KW'],
                        q=quantiles,
                        labels=bin_labels,
                        duplicates='drop'
                    )

                else:
                    cat_df['load_bin'] = 'no_sanctioned_bin'
                    bin_labels = ['no_sanctioned_bin']

            else:

                bin_labels = ['no_sanctioned_bin']
                cat_df['load_bin'] = 'no_sanctioned_bin'

            if 'monthly_consumption' in self.group_list:
                #consumption_bin = [120, 240, 340, 500, 750, 1000, 1500, np.inf]
                #cons_labels = ['120-240', '240-340', '340-500', '500-750', '750-1000', '1000-1500', '1500+']
                unique_vals = cat_df['total_monthly_consumption'].nunique()
                quantiles = min(unique_vals, 2)


                if quantiles > 1:
                    # Perform qcut with duplicate bin edges dropped
                    cat_df['consumption_bin'] = pd.qcut(
                        cat_df['total_monthly_consumption'],
                        q=quantiles,
                        labels=False,  # Temporarily use integers so we can get actual bin count
                        duplicates='drop'
                    )

                    # Get actual number of bins after dropping duplicates
                    actual_bins = cat_df['consumption_bin'].nunique()

                    # Assign proper labels
                    cons_labels = [f'C{i + 1}' for i in range(actual_bins)]

                    # Reapply qcut with correct labels
                    cat_df['consumption_bin'] = pd.qcut(
                        cat_df['total_monthly_consumption'],
                        q=actual_bins,
                        labels=cons_labels,
                        duplicates='drop'
                    )
                else:
                    cons_labels = ['no_cons_label']
                    cat_df['consumption_bin'] = 'no_cons_label'

            else:

                cons_labels = ['no_cons_label']
                cat_df['consumption_bin'] = 'no_cons_label'


            for lb in bin_labels:
                for cb in cons_labels:

                    bin_df = cat_df[(cat_df['load_bin'] == lb) & (cat_df['consumption_bin'] == cb)].copy()
                    if bin_df.empty:
                        continue

                    # If a bin has ≤ 5 rows, assign each a unique cluster number within that bin
                    if len(bin_df) <= 10:
                        cluster_label = list(range(1, len(bin_df) + 1))
                        clusters = [x + idx for x in cluster_label]
                        bin_df['Cluster'] = clusters
                        all_clustered.append(bin_df)
                        all_medoid_profiles.append(bin_df)
                        continue

                    # Otherwise, run K‐Medoids for 5 clusters on this bin
                    X = bin_df[self.consumption_cols].values
                    X_scaled = []
                    for cons in range(len(X)):
                        row = X[cons]
                        row_mean = np.mean(row)
                        row_std = np.std(row)

                        # Avoid division by zero
                        if row_std == 0:
                            scaled_row = row  # or np.zeros_like(row) if you want zeroed output
                        else:
                            scaled_row = (row - row_mean) / row_std

                        X_scaled.append(scaled_row)

                    # Convert list of arrays to a NumPy array
                    X_Scaled = np.array(X_scaled)
                    dist_matrix = pairwise_distances(X_Scaled, metric=self.distance_metric)
                    kmin, kmax = 3,10
                    #fp = kmedoids.dynmsc(dist_matrix, kmax, kmin)

                    len_x = len(X_Scaled)
                    if len_x - 10 > 10:
                        KMAX = 10
                    else:
                        KMAX = len_x // 2

                    kmin, kmax = 3, KMAX

                    fp = None

                    if self.opt_flag == "yes" or self.num_cluster is None:
                        fp = kmedoids.dynmsc(dist_matrix, kmax, kmin)


                    else:
                        num = int(self.num_cluster)
                        fp = kmedoids.fasterpam(dist_matrix, num)


                    bin_df['Cluster'] = fp.labels
                    all_clustered.append(bin_df)
                    medoid_profiles = bin_df.iloc[fp.medoids]
                    all_medoid_profiles.append(medoid_profiles)

        # Concatenate all pieces
        self.clustered_data = pd.concat(all_clustered, axis=0).reset_index(drop=True)
        # Subset the clustered data to keep only necessary columns
        cluster_info = self.clustered_data[
            ['Consumer No', 'Cluster', 'Category', 'Sanctioned_Load_KW']].drop_duplicates()

        # Merge cluster labels and associated info onto raw_df using Consumer No
        self.reformed_df = pd.merge(
            self.raw_df,
            cluster_info,
            on='Consumer No',
            how='left'
        )

        self.medoid_data = pd.concat(all_medoid_profiles, axis=0).reset_index(drop=True)


    def fit(self):
        """
        Runs the entire pipeline:
          1. Filter and flag consumption > 120.
          2. Compute median profiles + static info.
          3. Cluster per category (and per load‐bin if needed).
        After this, `self.clustered_data` and `self.medoid_data` are populated.
        """
        # Step 1: Flag and filter
        sub_data = self._flag_consumption()

        # Step 2: Build one‐row‐per‐consumer with median profiles + static fields
        final_df = self._compute_median_profiles(sub_data)

        # Step 3: Cluster per category
        self._cluster_per_category(final_df)



"""
clusterer = ConsumerClusterer(raw_df=m1,group_list= ['Sanctioned_Load_KW'])
clusterer.fit()
final_clustered_data = clusterer.clustered_data
final_medoid_data = clusterer.medoid_data
transformed_data = clusterer.reformed_df



# ============================
# Example usage:
# ============================

clusterer = ConsumerClusterer(raw_df=m1)
clusterer.fit()

final_clustered_data = clusterer.clustered_data
final_medoid_data = clusterer.medoid_data
transformed_data = clusterer.reformed_df

#final_clustered_data.to_csv("all_clustered_results.csv")
#final_medoid_data.to_csv("medoid.csv")
#transformed_data.to_csv("reformed_df.csv")




"""