class ValidateStatsMixin(object):
    # TODO: Move this class to a higher level, where could be useful for thing beyond this
    # network module, maybe BaseEntity
    def validate_stats(self, expected_stats):
        """ Validates that the details page matches the expected stats.

        Args:
            expected_stats: dictionary of values to be compered to UI values,
            where keys have the same names as ui methods in classes that inherits this class.

        This method is given expected stats as an argument and those are then matched
        against the UI. An AssertionError exception will be raised if the stats retrieved
        from the UI do not match those from expected stats.

        IMPORTANT: Please make sure inherited classes implements counterpart ui method for each of
        the keys in expected_stats dictionary.
        """

        cfme_stats = {
            stat: getattr(self, stat) for stat in expected_stats
        }
        assert cfme_stats == expected_stats
