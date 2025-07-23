import os
import json
import logging
import pandas as pd


logging.basicConfig(
    filename="analysis_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def load_run(csv_path):
    meta_path = csv_path.replace(".csv", ".meta.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Meta file missing for {csv_path}")

    df = pd.read_csv(csv_path)
    with open(meta_path) as f:
        meta = json.load(f)

    path_cols = [col for col in df.columns if col.endswith("_load")]

    osc = df[path_cols].std().mean()
    loss = df["total_loss"].mean()
    tput = df["total_throughput"].mean()
    fairness = df[path_cols].mean().std()

    result = {
        "file": os.path.basename(csv_path),
        "experiment": meta.get("experiment", "unknown"),
        "strategy": meta["strategy"],
        "agents": meta["agents"],
        "topology": meta.get("topology", "unknown"),
        "oscillation": round(osc, 2),
        "loss": round(loss, 2),
        "throughput": round(tput, 2),
        "fairness_std": round(fairness, 2)
    }

    logging.info(f"{result['file']}: "
                 f"osc={result['oscillation']}, "
                 f"loss={result['loss']}, "
                 f"tput={result['throughput']}, "
                 f"fairness={result['fairness_std']}")
    return result


def analyze_folder(folder="."):
    summary = []

    for file in os.listdir(folder):
        if file.endswith(".csv") and file.startswith("results_"):
            try:
                result = load_run(os.path.join(folder, file))
                summary.append(result)
            except Exception as e:
                logging.warning(f"Error with {file}: {e}")
                print(f" Error with {file}: {e}")

    return pd.DataFrame(summary)



if __name__ == "__main__":
    logging.info("=== Starting analysis ===")

    df = analyze_folder()
    df = df.sort_values(by=["experiment", "strategy", "agents"])

    for _, row in df.iterrows():
        logging.info(
            f"{row['file']}: "
            f"osc={row['oscillation']}, "
            f"loss={row['loss']}, "
            f"tput={row['throughput']}, "
            f"fairness={row['fairness_std']}"
        )

    print("\n=== Summary ===\n")
    print(df.to_string(index=False))

    df.to_csv("summary_all_experiments.csv", index=False)
    logging.info("=== Analysis complete ===\n")
