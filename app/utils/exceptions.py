from fastapi import HTTPException, status

def not_found(detail: str = "Not found"):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def bad_request(detail: str = "Bad request"):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
