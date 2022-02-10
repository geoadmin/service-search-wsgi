import logging

from werkzeug.exceptions import BadRequest

from app.helpers.db import get_topics
from app.helpers.helpers_search import float_raise_nan
from app.helpers.helpers_search import ilen
from app.helpers.helpers_search import shift_to

SUPPORTED_OUTPUT_SRS = (21781, 2056, 3857, 4326)

MAX_SPHINX_INDEX_LENGTH = 63
MAX_SEARCH_TERMS = 10

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class MapNameValidation(object):  # pylint: disable=too-few-public-methods

    @staticmethod
    def has_topic(topic_name):
        topics = get_topics()
        if topic_name not in topics:
            raise BadRequest(f'The map ({topic_name}) you provided does not exist')


class SearchValidation(MapNameValidation):  # pylint: disable=too-many-instance-attributes

    def __init__(self, request):
        super().__init__()
        self.request = request
        self.availableLangs = ['de', 'fr', 'it', 'rm', 'en']
        self.locationTypes = ['locations']
        self.layerTypes = ['layers']
        self.featureTypes = ['featuresearch']
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
            self._timeEnabled = list(
                map(lambda val: val.lower() in ['true', 't', '1'], value.split(','))
            )

    @searchText.setter
    def searchText(self, value):
        isSearchTextRequired = not bool(
            self.bbox is not None and bool(set(self.locationTypes) & set([self.typeInfo]))
        )
        if (value is None or value.strip() == '') and isSearchTextRequired:
            logger.warning("Please provide a search text")
            raise BadRequest("Please provide a search text")
        searchTextList = value.split(' ')
        # Remove empty strings
        # Python2/3
        searchTextList = list(filter(None, searchTextList))
        if ilen(searchTextList) > MAX_SEARCH_TERMS:
            msg = "The searchText parameter can not contain more than 10 words"
            logger.warning(msg)
            raise BadRequest(msg)
        self._searchText = searchTextList

    @bbox.setter
    def bbox(self, value):
        if value is not None and value != '':
            values = value.split(',')
            if len(values) != 4:
                msg = f"Please provide 4 coordinates in a comma separated list and not {value}"
                logger.warning(msg)
                raise BadRequest(msg)
            try:
                # Python 2/3
                values = list(map(float_raise_nan, values))
            except ValueError as e:
                msg = f"Please provide numerical values for the parameter bbox and not {value}"
                logger.error("%s, %s", msg, e)
                raise BadRequest(msg) from e
            if self._srid == 2056:
                values = shift_to(values, 21781)
            # Swiss extent
            if values[0] >= 420000 and values[1] >= 30000:
                if values[0] < values[1]:
                    msg = "The first coordinate must be higher than the second"
                    logger.warning(msg)
                    raise BadRequest(msg)
            if values[2] >= 420000 and values[3] >= 30000:
                if values[2] < values[3]:
                    msg = "The third coordinate must be higher than the fourth"
                    logger.warning(msg)
                    raise BadRequest(msg)
            self._bbox = values

    @timeInstant.setter
    def timeInstant(self, value):
        if value is not None:
            if len(value) != 4:
                logger.warning(
                    "Only years are supported as timeInstant paramtere and not %s", value
                )
                raise BadRequest(
                    "Only years are supported as timeInstant parameter"
                    f" and not {value}"
                )
            if value.isdigit():
                self._timeInstant = int(value)
            else:
                logger.warning(
                    "Please provide an integer for the parameter timeInstant and not %s", value
                )
                raise BadRequest(
                    "Please provide an integer for the parameter timeInstant"
                    f" and not {value}"
                )
        else:
            self._timeInstant = value

    @timeStamps.setter
    def timeStamps(self, value):
        if value is not None and value != '':
            values = value.split(',')
            result = []
            for val in values:
                if len(val) != 4 and len(val) != 0:
                    logger.warning(
                        "Only years (4 digits) or empty strings are supported in " \
                            "timeStamps parameter"
                    )
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
                        logger.warning(
                            "Please provide integers for timeStamp parameter and not %s", value
                        )
                        raise BadRequest(
                            "Please provide integers for timeStamps parameter"
                            f" and not {value}"
                        )
            self._timeStamps = result

    @srid.setter
    def srid(self, value):
        if value in map(str, SUPPORTED_OUTPUT_SRS):
            self._srid = int(value)
        elif value is not None:
            logger.warning("Unsupported spatial reference %s", value)
            raise BadRequest(f"Unsupported spatial reference {value}")

    @returnGeometry.setter
    def returnGeometry(self, value):
        if value is False or value == 'false':
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
                logger.warning("The limit parameter should be an integer")
                raise BadRequest('The limit parameter should be an integer')

    @searchLang.setter
    def searchLang(self, value):
        if value == 'en':
            value = 'de'
        if value is not None and value not in self.availableLangs:
            logger.warning("Unsupported lang filter %s", value)
            raise BadRequest(f"Unsupported lang filter {value}")
        self._searchLang = value
