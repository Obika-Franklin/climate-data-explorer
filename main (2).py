import pandas as pd
import numpy as np

# ---------------- AGENTS ---------------- #

class DataLoader:
    def run(self, file):
        df = pd.read_csv(file)

        # Try to standardize columns
        df.columns = [c.strip() for c in df.columns]

        # Convert date if exists
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col])

        # Fill missing values
        df = df.fillna(method="ffill")

        return df


class TrendAnalyst:
    def run(self, df):
        numeric_cols = df.select_dtypes(include=np.number).columns

        trends = {}
        for col in numeric_cols:
            trend = df[col].iloc[-1] - df[col].iloc[0]
            trends[col] = float(trend)

        return trends


class AnomalyDetector:
    def run(self, df):
        numeric_cols = df.select_dtypes(include=np.number).columns

        anomalies = {}

        for col in numeric_cols:
            series = df[col]
            z = (series - series.mean()) / series.std()
            anomaly_idx = list(df[np.abs(z) > 3].index)
            anomalies[col] = anomaly_idx

        return anomalies


class PolicyAdvisor:
    def run(self, trends, anomalies):
        recommendations = []

        for feature, trend in trends.items():
            if trend > 0:
                recommendations.append(f"{feature} is increasing. Monitor environmental impact.")
            else:
                recommendations.append(f"{feature} is stable/decreasing.")

        return {
            "trends": trends,
            "anomalies": anomalies,
            "recommendations": recommendations
        }


#  PIPELINE 

def run_pipeline(file):

    loader = DataLoader()
    analyst = TrendAnalyst()
    detector = AnomalyDetector()
    advisor = PolicyAdvisor()

    df = loader.run(file)
    trends = analyst.run(df)
    anomalies = detector.run(df)

    result = advisor.run(trends, anomalies)

    return df, result
