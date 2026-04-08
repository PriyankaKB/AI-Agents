#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
DATASET_NAME="mcp_blog"
LOCATION="US"

# Generate bucket name if not provided
if [ -z "$1" ]; then
    BUCKET_NAME="gs://mcp-blog-data-$PROJECT_ID"
    echo "No bucket provided. Using default: $BUCKET_NAME"
else
    BUCKET_NAME=$1
fi

echo "----------------------------------------------------------------"
echo "MCP news Demo Setup"
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_NAME"
echo "Bucket:  $BUCKET_NAME"
echo "----------------------------------------------------------------"

# 1. Create Bucket if it doesn't exist
echo "[1/8] Checking bucket $BUCKET_NAME..."
if gcloud storage buckets describe $BUCKET_NAME >/dev/null 2>&1; then
    echo "      Bucket already exists."
else
    echo "      Creating bucket $BUCKET_NAME..."
    gcloud storage buckets create $BUCKET_NAME --location=$LOCATION
fi

# 2. Upload Data
echo "[2/8] Uploading data to $BUCKET_NAME..."
gcloud storage cp data/*.csv $BUCKET_NAME

# 3. Create Dataset
echo "[3/8] Creating Dataset '$DATASET_NAME'..."
if bq show "$PROJECT_ID:$DATASET_NAME" >/dev/null 2>&1; then
    echo "      Dataset already exists. Skipping creation."
else    
    bq mk --location=$LOCATION --dataset \
        --description "$DATASET_DESCRIPTION" \
        "$PROJECT_ID:$DATASET_NAME"
    echo "      Dataset created."
fi

# 4. Create mcp-drafting-data Table
echo "[4/8] Setting up Table: mcp-drafting-data..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.mcp-drafting-data\` (
    id INT OPTIONS (description='Id of blog content'),
    title STRING OPTIONS (description='Title of blog, reaserch or publishing'),
    author STRING OPTIONS (description='Author of blog, reaserch or publishing'),
    location STRING OPTIONS (description='Location related to blog or mentioned in the content'),
    timestamp STRING OPTIONS (description='Timestamp or date of publishing')
    content STRING OPTIONS (description='Blog content')
)
OPTIONS(
    description='Drafting data for drafting content.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$DATASET_NAME.mcp-drafting-data" "$BUCKET_NAME/mcp-drafting-data.csv"

# 5. Create mcp-plagiarism-data Table
echo "[5/8] Setting up Table:mcp-plagiarism-data..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.mcp-plagiarism-data\` (
    sentence1 STRING OPTIONS (description='First sentence'),
    sentence2 STRING OPTIONS (description='Second sentence'),
    label STRING OPTIONS (description='Label for data - 0 for non-plagirised and 1 for plgiarised'),
)
OPTIONS(
    description='Plagiarism comparison dataset.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$DATASET_NAME.mcp-plagiarism-data" "$BUCKET_NAME/mcp-plagiarism-data.csv"

# 6. Create mcp-seo-data Tables
echo "[6.1/8] Setting up Table:mcp-seo-data..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.mcp-seo-data\` (
    id INT OPTIONS (description='id of seo field'),
    url STRING OPTIONS (description='url of seo field'),
    title STRING OPTIONS (description='title of seo field'),
    author STRING OPTIONS (description='author of seo field'),
    location STRING OPTIONS (description='location of seo field'),
    timestamp STRING OPTIONS (description='timestamp of seo field'),
    meta_description STRING OPTIONS (description='meta_description of seo field '),
    keywords STRING OPTIONS (description='keywords of seo field'),
    content STRING OPTIONS (description='content of seo field')
)
OPTIONS(
    description='SEO dataset.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$DATASET_NAME.mcp-seo-data" "$BUCKET_NAME/mcp-seo-data.csv"

# 7. Create mcp-publishing-data Tables
echo "[7/8] Setting up Table:mcp-publishing-data..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.mcp-publishing-data\` (
    id INT OPTIONS (description='id'),
    title STRING OPTIONS (description='title'),
    author STRING OPTIONS (description='author'),
    category STRING OPTIONS (description='category'),
    status STRING OPTIONS (description='status'),
    scheduled_date STRING OPTIONS (description='scheduled_date'),
    content STRING OPTIONS (description='content'),
)
OPTIONS(
    description='Publishing dataset.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$DATASET_NAME.mcp-publishing-data" "$BUCKET_NAME/mcp-publishing-data.csv"

# 8. Create mcp-feedback-data Tables
echo "[8/8] Setting up Table:mcp-feedback-data..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.mcp-feedback-data\` (
    id INT OPTIONS (description='id'),
    user_id INT OPTIONS (description='title'),
    post_id INT OPTIONS (description='author'),
    post_title STRING OPTIONS (description='category'),
    rating INT OPTIONS (description='status'),
    comment STRING OPTIONS (description='scheduled_date'),
    timestamp STRING OPTIONS (description='content'),
)
OPTIONS(
    description='feedback dataset.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$DATASET_NAME.mcp-feedback-data" "$BUCKET_NAME/mcp-feedback-data.csv"



echo "----------------------------------------------------------------"
echo "Setup Complete!"
echo "----------------------------------------------------------------"