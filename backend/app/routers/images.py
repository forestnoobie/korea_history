"""Serve question images from the local filesystem."""
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..config import settings

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/{path:path}")
def serve_image(path: str):
    """
    Serve an image file. `path` is relative to `settings.images_root`.
    Path-traversal is prevented by resolving and checking the prefix.
    """
    root = os.path.realpath(settings.images_root)
    requested = os.path.realpath(os.path.join(root, path))

    if not requested.startswith(root + os.sep) and requested != root:
        raise HTTPException(status_code=400, detail="Invalid path.")

    if not os.path.isfile(requested):
        raise HTTPException(status_code=404, detail="Image not found.")

    return FileResponse(requested)
