"""
summarizer.py
This module contains the summarizer for the aggregator.
"""

import torch
import logging
from transformers import BartTokenizer, BartForConditionalGeneration
from goose3 import Goose

logger = logging.getLogger(__name__)
# Disable debug warning of urlib3
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Summarizer:

    def __init__(self):
        model_name = "sshleifer/distilbart-cnn-12-6"
        cache_dir = "./model/DistilBART"

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BartTokenizer.from_pretrained(
            model_name, cache_dir=cache_dir)
        # Load Model
        logger.info("Loading DistilBART Model for Summarization")
        self.model = BartForConditionalGeneration.from_pretrained(
            model_name, cache_dir=cache_dir).to(self.device)
        if str(self.device) == "cuda":
            logger.info("DistilBART is Using GPU")
        else:
            logger.info("DistilBART is Using CPU")

    @staticmethod
    def __get_article(url: str):
        """
        Fetch and Parse Article
        Args:
            url: URL of article
        Returns:
            text: Text content of Article
        Raises:
            Exception: If article cannot be fetched or parsed
        """
        try:
            # Fetch Article
            g = Goose()
            article = g.extract(url=url)

            text = article.cleaned_text

            if not text:
                raise Exception("No text content found in article")

            return text
        except Exception as e:
            logger.error(f"Error in Parsing Article: {e}")
            raise Exception(f"Failed to fetch or parse article: {str(e)}")

    def summarize(self, article):
        """
        Tokenize and then summarize article
        Args:
            article: Text content of article
        Returns:
            summary: Summary of Article
        """
        try:
            # Tokenize Article
            inputs = self.tokenizer(article, return_tensors="pt",
                                    max_length=1024, truncation=True, padding="longest")
            inputs = {key: value.to(self.device)
                      for key, value in inputs.items()}
            # Generate Summary
            # Generate summary
            summary_ids = self.model.generate(
                inputs["input_ids"],
                min_length=60,       # Forces a longer summary
                max_length=100,      # Upper limit
                num_beams=4,         # Beam search for better quality
                length_penalty=1.4,  # Controls summary length (lower = longer)
                early_stopping=True
            )
            # Decode and print summary
            summary = self.tokenizer.decode(
                summary_ids[0], skip_special_tokens=True)
            # print(summary)
            return summary
        except Exception as e:
            logger.error(f"Error in Generating Summary: {e}")
            return None

    def infer(self, url: str) -> str:
        """
        Get summary of article from url
        Args:
            url: URL of article
        Return:
            summary: Summary of article
        Raises:
            Exception: If article cannot be fetched or summarized
        """
        try:
            # Fetch Article
            article = Summarizer.__get_article(url)
            # Generate Summary
            summary = self.summarize(article)
            if not summary:
                raise Exception("Failed to generate summary")
            return summary
        except Exception as e:
            logger.error(f"Unexpected error in getting summary: {e}")
            raise Exception(f"Failed to generate summary: {str(e)}")
