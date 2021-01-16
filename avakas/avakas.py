"""
Avakas classes and plugin handlers
"""

from semantic_version import Version

from .errors import AvakasError


def detect_project_flavor(**kwargs):
    """
    Determines the project flavor for a given directory
    """

    flavor = kwargs.get('flavor', 'auto')

    if flavor == 'auto':
        matched = [f for n, f
                   in Avakas.project_flavors.items()
                   if f.guess_flavor(directory=kwargs['directory'][0])]
        if len(matched) == 1:
            project = matched[0]
        elif len(matched) == 0:
            project = Avakas.project_flavors['legacy']
        else:
            matched_names = [f.PROJECT_TYPE for f in matched]
            raise AvakasError("Multiple project flavor matches: %s" %
                              ", ".join(matched_names))
    else:
        if flavor in Avakas.project_flavors:
            project = Avakas.project_flavors[flavor]
        else:
            raise AvakasError('Unable to find flavor "%s"' % flavor)

    return project(**kwargs)


class Avakas():
    """
    Main instance of Avakas associated to a project and it's version
    """
    project_flavors = {}

    def __init__(self, **kwargs):
        self._version = Version('0.0.0')
        self.directory = kwargs['directory'][0]
        self.options = kwargs

    @property
    def version(self):
        """Get version"""
        tag_prefix = self.options.get('tag_prefix', '')
        return "%s%s" % (tag_prefix, self._version)

    @version.setter
    def version(self, version):
        """Set version"""
        if not isinstance(version, str):
            raise TypeError("version must be type of str")

        tag_prefix = self.options.get('tag_prefix', None)
        version = version.strip(tag_prefix)

        try:
            self._version = Version(version)
        except ValueError as err:
            raise AvakasError("Invalid version string %s" %
                              version) from err

    @classmethod
    def read(cls):
        """Read version data from a project"""
        return True

    @classmethod
    def write(cls):
        """Write version data to a project"""

    def bump(self,
             bump=None,
             prerelease=False,
             prerelease_prefix=None,
             build_date=None):
        """Bump version"""

        original = self._version

        if not bump:
            return False

        if bump == 'patch':
            bump_method = self._version.next_patch
        elif bump == 'minor':
            bump_method = self._version.next_minor
        elif bump == 'major':
            bump_method = self._version.next_major
        else:
            raise AvakasError("Invalid version component")

        self._version = bump_method()

        if prerelease:
            prerelease_version = self._get_prerelease_version(
                original, prefix=prerelease_prefix
            )

            self.apply_prerelease(prerelease_version,
                                  prefix=prerelease_prefix,
                                  build_date=build_date)

        assert self._version != original

        return True

    def _get_prerelease_version(self, starting_version, prefix,
                                new_version=None):
        """
        Return an integer representing the version of a given prerelase label
        (i.e. alpha, beta, rc) which comes next
        """

        if new_version is None:
            new_version = self._version

        # This \/ checks whether last version was a pre-release, and then
        # whether the beginning (at minimum) of the current pre-release
        # prefix (PRP) matches the intended PRP. This could resolve to
        # being `True` in the case that we're doing some sort of pre-pre
        # release, e.g. rc.1.dev.1 would match an attempted 'rc' bump), but
        # that's actually desirable (because bumping to the next 'rc'
        # should treat `dev.1` as if it doesn't exist.
        prerelease_len = 0
        if not prefix:
            prefix = tuple()
        if isinstance(prefix, str):
            prefix = (prefix, )

        prerelease_len = len(prefix)

        current_prefix_match = starting_version.prerelease[:prerelease_len]

        if (new_version == starting_version.truncate() and
                prefix == current_prefix_match):

            # prerelease bumping for the same release.
            # this will catch a case where there's e.g. rc.dev.1
            # and we're trying to bump the 'rc' prefix, in that
            # case per semver, there is an implicit zero (i.e. .alpha comes
            # before .alpha.1).
            try:
                prerelease_version = int(
                    starting_version.prerelease[prerelease_len])

            except (IndexError, TypeError):
                # either there is no explicit prerelease version in the
                # current version, or there are additional prerelease
                # prefixes which are not intended for this bump
                prerelease_version = 0
        else:
            # different release or different prefix
            prerelease_version = 0

        prerelease_version += 1

        return prerelease_version

    def make_prerelease(self, prefix=None, build_date=None):
        """Make current version a prerelease"""

        release_pos = 1 if prefix else 0
        if self._version.prerelease:
            release = self._version.prerelease[release_pos]
        else:
            release = 1

        self.apply_prerelease((str(release)),
                              prefix=prefix,
                              build_date=build_date)

    def apply_metadata(self, *metadata):
        """Apply build metadata to project version"""
        self._version.build += metadata

    def apply_prerelease(self, *prebuild, prefix=None, build_date=None):
        """Apply prebuild data to project version"""
        if prefix:
            self._version.prerelease = (prefix,)

        self._version.prerelease += tuple(str(element) for element in prebuild)

        if build_date is not None and build_date:

            self._version.prerelease += (build_date,)


def register_flavor(flavor):
    """
    Registers a Avakas Project Flavor
    Used for future language/project expansions
    """
    def wrapper(project):
        Avakas.project_flavors[flavor] = project
        return project
    return wrapper
