class MatamataServiceException(Exception):
    pass


class MatchAlreadyRegisteredResult(MatamataServiceException):
    pass


class MatchShouldHaveAutomaticWinner(MatamataServiceException):
    pass


class MatchMissingCompetitorFromPreviousMatch(MatamataServiceException):
    pass


class MatchTargetCompetitorIsNotMatchCompetitor(MatamataServiceException):
    pass
