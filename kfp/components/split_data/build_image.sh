# Set global variables
REGION="europe-west1"
PROJECT_ID="third-being-310214"

# Build trainer image
IMAGE_NAME="split_data"
IMAGE_TAG="latest"
IMAGE_URI="eu.gcr.io/$PROJECT_ID/$NAME/$IMAGE_NAME:$IMAGE_TAG"
gcloud builds submit --async --tag $IMAGE_URI $IMAGE_NAME