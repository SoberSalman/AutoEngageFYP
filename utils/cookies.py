from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sql import crud
from utils.logger import print_error


def validate_admin_cookies(db: Session, request: Request) -> dict:
    cookie_header = request.headers.get("cookie")
    if not cookie_header:
        print_error("No cookies found in the request.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=401),
        }

    cookies = {
        cookie.split("=")[0]: cookie.split("=")[1]
        for cookie in cookie_header.split("; ")
    }

    current_username = cookies.get("current_username")
    if current_username != "admin":
        print_error("Authentication failed. Admin access is required.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=403),
        }

    if not crud.get_user(db, current_username):
        print_error("Admin user not found in the database.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=404),
        }

    return {"success": True, "response": None}


def validate_cookies(
    db: Session, request: Request, keys: list = ["current_username"]
) -> dict:
    cookie_header = request.headers.get("cookie")
    if not cookie_header:
        print_error("No cookies found in the request.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=401),
        }

    cookies = {
        cookie.split("=")[0]: cookie.split("=")[1]
        for cookie in cookie_header.split("; ")
    }

    current_username = cookies.get("current_username")
    if not current_username:
        print_error("No username found in the cookies.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=401),
        }

    if not crud.get_user(db, current_username):
        print_error("User not found in the database.")
        return {
            "success": False,
            "response": RedirectResponse(url="/login", status_code=404),
        }

    cookies = {key: cookies[key].strip('"') for key in keys if key in cookies}
    return {"success": True, "cookies": cookies}
