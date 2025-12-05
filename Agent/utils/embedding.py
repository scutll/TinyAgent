import chromadb
from chromadb.utils import embedding_functions
from Agent.prompts import tools_prompt
import json


def get_all_tool_prompts_description() -> list:
    prompts = []
    prompt_id = 1
    for name in dir(tools_prompt):
        if "Finish" in name or "__" in name:
            continue

        value = getattr(tools_prompt, name)
        prompts.append({
            "id": f"tp{prompt_id}",
            "text": (json.loads(value))["description"],
            "meta": {"tool": name.replace('_prompt', '')}
        })
        prompt_id += 1
    print("total: ", len(prompts), " tool prompts loaded")
    return prompts
    


client = chromadb.PersistentClient(path="E:/D2L/Agent/TinyAgent/Agent/prompts/tools_db")
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="moka-ai/m3e-small")


collection = client.get_or_create_collection(
    name="tool_prompts",
    embedding_function=embedding_func
    )

# prompts = get_all_tool_prompts_description()
# collection.add(
#     documents=[p["text"] for p in prompts],
#     metadatas=[p["meta"] for p in prompts],
#     ids=[p["id"] for p in prompts],
# )
print(collection.count())


# 准确性堪忧。。。现在换成moka-ai/m3e-small会好一点，但sentence-transformer是真难绷




class Embedding_tool_db:
    
    def __init__(self,
                 path="E:/D2L/Agent/TinyAgent/Agent/prompts/tools_db",
                 model="moka-ai/m3e-small",
                 collection_name="tool_prompts") -> None:
        self.path = path
        self.model = model
        self.collection_name = collection_name
        self.collection = None
    
    def __init_db(self) -> None:
        client = chromadb.PersistentClient(path=self.path)
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.model)
        self.collection = client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_func,
        )


    def _query_tool(self, query: str, k: int):
        results = collection.query(
            query_texts=[query],
            n_results=k
        )
        return [p["tool"] for p in results['metadatas'][0]]

    def _add_tool_todb(self, tool_name: str, tool_description: str):
        cnt = collection.count()
        collection.add(
            ids=[f"tp{cnt}"],
            documents=[tool_description],
            metadatas=[{"tool": tool_name}]
        )