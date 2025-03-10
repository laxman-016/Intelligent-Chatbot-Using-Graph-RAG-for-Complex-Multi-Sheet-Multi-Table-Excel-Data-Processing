def query_graph(tx, query):
    result = tx.run(query)
    return [record for record in result]
# import os
# import requests
# import streamlit as st

# # ✅ Ensure 'data' directory exists before anything
# DATA_DIR = "data"  # Go one level up to backend's data folder
# if not os.path.exists(DATA_DIR):
#     os.makedirs(DATA_DIR)

# uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# if uploaded_file:
#     file_path = os.path.join(DATA_DIR, uploaded_file.name)

#     try:
#         # ✅ Save the uploaded file
#         with open(file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         # ✅ Send the file to the backend API
#         with open(file_path, "rb") as file:
#            response = requests.post("http://localhost:8000/upload_excel/", files={"file": file})


#         if response.status_code == 200:
#             st.success("✅ File uploaded & data added to Neo4j!")
#         else:
#             st.error(f"❌ Upload failed! Server responded with: {response.status_code}")

#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# # ✅ Question Input Box
# question = st.text_input("Ask me anything!")

# if question:
#     response = requests.get(f"http://localhost:8000/query/?question={question}")
#     if response.status_code == 200:
#         st.write(response.json())
#     else:
#         st.error("❌ Error in fetching results.")
