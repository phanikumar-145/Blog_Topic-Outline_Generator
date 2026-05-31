# Expose the port Hugging Face expects
EXPOSE 7860

# Run Uvicorn binding to port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]