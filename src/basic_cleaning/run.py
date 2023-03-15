#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    """
    load the input csv file with the following columns:
    ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
       'neighbourhood', 'latitude', 'longitude', 'room_type', 'price',
       'minimum_nights', 'number_of_reviews', 'last_review',
       'reviews_per_month', 'calculated_host_listings_count',
       'availability_365']
    """
    df = pd.read_csv(artifact_local_path)
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    # remove price outliers
    idx = df['price'].between(args.min_price, args.max_price) & \
        df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    # save the updated dataframe as a csv
    df[idx].to_csv(args.output_artifact, index=False)
    # create a new artifact and upload the cleaned data
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="mlflow input artifact filename with a version. Eg. sample.csv:latest",
        required=True)

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="mlflow output artifact filename. Eg. output.csv",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="the task/category the artifact should fall under",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="a detailed description of the output file/result",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="minimum price value to be considered valid",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="maximum price value to be considered valid",
        required=True
    )

    args = parser.parse_args()
    go(args)
