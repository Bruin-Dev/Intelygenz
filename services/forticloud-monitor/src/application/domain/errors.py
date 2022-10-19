class AutoResolutionError(Exception):
    pass


class ServiceNumberHasNoTaskError(AutoResolutionError):
    pass


class ServiceNumberTaskWasAlreadyResolvedError(AutoResolutionError):
    pass


class AutoResolutionGracePeriodExpiredError(AutoResolutionError):
    pass


class MaxTaskAutoResolutionsReachedError(AutoResolutionError):
    pass
