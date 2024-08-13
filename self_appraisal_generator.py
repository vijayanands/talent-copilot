from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
from llama_index.legacy.vector_stores import PineconeVectorStore


def generate_self_appraisal(email, llm, pinecone_index):
    # Create vector store
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Recreate the index from the existing vector store
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # Query for relevant information
    query_engine = index.as_query_engine(llm=llm)
    
    # Construct prompts for different aspects of the self-appraisal
    prompts = [
        f"What are the main accomplishments of {email} based on the available data?",
        f"What projects has {email} been involved in?",
        f"What are the key skills demonstrated by {email}?",
        f"Are there any areas where {email} has shown improvement?",
        f"What are some potential areas of growth for {email}?"
    ]

    # Generate responses for each prompt
    responses = [query_engine.query(prompt) for prompt in prompts]

    # Combine responses into a self-appraisal document
    appraisal = f"Self-Appraisal for {email}\n\n"
    appraisal += "1. Main Accomplishments:\n" + str(responses[0]) + "\n\n"
    appraisal += "2. Project Involvement:\n" + str(responses[1]) + "\n\n"
    appraisal += "3. Key Skills Demonstrated:\n" + str(responses[2]) + "\n\n"
    appraisal += "4. Areas of Improvement:\n" + str(responses[3]) + "\n\n"
    appraisal += "5. Potential Growth Areas:\n" + str(responses[4]) + "\n\n"

    return appraisal
