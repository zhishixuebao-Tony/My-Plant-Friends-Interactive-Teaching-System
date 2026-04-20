from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, db_instance
from app.api.endpoints import student_flow, teacher_dash, ws_routes, ops_control


app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

media_dir = Path(settings.LOCAL_MEDIA_DIR)
media_dir.mkdir(parents=True, exist_ok=True)
media_prefix = "/" + str(settings.LOCAL_MEDIA_URL_PREFIX).strip("/")
app.mount(media_prefix, StaticFiles(directory=str(media_dir)), name="local_media")


@app.on_event('startup')
async def startup():
    await connect_to_mongo()


@app.on_event('shutdown')
async def shutdown():
    await close_mongo_connection()


@app.on_event('startup')
async def startup_db_client():
    admin_col = db_instance.db.admin_config
    existing = await admin_col.find_one({'key': 'teacher_password'})
    if not existing:
        await admin_col.insert_one({'key': 'teacher_password', 'value': '123456'})


app.include_router(student_flow.router, prefix='/api/student', tags=['student_flow'])
app.include_router(teacher_dash.router, prefix='/api/teacher', tags=['teacher_dashboard'])
app.include_router(ops_control.router, prefix='/api/ops', tags=['ops_control'])
app.include_router(ws_routes.router, prefix='/ws', tags=['websocket'])
