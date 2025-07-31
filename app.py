from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ollama import chat
import re

def clean_sql(text: str) -> str:
    text = text.strip()
    # Remove fenced code if present
    text = re.sub(r"^```(?:sql)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def flatten_sql_safe(sql: str) -> str:
    # Option 2: split and rejoin intelligently
    return " ".join(line.strip() for line in sql.splitlines() if line.strip())

app = FastAPI()


class QueryRequest(BaseModel):
    schema_: str = Field(..., alias="schema")
    question: str

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    prompt = f"""
            You are an expert SQL developer. Given the following database schema:

            {request.schema}

            Write a SQL query that answers the following question:

            {request.question}

            Only return the SQL query. Do not include any explanation.
            """

    try:
        response = chat(
            model='gemma3',
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return {"sql_query": flatten_sql_safe(clean_sql(response['message']['content'].strip()))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", port=8000, reload=True)
