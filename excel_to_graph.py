# import pandas as pd
# from neo4j import GraphDatabase

# # ✅ Ensure correct file path
# xls = pd.ExcelFile("data/financial_data.xlsx")

# # ✅ Fix Neo4j connection
# NEO4J_URI = "bolt://localhost:7687"
# NEO4J_USER = "neo4j"  # ✅ Must be "neo4j", not "GraphRAG_DB"
# NEO4J_PASSWORD = "12345678"  # ✅ Ensure this is correct

# driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# def create_nodes_and_relationships(tx, sheet_name, df):
#     for _, row in df.iterrows():
#         properties = ", ".join([f"{col.replace(' ', '_')}: '{row[col]}'" for col in df.columns if pd.notna(row[col])])
#         query = f"MERGE (n:{sheet_name} {{{properties}}})"
#         tx.run(query)


# # ✅ FIX: Use `execute_write()` instead of `write_transaction()`
# with driver.session() as session:
#     for sheet in xls.sheet_names:
#         df = pd.read_excel(xls, sheet_name=sheet)
#         session.execute_write(create_nodes_and_relationships, sheet, df)

# print("✅ Data successfully loaded into Neo4j!")
import pandas as pd# excel_to_graph.py
import pandas as pd
from neo4j import GraphDatabase
import re
from pathlib import Path

# Neo4j connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_nodes_and_relationships(tx, sheet_name, df):
    for _, row in df.iterrows():
        # Clean column names
        clean_columns = {col: re.sub(r'[^a-zA-Z0-9_]', '_', col) for col in df.columns}
        
        # Build properties string with proper escaping
        properties = []
        for col in df.columns:
            if pd.notna(row[col]):
                value = str(row[col]).replace('\\', '\\\\').replace("'", "\\'")
                properties.append(f"`{clean_columns[col]}`: '{value}'")
        
        properties_str = ", ".join(properties)
        
        # Create Cypher query
        query = f"MERGE (n:{sheet_name} {{{properties_str}}})"
        tx.run(query)

def process_excel(file_path):
    try:
        # Verify file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Excel file not found at {file_path}")
            
        # Create Neo4j driver
        driver = get_neo4j_driver()
        
        # Read Excel file
        xls = pd.ExcelFile(file_path)
        
        # Process each sheet
        with driver.session() as session:
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                session.execute_write(create_nodes_and_relationships, sheet, df)
        
        print(f"✅ Successfully imported {file_path} into Neo4j!")
        return True
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        raise e
    finally:
        if 'driver' in locals():
            driver.close()

if __name__ == "__main__":
    test_file_path = "data/your_uploaded_file.xlsx"
    process_excel(test_file_path)