from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from excel_to_graph import process_excel
from neo4j import GraphDatabase
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GraphRAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_DIR = "data"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize Neo4j driver
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    logger.info("Successfully connected to Neo4j")
except Exception as e:
    logger.error(f"Failed to connect to Neo4j: {str(e)}")
    raise

@app.post("/upload_excel/")
async def upload_excel(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Upload and process an Excel file into Neo4j.
    
    Args:
        file: The uploaded Excel file
    
    Returns:
        Dict containing success message
    
    Raises:
        HTTPException: If file upload or processing fails
    """
    try:
        # Validate file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are accepted"
            )

        file_path = os.path.join(DATA_DIR, file.filename)
        
        # Save uploaded file
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )

        # Process file in Neo4j
        try:
            process_excel(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file in Neo4j: {str(e)}"
            )

        logger.info(f"Successfully processed {file.filename}")
        return {"message": f"✅ {file.filename} uploaded & data inserted into Neo4j"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/query/")
async def query_data(
    question: str = Query(..., description="Enter your query")
) -> Dict[str, Any]:
    """
    Query Neo4j database based on user question.
    
    Args:
        question: The search query string
    
    Returns:
        Dict containing query results or no-match message
    
    Raises:
        HTTPException: If query execution fails
    """
    try:
        with driver.session() as session:
            # Sanitize input to prevent injection
            sanitized_question = question.replace("'", "\\'")
            
            # Execute query
            result = session.run(
                "MATCH (n) WHERE n.name CONTAINS $question RETURN n LIMIT 5",
                question=sanitized_question
            )
            
            # Process results
            data = [dict(record["n"]) for record in result]
            
            return {
                "response": data if data else "No matching data found"
            }

    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to execute query"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    driver.close()
    logger.info("Application shutdown: Neo4j connection closed")