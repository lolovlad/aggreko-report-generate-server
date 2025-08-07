from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from urllib.parse import quote

from ..repositories import FileBucketRepository


router = APIRouter(prefix="/file", tags=["file"])


@router.get("/")
async def get_file(name_file: str):
    file_repo_blueprint = FileBucketRepository('blueprint')
    file_repo_report = FileBucketRepository('report')
    file_name_split = name_file.split("/")

    file_name = name_file.split("/")[-1]
    buket = name_file.split("/")[0]

    if name_file is None:
        return JSONResponse(content={"message": "не существует"},
                            status_code=status.HTTP_404_NOT_FOUND)

    media_type = "application/octet-stream"

    encoded_filename = quote(file_name)
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}

    file_key = "/".join(file_name_split[1:])
    if buket == "blueprint":
        info = await file_repo_blueprint.get_sate(file_key)
        return StreamingResponse(
            file_repo_blueprint.get_file_stream(file_key, info.size),
            media_type=media_type,
            headers=headers,
        )
    else:
        info = await file_repo_report.get_sate(file_key)
        return StreamingResponse(
            file_repo_report.get_file_stream(file_key, info.size),
            media_type=media_type,
            headers=headers,
        )
