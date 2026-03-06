from fastapi import status
from fastapi.exceptions import HTTPException

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

ACCESSORY_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found"
)

LOCATION_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
)

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="User not found",
)

USER_NOT_PERMITTED_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="User not permitted"
)
