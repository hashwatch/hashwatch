from fastapi import Query, HTTPException
from app.internal.validator import is_api_key

def validate_api_key(api_key: str = Query(...)):
    if not is_api_key(api_key):
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    return api_key