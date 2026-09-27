from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user.update_user_info import UpdateUserInfoService
from src.vm.user.user_info_vm import UserInfoUpdateReqModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")


class TestUpdateUserInfoService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> UpdateUserInfoService:
        return UpdateUserInfoService(mock_session)

    @pytest.fixture
    def mock_file(self) -> MagicMock:
        file = MagicMock(spec=UploadFile)
        file.filename = "avatar.jpg"
        file.read = AsyncMock(side_effect=[b"content", b""])
        file.close = AsyncMock()
        return file

    # --- update_user_info ---

    async def test_update_user_info(self, service: UpdateUserInfoService):
        data = UserInfoUpdateReqModel(name="Ben2", email="ben2@gmail.com")

        result = await service.update_user_info(USER_ID, data)

        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert 'UPDATE restaurant."user"' in stmt
        assert result["code"] == 200

    async def test_update_user_info_partial(self, service: UpdateUserInfoService):
        data = UserInfoUpdateReqModel(name=None, email="ben2@gmail.com")

        await service.update_user_info(USER_ID, data)

        values = service._session.execute.call_args[0][0].compile().params  # type: ignore
        assert values == {"email": "ben2@gmail.com", "id_1": USER_ID}

    # --- update_user_image ---

    async def test_update_user_image(self, service: UpdateUserInfoService, mock_file: MagicMock):
        service._save_file_to_folder = AsyncMock(return_value="uuid_avatar.jpg")

        result = await service.update_user_image(USER_ID, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._session.execute.assert_awaited_once()  # type: ignore
        assert result["code"] == 200

    async def test_update_user_image_without_file(self, service: UpdateUserInfoService):
        with pytest.raises(HTTPException) as exc_info:
            await service.update_user_image(USER_ID, file=None)

        assert exc_info.value.status_code == 400
        service._session.execute.assert_not_awaited()  # type: ignore

    # --- _save_file_to_folder ---

    @pytest.fixture
    def patched_file_path(self, tmp_path, monkeypatch):
        import src.service.user.update_user_info as module
        monkeypatch.setattr(module, "FILE_PATH", tmp_path)
        return tmp_path

    async def test_save_file_to_folder(
            self, service: UpdateUserInfoService, mock_file: MagicMock, patched_file_path
    ):
        filename = await service._save_file_to_folder(file=mock_file)

        assert filename.endswith("_avatar.jpg")
        assert (patched_file_path / filename).exists()
        mock_file.close.assert_awaited_once()

    async def test_save_file_to_folder_write_failure(
            self, service: UpdateUserInfoService, mock_file: MagicMock, patched_file_path
    ):
        mock_file.read = AsyncMock(side_effect=OSError("disk full"))

        with pytest.raises(HTTPException) as exc_info:
            await service._save_file_to_folder(file=mock_file)

        assert exc_info.value.status_code == 500
        mock_file.close.assert_awaited_once()
