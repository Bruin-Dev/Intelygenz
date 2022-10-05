class RefreshCache:
    def __init__(self, cache_repository):
        self.cache_repository = cache_repository

    async def refresh_cache(self):
        await self.cache_repository.add_job_to_refresh_cache()
