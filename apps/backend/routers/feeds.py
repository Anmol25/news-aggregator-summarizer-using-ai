from fastapi import APIRouter, HTTPException
from feeds.rss_feed import RssFeed
from sentence_transformers import SentenceTransformer
import torch
import yaml

router = APIRouter()


with open("feeds.yaml", 'r') as file:
    rss_feeds = yaml.safe_load(file)

sbert = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Check if a GPU is available
if torch.cuda.is_available():
    device = torch.device("cuda")  # Use GPU
    print("Using GPU:", torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")  # Use CPU
    print("GPU not available, using CPU.")

# Move the model to the GPU
sbert.to(device)

# Create RssFeed Object to store Articles
articles = RssFeed()


@router.on_event("startup")
async def startup_event():
    await articles.refresh_articles(rss_feeds, sbert, device)


@router.get("/feed/{topic}")
def retrieve_feed(topic: str):
    try:
        data = articles.get_articles()
        if topic not in data:
            raise HTTPException(status_code=404, detail="Topic not found")
        return data[topic]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
