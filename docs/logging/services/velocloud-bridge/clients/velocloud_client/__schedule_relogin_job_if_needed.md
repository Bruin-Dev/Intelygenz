## Schedule relogin job if needed

* If auth token expired for a particular VeloCloud host:
    ```python
    logger.info(f"Auth token expired for host {velocloud_host}. Scheduling re-login job...")
    ```

    [_start_relogin_job](_start_relogin_job.md)