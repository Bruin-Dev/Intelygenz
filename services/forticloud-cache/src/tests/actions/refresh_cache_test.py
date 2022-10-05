from unittest.mock import AsyncMock


async def refresh_cache_not_return_nothing_test(refresh_cache_instance):
    refresh_cache_instance.cache_repository.add_job_to_refresh_cache = AsyncMock()
    result_refresh_cache = await refresh_cache_instance.refresh_cache()
    assert result_refresh_cache is None


async def refresh_cache_not_called_to_add_job_test(refresh_cache_instance):
    refresh_cache_instance.cache_repository.add_job_to_refresh_cache = AsyncMock()
    await refresh_cache_instance.refresh_cache()
    refresh_cache_instance.cache_repository.add_job_to_refresh_cache.assert_called()
