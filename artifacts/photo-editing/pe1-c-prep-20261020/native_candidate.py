"""Prospective empty-slot qualification. Not installed or used by the app."""

from app.images.engine import Engine


class CandidateEngine(Engine):
    @staticmethod
    def qualified_edit(models):
        # The only change proposed for qualification; strict existing resident gate remains.
        return models == [] or Engine.qualified_edit(models)
