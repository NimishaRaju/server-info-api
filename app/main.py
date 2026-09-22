import logging
from fastapi import FastAPI, status, HTTPException, Depends
from schemas import CreateServer, ServerMetricPatchRequest
from services import ServerService
from dependencies import get_server_service


app=FastAPI()

logger = logging.getLogger("uvicorn.error")


@app.get('/health')
def health():
    return {'status':"success"}

@app.get('/api/servers')
async def get_server(server_service:ServerService=Depends(get_server_service)):
    return server_service.get_all_servers()

@app.get('/api/servers/{server_id}',status_code=status.HTTP_200_OK)
async def get_server(server_id:str,server_service:ServerService=Depends(get_server_service)):
    server=server_service.get_server_by_id(server_id)
    if not server:
            raise HTTPException(status_code=404, detail=f"Server with ID '{server_id}' not found.")
    return server

@app.post("/api/servers", status_code=status.HTTP_201_CREATED)
async def create_server(payload: CreateServer,server_service:ServerService=Depends(get_server_service)):
    new_server=server_service.create_server(payload.server_name)
    # Return a custom success response to the client
    return {
        "status": "success",
        "message": f"Server '{payload.server_name}' successfully added to database.",
        "server_id": new_server["server_id"]
    }

@app.patch("/api/servers/{server_id}",status_code=status.HTTP_200_OK)
def update_server(server_id: str,payload:ServerMetricPatchRequest,server_service:ServerService=Depends(get_server_service)):
    """
    HTTP PATCH Route. Targets the server by validating the path param
    against the 'server_id' field inside the single-object JSON file.
    """
    # Extract ONLY the fields the client explicitly sent
    update_data = payload.model_dump(exclude_unset=True)
    updated_fields = server_service.update_server(server_id, update_data)
    if updated_fields is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Server with ID '{server_id}' not found in the file."
            )
    return {
        "message": f"Server '{server_id}' updated successfully", 
        "updated_fields": updated_fields
    }

@app.delete("/api/servers/delete/{server_id}",status_code=status.HTTP_200_OK)
def delete_server(server_id:str,server_service:ServerService=Depends(get_server_service)):
    """
    HTTP DELETE Route. Finds the server matching the path parameter
    and removes it from the list inside the JSON file.
    """
    logger.info(f"🚀 ROUTE ACCESSED! Looking for ID: {server_id}")
    deleted=server_service.delete_server(server_id)
    if not deleted:
            raise HTTPException(
                status_code=404, 
                detail=f"Server with ID '{server_id}' not found."
            )

    return {"message": f"Server '{server_id}' successfully deleted."}