"""
containing routes
"""
from typing import Any, Dict
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES, db
from app.utils import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from .models import User, UserInDB, Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):

    """
    Endpoint to authenticate a user and generate an access token.

    :param form_data: OAuth2PasswordRequestForm type object (
        containing username and password
    )
    :return: Dictionary with access token and token type
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the details of the currently authenticated user.

    Parameters:
    - current_user (User): The current authenticated user.

    Returns:
    - User: Details of the current authenticated user.
    """
    return current_user


@router.post("/users/", response_model=User)
async def create_user(user: UserInDB):
    """
    Create a new user in the database.

    Parameters:
    - user: UserInDB - The user object to be created.

    Returns:
    - User: The newly created user object.

    This function hashes the user's password,
    inserts the user data into the database,
    retrieves the created user, and returns it.
    """
    password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = password
    new_user = await db.users.insert_one(user_dict)
    return await db.users.find_one({"_id": new_user.inserted_id})


@router.patch("/users/me", response_model=User)
async def update_user_partial(
    update_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """
    Update a user partially.

    Parameters:
    - update_data (Dict[str, Any]): Data to update for the user.
    - current_user (User): The current user making the update.

    Raises:
    - HTTPException: If no update data is provided,
    user is not found, or no changes are made.

    Returns:
    - User: The updated user object.
    """
    if len(update_data) == 0:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_result = await db.users.update_one(
        {"username": current_user.username}, {"$set": update_data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404,
                            detail="User not found or no changes made")

    return await db.users.find_one({"username": current_user.username})


@router.put("/users/me", response_model=User)
async def update_user_full(
    user_update: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """
    Update the current user's information.
    Hashes the new password if provided.
    If no new password is provided,
    removes the password field to avoid overwriting with None.
    Raises HTTPException if the user is not found or no changes are made.
    Returns the updated user.
    """
    update_data = user_update.copy()
    # Hash the new password if provided
    if user_update.get("password"):
        update_data["password"] = get_password_hash(
            user_update.get("password")
        )
    else:
        # If no new password provided,
        # remove the password field to avoid overwriting with None
        update_data.pop("password", None)

    update_result = await db.users.replace_one(
        {"username": current_user.username}, update_data
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404,
                            detail="User not found or no changes made")

    return await db.users.find_one({"username": current_user.username})


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: User = Depends(get_current_user)):
    """
    Delete the current user from the database.

    Parameters:
    - current_user (User): The user to be deleted.

    Raises:
    - HTTPException: If the user is not found.

    Returns:
    - dict: A message confirming successful deletion.
    """
    delete_result = await db.users.delete_one(
        {"username": current_user.username})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User deleted successfully"}
