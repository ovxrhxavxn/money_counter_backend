import dramatiq

import dramatiq.asyncio
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO
from pathlib import Path

from database.crud import SQLAlchemyCRUD
from database.database import SQLAlchemyDBHelper
from cv_models.schemas import TaskSchema, TaskId, ImageHistorySchema, CVModelEnum
from cv_models.cv_processing.model import work_with_items
from utils import UtilsMethod


broker = RedisBroker(url='redis://localhost:6379')
broker.add_middleware(AsyncIO())
dramatiq.set_broker(broker)

class TasksSet:

    @dramatiq.actor
    @dramatiq.asyncio.async_to_sync
    @staticmethod
    async def use_yolo8s(user_name: str, task_id: int, image_path: Path):
        
        # TODO: Реализация работы с моделью

        #sum, main_img, imgs_array = work_with_items(bytes(image))

        async_generator = SQLAlchemyDBHelper().get_async_session()

        session = await async_generator.__anext__()

        crud = SQLAlchemyCRUD(session)

        task: TaskId = await crud.get_task_by_id(task_id)

        await crud.update_task_result(task.msg_id, 'main_img')

        await crud.update_user_token_amount(user_name, 5)

        user_id = await crud.get_user_id(user_name)

        await crud.add_image_history(ImageHistorySchema(

            user_id=user_id,
            task_id=task_id
        ))


    @dramatiq.actor
    @dramatiq.asyncio.async_to_sync
    @staticmethod
    async def use_yolo8m(user_name: str, task_id: int, image_path: str):

        utils_method = UtilsMethod()
        
        # TODO: Реализация работы с моделью

        image_bytes = utils_method.read_image(image_path)

        sum, main_img, imgs_array = work_with_items(task_id, image_bytes)

        async_generator = SQLAlchemyDBHelper().get_async_session()

        session = await async_generator.__anext__()

        crud = SQLAlchemyCRUD(session)

        task: TaskId = await crud.get_task_by_id(task_id)

        await crud.update_task_result(task.msg_id, str(Path(f'database\\images\\processed\\{task_id}Result.jpeg')))

        cv_model = await crud.get_cv_model(CVModelEnum.YOLO8M)

        await crud.update_user_token_amount(user_name, cv_model.cost)

        user_id = await crud.get_user_id(user_name)

        await crud.add_image_history(ImageHistorySchema(

            user_id=user_id,
            task_id=task_id
        ))


    @dramatiq.actor
    @dramatiq.asyncio.async_to_sync
    @staticmethod
    async def use_yolo8n(user_name: str, task_id: int, image: bytes):
        
        # TODO: Реализация работы с моделью

        async_generator = SQLAlchemyDBHelper().get_async_session()

        session = await async_generator.__anext__()

        task: TaskSchema = await SQLAlchemyCRUD().get_task_by_id(session, task_id)

        await SQLAlchemyCRUD().update_task_result(session, task.msg_id, 'new result from y8n')

        await SQLAlchemyCRUD().update_user_token_amount(session, user_name, 15)