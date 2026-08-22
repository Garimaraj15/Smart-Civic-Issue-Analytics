"""
Geospatial Hotspot & Cluster Detection Module.
Uses spatial density clustering (DBSCAN / K-Means) on civic coordinates
to discover persistent infrastructure failure corridors and chronic complaint clusters.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from src.core.logger import get_logger

logger = get_logger("ClusterAnalyzer")


class GeospatialClusterAnalyzer:
    """Discovers geographic clusters and spatial hotspots in complaints."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def find_hotspots(
        self, eps_km: float = 1.5, min_samples: int = 8
    ) -> pd.DataFrame:
        """
        Applies DBSCAN spatial clustering using Haversine metric.
        eps_km: maximum distance in kilometers to consider two complaints neighbors.
        min_samples: minimum complaints in a cluster to be considered a persistent hotspot.
        """
        valid_coords = self.df[
            self.df["Latitude"].notna() & self.df["Longitude"].notna()
        ].copy()

        if len(valid_coords) == 0:
            logger.warning("No valid coordinates found for spatial clustering.")
            return self.df

        # Convert lat/lon to radians for Haversine distance
        coords_rad = np.radians(valid_coords[["Latitude", "Longitude"]].values)
        kms_per_radian = 6371.0088
        epsilon = eps_km / kms_per_radian

        db = DBSCAN(
            eps=epsilon,
            min_samples=min_samples,
            metric="haversine",
            algorithm="ball_tree",
        )
        cluster_labels = db.fit_predict(coords_rad)

        valid_coords["Hotspot_Cluster_ID"] = cluster_labels
        valid_coords["Is_Hotspot"] = valid_coords["Hotspot_Cluster_ID"].apply(
            lambda x: "Hotspot Cluster" if x != -1 else "Dispersed Incident"
        )

        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        logger.info(
            f"DBSCAN Clustering complete: Found {n_clusters} persistent hotspot zones ({n_noise} dispersed tickets)."
        )

        return valid_coords

    def summarize_clusters(self, clustered_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Summarizes top hotspot clusters by issue types and severity."""
        hotspots = clustered_df[clustered_df["Hotspot_Cluster_ID"] != -1]
        summary = []

        for cluster_id, group in hotspots.groupby("Hotspot_Cluster_ID"):
            top_issues = group["Issue_Type"].value_counts().head(2).to_dict()
            top_areas = group["Area"].value_counts().head(2).index.tolist()
            avg_rating = group["Citizen_Rating"].dropna().mean()
            sla_breach_pct = (
                (group["SLA_Status"] == "SLA Breached").sum() / len(group)
            ) * 100

            summary.append(
                {
                    "cluster_id": int(cluster_id),
                    "total_complaints": len(group),
                    "center_lat": round(float(group["Latitude"].mean()), 6),
                    "center_lon": round(float(group["Longitude"].mean()), 6),
                    "primary_areas": ", ".join(top_areas),
                    "primary_issues": top_issues,
                    "avg_citizen_rating": round(float(avg_rating), 2) if not np.isnan(avg_rating) else "N/A",
                    "sla_breach_rate_pct": round(float(sla_breach_pct), 1),
                }
            )

        summary = sorted(summary, key=lambda x: x["total_complaints"], reverse=True)
        return summary
