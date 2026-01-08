import operator
import sys
import tempfile
import os
import subprocess
from typing import Annotated, List, TypedDict

from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import START, END, StateGraph

# --- CONFIG ---
MAX_RETRIES = 3  # Maximum times the agent can try to fix its own code

# --- CONNECT TO MEMORY & BRAIN ---
client = QdrantClient(path="./qdrant_db")
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vector_store = QdrantVectorStore(client=client, embedding=embeddings, collection_name="codebase_index")

llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.3)

# --- STATE ---
class AgentState(TypedDict):
    query: str
    context: List[str]
    answer: str
    error: str          # Tracks syntax errors found by linter
    iterations: int     # Safety counter

# --- NODES ---

def retrieve_node(state: AgentState):
    print(f"\n🔍 Searching codebase for: '{state['query']}'...")
    docs = vector_store.similarity_search(state['query'], k=3)
    context_text = [d.page_content for d in docs]
    return {"context": context_text, "iterations": 0}

def analyze_node(state: AgentState):
    print("🧠 Generating Fix...")
    
    # If we are looping back, add the previous error to the prompt
    error_context = ""
    if state.get("error"):
        print(f"   ⚠️ Previous fix failed syntax check. Retrying... (Attempt {state['iterations'] + 1})")
        error_context = f"\n\nYOUR PREVIOUS CODE HAD THIS SYNTAX ERROR:\n{state['error']}\nPLEASE FIX IT."

    prompt = f"""
    You are an expert Python Debugger.
    
    USER ERROR REPORT:
    "{state['query']}"
    
    RELEVANT CODE FOUND:
    ```python
    {state['context']}
    ```
    {error_context}
    
    TASK:
    1. Output ONLY the fixed Python code block. 
    2. Do NOT add explanation text outside the code block if possible.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content, "iterations": state["iterations"] + 1}

def validate_node(state: AgentState):
    """
    Worker 3: The Quality Control.
    Extracts code, runs it through a linter, and checks for syntax errors.
    """
    print("🕵️ Validating code syntax...")
    answer = state["answer"]
    
    # 1. Extract just the python code from the markdown blocks
    if "```python" in answer:
        code_block = answer.split("```python")[1].split("```")[0].strip()
    elif "```" in answer:
        code_block = answer.split("```")[1].split("```")[0].strip()
    else:
        code_block = answer # Assume raw code if no blocks

    # 2. Write to a temp file to run the linter
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp:
        temp.write(code_block)
        temp_path = temp.name

    # 3. Run Flake8 (Linter)
    # We only check for critical Syntax Errors (E9, F63, F7, F82)
    try:
        result = subprocess.run(
            ['flake8', temp_path, '--select=E9,F63,F7,F82', '--show-source'],
            capture_output=True, text=True
        )
        syntax_errors = result.stdout + result.stderr
    except Exception as e:
        syntax_errors = str(e)
    finally:
        os.remove(temp_path) # Clean up

    # 4. Return result
    if syntax_errors:
        print(f"   ❌ Syntax Error found: {syntax_errors.strip().splitlines()[0]}")
        return {"error": syntax_errors}
    else:
        print("   ✅ Syntax check passed!")
        return {"error": "None"}

# --- ROUTER ---
def router(state: AgentState):
    # If no error, finish
    if state["error"] == "None":
        return END
    # If too many retries, give up (to prevent infinite loops)
    if state["iterations"] >= MAX_RETRIES:
        print("   🛑 Max retries reached. Returning best guess.")
        return END
    # Otherwise, try again
    return "analyze"

# --- GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("validate", validate_node)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "analyze")
workflow.add_edge("analyze", "validate")
workflow.add_conditional_edges("validate", router, {END: END, "analyze": "analyze"})

app = workflow.compile()

if __name__ == "__main__":
    user_error = """
    The calculate_total method is broken. 
    Fix it, but please use 'print "The total is " + str(total)' inside the function for debugging.
    """
    print(f"🚀 Starting Agentic Debugger...")
    result = app.invoke({"query": user_error})
    
    print("\n" + "="*50)
    print("🤖 FINAL VALIDATED SOLUTION")
    print("="*50)
    print(result["answer"])
    client.close()