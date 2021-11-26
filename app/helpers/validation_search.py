import logging

from werkzeug.exceptions import BadRequest

from app.helpers.helpers_search import float_raise_nan
from app.helpers.helpers_search import ilen
from app.helpers.helpers_search import shift_to

SUPPORTED_OUTPUT_SRS = (21781, 2056, 3857, 4326)

MAX_SPHINX_INDEX_LENGTH = 63
MAX_SEARCH_TERMS = 10

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class MapNameValidation(object):  # pylint: disable=too-few-public-methods

    def has_topic(self, db, topic_name):  # pylint: disable=no-self-use,unused-argument
        # DOTO - db connection and Topics Model here
        # availableMaps = [q[0] for q in db.query(Topics.id)]
        # availableMaps.append(u'all')
        availableMaps = ['swisstopo', 'all', 'schnee']

        if topic_name not in availableMaps:
            raise BadRequest('The map you provided does not exist')
        #if db or mapName:
        #    pass


class BaseValidation(MapNameValidation):  # pylint: disable=too-few-public-methods

    def __init__(self, request):
        super().__init__()

        self.mapName = request.matchdict.get('map')
        self.has_topic(request.db, self.mapName)
        self.geodataStaging = request.registry.settings['geodata_staging']
        self.cbName = request.params.get('callback')
        self.request = request
        self.lang = request.lang
        self.translate = request.translate


class SearchValidation(MapNameValidation):  # pylint: disable=too-many-instance-attributes

    def __init__(self, request):
        super().__init__()
        # DOTO remove this hack
        #self.availableLangs = request.registry.settings['available_languages'].split(' ')
        self.not_used_at_all_doto_delete = request
        self.availableLangs = ['de', 'fr', 'it', 'rm', 'en']
        self.locationTypes = [u'locations']
        self.layerTypes = [u'layers']
        self.featureTypes = [u'featuresearch']
        self.supportedTypes = self.locationTypes + self.layerTypes + self.featureTypes

        self._searchText = None
        self._featureIndexes = None
        self._timeInstant = None
        self._timeEnabled = None
        self._timeStamps = None
        self._srid = None
        self._bbox = None
        self._returnGeometry = None
        self._origins = None
        self._typeInfo = None
        self._limit = None
        self._searchLang = None

    @property
    def searchText(self):
        return self._searchText

    @property
    def featureIndexes(self):
        return self._featureIndexes

    @property
    def timeEnabled(self):
        return self._timeEnabled

    @property
    def bbox(self):
        return self._bbox

    @property
    def timeInstant(self):
        return self._timeInstant

    @property
    def timeStamps(self):
        return self._timeStamps

    @property
    def srid(self):
        return self._srid

    @property
    def returnGeometry(self):
        return self._returnGeometry

    @property
    def origins(self):
        return self._origins

    @property
    def typeInfo(self):
        return self._typeInfo

    @property
    def limit(self):
        return self._limit

    @property
    def searchLang(self):
        return self._searchLang

    @featureIndexes.setter
    def featureIndexes(self, value):
        if value is not None and value != '':
            value = value.replace('.', '_').replace('-', '_')
            self._featureIndexes = [idx[:MAX_SPHINX_INDEX_LENGTH] for idx in value.split(',')]

    @timeEnabled.setter
    def timeEnabled(self, value):
        if value is not None and value != '':
            values = value.split(',')
            result = []
            for val in values:
                result.append(val.lower() in [u'true', u't', u'1'])
            self._timeEnabled = result

    @searchText.setter
    def searchText(self, value):
        isSearchTextRequired = not bool(
            self.bbox is not None and bool(set(self.locationTypes) & set([self.typeInfo]))
        )
        if (value is None or value.strip() == '') and isSearchTextRequired:
            raise BadRequest("Please provide a search text")
        searchTextList = value.split(' ')
        # Remove empty strings
        # Python2/3
        searchTextList = list(filter(None, searchTextList))
        if ilen(searchTextList) > MAX_SEARCH_TERMS:
            raise BadRequest("The searchText parameter can not contain more than 10 words")
        self._searchText = searchTextList

    @bbox.setter
    def bbox(self, value):
        if value is not None and value != '':
            values = value.split(',')
            if len(values) != 4:
                raise BadRequest("Please provide 4 coordinates in a comma separated list")
            try:
                # Python 2/3
                values = list(map(float_raise_nan, values))
            except ValueError as e:
                raise e from BadRequest("Please provide numerical values for the parameter bbox")
            if self._srid == 2056:
                values = shift_to(values, 21781)
            # Swiss extent
            if values[0] >= 420000 and values[1] >= 30000:
                if values[0] < values[1]:
                    raise BadRequest("The first coordinate must be higher than the second")
            if values[2] >= 420000 and values[3] >= 30000:
                if values[2] < values[3]:
                    raise BadRequest("The third coordinate must be higher than the fourth")
            self._bbox = values

    @timeInstant.setter
    def timeInstant(self, value):
        if value is not None:
            if len(value) != 4:
                raise BadRequest('Only years are supported as timeInstant parameter')
            if value.isdigit():
                self._timeInstant = int(value)
            else:
                raise BadRequest('Please provide an integer for the parameter timeInstant')
        else:
            self._timeInstant = value

    @timeStamps.setter
    def timeStamps(self, value):
        if value is not None and value != '':
            values = value.split(',')
            result = []
            for val in values:
                if len(val) != 4 and len(val) != 0:
                    raise BadRequest(
                        'Only years (4 digits) or empty strings are'
                        ' supported in timeStamps parameter'
                    )
                if len(val) == 0:
                    result.append(None)
                else:
                    if val.isdigit():
                        result.append(int(val))
                    else:
                        raise BadRequest('Please provide integers for timeStamps parameter')
            self._timeStamps = result

    @srid.setter
    def srid(self, value):
        if value in map(str, SUPPORTED_OUTPUT_SRS):
            self._srid = int(value)
        elif value is not None:
            raise BadRequest(f'Unsupported spatial reference {value}')

    @returnGeometry.setter
    def returnGeometry(self, value):
        if value is False or value == u'false':
            self._returnGeometry = False
        else:
            self._returnGeometry = True

    @origins.setter
    def origins(self, value):
        if value is not None:
            self._origins = value.split(',')

    @typeInfo.setter
    def typeInfo(self, value):
        if value is None:
            raise BadRequest(
                "Please provide a type parameter. Possible values are"
                f" {', '.join(self.supportedTypes)}"
            )
        if value not in self.supportedTypes:
            raise BadRequest(
                "The type parameter you provided is not valid. Possible values are"
                f" {', '.join(self.supportedTypes)}"
            )
        self._typeInfo = value

    @limit.setter
    def limit(self, value):
        if value is not None:
            if value.isdigit():
                self._limit = int(value)
            else:
                raise BadRequest('The limit parameter should be an integer')

    @searchLang.setter
    def searchLang(self, value):
        if value == 'en':
            value = 'de'
        if value is not None and value not in self.availableLangs:
            raise BadRequest(f'Usupported lang filter {value}')
        self._searchLang = value
